"""Relay between SelfHeal's OpenAI clients and the VT ARC endpoint.

SelfHeal's scripts name OpenAI models (`gpt-5.2`, `gpt-5-mini`, `o3-mini`). ARC serves other
names. The relay listens on 127.0.0.1 and receives each `/chat/completions` request. It replaces
the `model` field with the run's ARC model and asks ARC for a streamed reply, because ARC caps
replies that are not streamed at 8000 tokens. No length limit is set, so the reply length is
ARC's default maximum. The relay joins the streamed pieces into one ordinary chat completion
and returns it to SelfHeal's client, which asked for a reply that is not streamed. Every other
request field is forwarded unchanged.

One JSON line per call is appended to the log. It holds the request as the client sent it, the
model and stream setting sent to ARC, the HTTP status, the number of streamed pieces and the
joined reply. Request headers, which carry the key, are forwarded and never written to the log.
When the relay is stopped it first waits for every open call to finish and be logged.

When the AgentDefect programs run their tests, two more kinds of request arrive. An
`/embeddings` request goes to OpenAI with the key in --openai-key-file, unchanged. Its reply
is saved in --embed-store under the exact request body, and a later identical request gets
the saved reply. The log records whether each embedding reply was reused or called. Any other
request goes to ARC with only the model name replaced, and ARC's answer is returned as it is.

With --usage-counts-only, used for the program tests, the usage part of a joined chat reply is
returned with only prompt_tokens, completion_tokens and total_tokens. ARC's full reply is still
written to the log, and the usage returned is logged as usage_returned. Jun "yes", on dropping
the two detail fields that LangChain 0.0.245 cannot add up.

With --provider openrouter (Jun "let's try with open router for deep seek", then "Default routing"
and "2"), chat and other requests go to OpenRouter instead of ARC, under --provider-model, with the
key read from --provider-key-file. The client's Authorization header, which carries the ARC key, is
not forwarded. Nothing else changes: the request is streamed, no length limit, temperature or
reasoning setting is added, and OpenRouter's default routing picks the upstream provider. Each log
line then also holds provider "openrouter" and the upstream provider OpenRouter names in its stream.
Without --provider, or with --provider arc, the relay works exactly as described above.

Usage: python relay.py --model gpt-oss-120b --log relay_log.jsonl --port-file port.txt
       [--embed-store store.jsonl --openai-key-file institutional.sh] [--usage-counts-only]
       [--provider openrouter --provider-model deepseek/deepseek-v4.1-flash --provider-key-file openrouter.sh]
"""
import argparse
import hashlib
import json
import re
import signal
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ARC_BASE = "https://llm-api.arc.vt.edu/api/v1"
USAGE_COUNTS = ("prompt_tokens", "completion_tokens", "total_tokens")
OPENAI_BASE = "https://api.openai.com/v1"
OPENROUTER_BASE = "https://openrouter.ai/api/v1"


class StreamError(Exception):
    def __init__(self, payload):
        super().__init__(json.dumps(payload))
        self.payload = payload


def join_stream(resp, meta=None):
    """Join an OpenAI style event stream into one chat completion, as ARC returns it unstreamed.
    With meta, the upstream provider a chunk names (OpenRouter's "provider") is kept in meta for the log."""
    out, choices, usage, pieces = None, {}, None, 0
    for raw in resp:
        line = raw.decode("utf-8").strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        chunk = json.loads(data)
        pieces += 1
        if "error" in chunk:
            raise StreamError(chunk)
        if meta is not None and chunk.get("provider"):
            meta["upstream_provider"] = chunk["provider"]
        if out is None:
            out = {"id": chunk.get("id"), "object": "chat.completion", "created": chunk.get("created"),
                   "model": chunk.get("model")}
            if chunk.get("system_fingerprint") is not None:
                out["system_fingerprint"] = chunk["system_fingerprint"]
        if chunk.get("usage"):
            usage = chunk["usage"]
        for ch in chunk.get("choices") or []:
            i = ch.get("index", 0)
            acc = choices.setdefault(i, {"index": i, "message": {"role": "assistant", "content": None},
                                         "finish_reason": None})
            msg, delta = acc["message"], ch.get("delta") or {}
            if delta.get("role"):
                msg["role"] = delta["role"]
            for key in ("content", "reasoning", "reasoning_content"):
                if delta.get(key):
                    msg[key] = (msg.get(key) or "") + delta[key]
            for t in delta.get("tool_calls") or []:
                calls = msg.setdefault("tool_calls", [])
                j = t.get("index", len(calls))
                while len(calls) <= j:
                    calls.append({"id": None, "type": "function", "function": {"name": "", "arguments": ""}})
                call, fn = calls[j], t.get("function") or {}
                if t.get("id"):
                    call["id"] = t["id"]
                if t.get("type"):
                    call["type"] = t["type"]
                if fn.get("name"):
                    call["function"]["name"] += fn["name"]
                if fn.get("arguments"):
                    call["function"]["arguments"] += fn["arguments"]
            if ch.get("finish_reason"):
                acc["finish_reason"] = ch["finish_reason"]
            if ch.get("stop_reason") is not None:
                acc["stop_reason"] = ch["stop_reason"]
    out = out or {"object": "chat.completion"}
    out["choices"] = [choices[i] for i in sorted(choices)]
    if usage is not None:
        out["usage"] = usage
    return out, pieces


def make_handler(model, log_path, lock, open_calls, embed=None, usage_counts_only=False, route=None):
    # route is None for ARC. For OpenRouter it holds the base URL, the model name there and the key.
    base = route["base"] if route else ARC_BASE
    sent_model = route["model"] if route else model

    def auth(headers):
        return f"Bearer {route['key']}" if route else headers.get("Authorization", "")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _write_log(self, rec):
            with lock, open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        def _reply(self, rec, status, data, ctype):
            try:
                self.send_response(status)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):
                rec["client_gone"] = True  # the client stopped waiting before the reply was ready

        def do_POST(self):
            self._counted(self._post)

        def do_GET(self):
            self._counted(lambda: self._forward(time.time(), b"", "GET"))

        def _counted(self, fn):
            with open_calls["cond"]:
                open_calls["n"] += 1
            try:
                fn()
            finally:
                with open_calls["cond"]:
                    open_calls["n"] -= 1
                    open_calls["cond"].notify_all()

        def _arc_url(self):
            path = self.path[len("/v1"):] if self.path.startswith("/v1") else self.path
            return base + path

        def _forward(self, t0, raw, method):
            """Any request other than chat and embeddings: to ARC with only the model name replaced."""
            rec = {"t_start": t0, "path": self.path, "method": method}
            if route:
                rec["provider"] = route["name"]
            sent = raw or None
            try:
                body = json.loads(raw) if raw else None
            except ValueError:
                body = None
            if isinstance(body, dict):
                rec["request"] = body
                if "model" in body:
                    rec["client_model"] = body.get("model")
                    sent = json.dumps(dict(body, model=sent_model)).encode()
                    rec["sent_model"] = sent_model
            req = urllib.request.Request(self._arc_url(), data=sent, method=method, headers={
                "Content-Type": self.headers.get("Content-Type", "application/json"),
                "Authorization": auth(self.headers)})
            ctype = "application/json"
            try:
                resp = urllib.request.urlopen(req, timeout=900)
                status, data, ctype = resp.status, resp.read(), resp.headers.get("Content-Type", ctype)
            except urllib.error.HTTPError as e:
                status, data = e.code, e.read()
                ctype = e.headers.get("Content-Type", ctype)
            except Exception as e:
                status, data = 502, json.dumps({"error": repr(e)}).encode()
            rec.update(status=status, t_end=time.time(), response_text=data.decode("utf-8", "replace"))
            self._reply(rec, status, data, ctype)
            self._write_log(rec)

        def _embeddings(self, t0, raw):
            """An embedding request: the saved reply for this exact body, or a real OpenAI call."""
            body = json.loads(raw)
            key = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            inp = body.get("input")
            rec = {"t_start": t0, "path": self.path, "embed_model": body.get("model"), "embed_key_sha256": key,
                   "embed_inputs": len(inp) if isinstance(inp, list) else 1}
            with embed["lock"]:
                saved = embed["store"].get(key)
            if saved is not None:
                status, data, rec["embed_reused"] = 200, json.dumps(saved).encode(), True
            else:
                rec["embed_reused"] = False
                req = urllib.request.Request(OPENAI_BASE + "/embeddings", data=raw, method="POST", headers={
                    "Content-Type": "application/json", "Authorization": f"Bearer {embed['key']}"})
                try:
                    resp = urllib.request.urlopen(req, timeout=900)
                    status, data = resp.status, resp.read()
                    reply = json.loads(data)
                    with embed["lock"]:
                        embed["store"][key] = reply
                        with open(embed["path"], "a", encoding="utf-8") as f:
                            f.write(json.dumps({"key_sha256": key, "request": body, "response": reply},
                                               ensure_ascii=False) + "\n")
                except urllib.error.HTTPError as e:
                    status, data = e.code, e.read()
                    rec["response_text"] = data.decode("utf-8", "replace")
                except Exception as e:
                    status, data = 502, json.dumps({"error": repr(e)}).encode()
                    rec["response_text"] = data.decode("utf-8", "replace")
            rec.update(status=status, t_end=time.time())
            self._reply(rec, status, data, "application/json")
            self._write_log(rec)

        def _post(self):
            t0 = time.time()
            raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            path = self.path.split("?")[0].rstrip("/")
            if embed is not None and path.endswith("/embeddings"):
                return self._embeddings(t0, raw)
            if not path.endswith("/chat/completions"):
                return self._forward(t0, raw, "POST")
            rec = {"t_start": t0, "path": self.path}
            if route:
                rec["provider"] = route["name"]
            body = json.loads(raw)
            rec["request"] = body
            rec["client_model"] = body.get("model")
            client_stream = bool(body.get("stream"))
            sent = dict(body)
            sent["model"] = sent_model
            if not client_stream:
                sent["stream"] = True
                sent["stream_options"] = {"include_usage": True}  # usage, as in an unstreamed reply
            rec["sent_model"] = sent_model
            rec["sent_stream"] = True
            req = urllib.request.Request(
                base + "/chat/completions",
                data=json.dumps(sent).encode(),
                headers={"Content-Type": "application/json",
                         "Authorization": auth(self.headers)},
                method="POST",
            )
            ctype = "application/json"
            try:
                resp = urllib.request.urlopen(req, timeout=900)
                if client_stream:  # no SelfHeal client asks for this; the stream is passed through
                    status, data, ctype = resp.status, resp.read(), resp.headers.get("Content-Type", "text/event-stream")
                    rec["response_text"] = data.decode("utf-8", "replace")
                else:
                    meta = {} if route else None
                    joined, pieces = join_stream(resp, meta)
                    if meta:
                        rec.update(meta)
                    returned = joined
                    if usage_counts_only and isinstance(joined.get("usage"), dict):
                        returned = dict(joined, usage={k: joined["usage"][k] for k in USAGE_COUNTS
                                                       if k in joined["usage"]})
                        rec["usage_returned"] = returned["usage"]
                    status, data = resp.status, json.dumps(returned).encode()
                    rec["pieces"] = pieces
                    rec["response"] = joined
            except urllib.error.HTTPError as e:
                status, data = e.code, e.read()
                ctype = e.headers.get("Content-Type", "application/json")
            except StreamError as e:  # ARC reported an error inside the stream
                err = e.payload.get("error")
                code = err.get("code") if isinstance(err, dict) else None
                status, data = (code if isinstance(code, int) and code >= 400 else 500), json.dumps(e.payload).encode()
            except Exception as e:  # network failure: report it to the client as a 502
                status, data = 502, json.dumps({"error": repr(e)}).encode()
            rec["status"] = status
            rec["t_end"] = time.time()
            if "response" not in rec and "response_text" not in rec:
                try:
                    rec["response"] = json.loads(data)
                except ValueError:
                    rec["response_text"] = data.decode("utf-8", "replace")
            self._reply(rec, status, data, ctype)
            self._write_log(rec)

    return Handler


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--port-file", required=True)
    ap.add_argument("--embed-store")
    ap.add_argument("--openai-key-file")
    ap.add_argument("--usage-counts-only", action="store_true")
    ap.add_argument("--provider", choices=["arc", "openrouter"], default="arc")
    ap.add_argument("--provider-model")
    ap.add_argument("--provider-key-file")
    a = ap.parse_args()
    route = None
    if a.provider == "openrouter":
        m = re.search(r'OPENROUTER_API_KEY\s*=\s*["\']?([^"\'\s]+)', open(a.provider_key_file).read())
        if not m or not a.provider_model:
            raise SystemExit("OPENROUTER_API_KEY or --provider-model missing")
        route = {"name": "openrouter", "base": OPENROUTER_BASE, "model": a.provider_model, "key": m.group(1)}
    embed = None
    if a.embed_store:
        m = re.search(r'OPENAI_API_KEY\s*=\s*["\']?([^"\'\s]+)', open(a.openai_key_file).read())
        if not m:
            raise SystemExit("OPENAI_API_KEY not found in the key file")
        store = {}
        try:
            for line in open(a.embed_store, encoding="utf-8"):
                row = json.loads(line)
                store[row["key_sha256"]] = row["response"]
        except FileNotFoundError:
            pass
        embed = {"key": m.group(1), "store": store, "path": a.embed_store, "lock": threading.Lock()}
    open_calls = {"n": 0, "cond": threading.Condition()}
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(a.model, a.log, threading.Lock(), open_calls, embed,
                                                                   a.usage_counts_only, route))
    # On SIGTERM the relay stops taking new calls, then waits until every open call has its
    # reply from ARC and is written to the log, even when the client has stopped waiting.
    signal.signal(signal.SIGTERM, lambda *_: threading.Thread(target=server.shutdown, daemon=True).start())
    with open(a.port_file, "w") as f:
        f.write(str(server.server_address[1]))
    server.serve_forever()
    with open_calls["cond"]:
        open_calls["cond"].wait_for(lambda: open_calls["n"] == 0)


if __name__ == "__main__":
    main()
