"""Trace probes for the AgentDefect extension.

The prelude text runs inside each child process. Each wrapper is installed on
the concrete class a configuration reaches, writes one JSON line per event and
returns the wrapped method's result unchanged.
"""

from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path

# Plan Appendix A.7. Each boundary maps to (class path, method) pairs.
BOUNDARY_CLASSES = {
    "chat_request": [("StudyChat", "_get_request_payload")],
    "network_attempt": [("httpx.Client", "send")],
    "memory": [
        ("langchain.memory.ConversationBufferMemory", "load_memory_variables"),
        ("langchain.memory.ConversationBufferMemory", "save_context"),
    ],
    "retrieval": [("langchain_core.vectorstores.VectorStoreRetriever", "_get_relevant_documents")],
    "direct_search": [("langchain_community.vectorstores.Chroma", "similarity_search")],
    "embeddings": [
        ("langchain_openai.OpenAIEmbeddings", "embed_documents"),
        ("langchain_openai.OpenAIEmbeddings", "embed_query"),
        ("langchain_community.embeddings.OpenAIEmbeddings", "embed_documents"),
        ("langchain_community.embeddings.OpenAIEmbeddings", "embed_query"),
    ],
    "parsers": [
        ("langchain_core.output_parsers.StrOutputParser", "invoke"),
        ("langchain_core.output_parsers.StrOutputParser", "parse"),
        ("langchain.output_parsers.StructuredOutputParser", "invoke"),
        ("langchain.output_parsers.StructuredOutputParser", "parse"),
    ],
    "agent_parsers": [
        ("langchain.agents.chat.output_parser.ChatOutputParser", "parse"),
        ("langchain.agents.conversational_chat.output_parser.ConvoOutputParser", "parse"),
    ],
    "tools": [("callback_handler", "on_tool_start"), ("callback_handler", "on_tool_end")],
    "loader": [("load_excel_response", "func")],
}

MODEL_PATHS = ("/chat/completions", "/embeddings", "/responses")

NO_RETRY_PRELUDE = r'''
import importlib as _mp_nr_importlib
_mp_nr_study_init = StudyChat.__init__
def _mp_nr_init(self, *args, **kwargs):
    kwargs["max_retries"] = 0
    _mp_nr_study_init(self, *args, **kwargs)
StudyChat.__init__ = _mp_nr_init
def _mp_nr_patch(path):
    module, name = path.rsplit(".", 1)
    cls = getattr(_mp_nr_importlib.import_module(module), name)
    original = cls.__init__
    def init(self, *args, **kwargs):
        kwargs["max_retries"] = 0
        original(self, *args, **kwargs)
    cls.__init__ = init
for _mp_nr_path in ("langchain_openai.OpenAIEmbeddings", "langchain_community.embeddings.OpenAIEmbeddings"):
    _mp_nr_patch(_mp_nr_path)
'''

NO_PROBE_PRELUDE = r'''
_MP_STATE = {"seq": 0, "phase": "prelude", "last_boundary": None}
def _mp_emit(kind, **fields):
    pass
def _mp_phase(name):
    _MP_STATE["phase"] = name
'''

TRACE_PRELUDE = r'''
import json as _mp_json, time as _mp_time, importlib as _mp_importlib, contextvars as _mp_cv
_MP_TRACE = __TRACE_PATH__
_MP_WANTED = __BOUNDARIES__
_MP_STATE = {"seq": 0, "phase": "prelude", "last_boundary": None}
_MP_LIMIT = 20000

def _mp_safe(value, depth=0):
    try:
        if depth > 6:
            return repr(value)[:_MP_LIMIT]
        if value is None or isinstance(value, (bool, int, float)):
            return value
        if isinstance(value, str):
            return value[:_MP_LIMIT]
        if isinstance(value, bytes):
            return value[:400].decode("utf-8", "replace")
        if isinstance(value, dict):
            return {str(key): _mp_safe(item, depth + 1) for key, item in list(value.items())[:300]}
        if isinstance(value, (list, tuple, set)):
            return [_mp_safe(item, depth + 1) for item in list(value)[:500]]
        if hasattr(value, "page_content"):
            return {"page_content": _mp_safe(value.page_content, depth + 1), "metadata": _mp_safe(getattr(value, "metadata", {}), depth + 1)}
        if hasattr(value, "content") and hasattr(value, "type"):
            out = {"type": value.type, "content": _mp_safe(value.content, depth + 1)}
            for key in ("additional_kwargs", "tool_calls", "tool_call_id", "name"):
                if getattr(value, key, None):
                    out[key] = _mp_safe(getattr(value, key), depth + 1)
            return out
        if hasattr(value, "columns") and hasattr(value, "shape"):
            return {"columns": [str(column) for column in value.columns], "shape": list(value.shape)}
        return repr(value)[:_MP_LIMIT]
    except Exception as exc:
        return "<unserializable " + type(exc).__name__ + ">"

def _mp_emit(kind, **fields):
    try:
        _MP_STATE["seq"] += 1
        row = {"seq": _MP_STATE["seq"], "t": _mp_time.time(), "phase": _MP_STATE["phase"], "kind": kind}
        row.update(fields)
        with open(_MP_TRACE, "a", encoding="utf-8") as handle:
            handle.write(_mp_json.dumps(row, default=str) + "\n")
    except Exception:
        pass

def _mp_phase(name):
    _MP_STATE["phase"] = name
    _mp_emit("phase", name=name)

def _mp_boundary(boundary, kind, **fields):
    _MP_STATE["last_boundary"] = boundary
    _mp_emit(kind, boundary=boundary, **fields)

def _mp_probe_error(where, exc):
    _mp_emit("probe_error", where=where, error_type=type(exc).__name__, message=str(exc)[:500])

def _mp_class(path):
    if path == "StudyChat":
        return StudyChat
    module, name = path.rsplit(".", 1)
    return getattr(_mp_importlib.import_module(module), name)

def _mp_install(boundary, path, method, after, on_error):
    try:
        cls = _mp_class(path)
    except Exception as exc:
        _mp_emit("probe_unresolved", boundary=boundary, cls=path, method=method, error=(type(exc).__name__ + ": " + str(exc))[:300])
        return
    owner = next((klass for klass in cls.__mro__ if method in klass.__dict__), None)
    if owner is None:
        _mp_emit("probe_unresolved", boundary=boundary, cls=path, method=method, error="method not found in the MRO")
        return
    original = owner.__dict__[method]
    def wrapper(self, *args, **kwargs):
        try:
            result = original(self, *args, **kwargs)
        except BaseException as exc:
            try:
                if on_error is not None:
                    on_error(self, args, kwargs, exc)
                else:
                    _mp_boundary(boundary, "boundary_error", method=method, error_type=type(exc).__name__, message=str(exc)[:1000])
            except Exception as probe_exc:
                _mp_probe_error(boundary + "." + method, probe_exc)
            raise
        try:
            after(self, args, kwargs, result)
        except Exception as probe_exc:
            _mp_probe_error(boundary + "." + method, probe_exc)
        return result
    wrapper.__wrapped__ = original
    try:
        setattr(cls, method, wrapper)
    except Exception as exc:
        _mp_emit("probe_unresolved", boundary=boundary, cls=path, method=method, error=("setattr " + type(exc).__name__ + ": " + str(exc))[:300])
        return
    _mp_emit("probe_installed", boundary=boundary, cls=cls.__module__ + "." + cls.__qualname__, method=method,
             resolved_from=owner.__module__ + "." + owner.__qualname__)

def _mp_arg(args, kwargs, index, *names):
    if len(args) > index:
        return args[index]
    for name in names:
        if name in kwargs:
            return kwargs[name]
    return None

def _mp_request_line(request):
    url = getattr(request, "url", None)
    return {"method": getattr(request, "method", None), "host": getattr(url, "host", None), "path": getattr(url, "path", None)}

def _mp_after_request(self, args, kwargs, result):
    model = result.get("model") if isinstance(result, dict) else None
    _mp_boundary("chat_request", "request_prepared", model=model, payload=_mp_safe(result))

def _mp_after_send(self, args, kwargs, result):
    _mp_boundary("network_attempt", "backend_attempt", status=getattr(result, "status_code", None),
                 **_mp_request_line(_mp_arg(args, kwargs, 0, "request")))

def _mp_error_send(self, args, kwargs, exc):
    _mp_boundary("network_attempt", "backend_attempt", error_type=type(exc).__name__, message=str(exc)[:300],
                 **_mp_request_line(_mp_arg(args, kwargs, 0, "request")))

def _mp_after_load(self, args, kwargs, result):
    _mp_boundary("memory", "memory_before", cls=type(self).__name__,
                 value_types={str(key): type(item).__name__ for key, item in (result or {}).items()}, value=_mp_safe(result))

def _mp_after_save(self, args, kwargs, result):
    chat = getattr(self, "chat_memory", None)
    _mp_boundary("memory", "memory_after", cls=type(self).__name__, inputs=_mp_safe(_mp_arg(args, kwargs, 0, "inputs")),
                 outputs=_mp_safe(_mp_arg(args, kwargs, 1, "outputs")), messages=_mp_safe(getattr(chat, "messages", None)))

def _mp_after_retrieve(self, args, kwargs, result):
    _mp_boundary("retrieval", "retrieval", query=_mp_safe(_mp_arg(args, kwargs, 0, "query")), search_type=getattr(self, "search_type", None),
                 search_kwargs=_mp_safe(getattr(self, "search_kwargs", None)), documents=_mp_safe(result))

def _mp_after_search(self, args, kwargs, result):
    _mp_boundary("direct_search", "retrieval", query=_mp_safe(_mp_arg(args, kwargs, 0, "query")),
                 k=_mp_safe(_mp_arg(args, kwargs, 1, "k")), documents=_mp_safe(result))

def _mp_embed_hook(method):
    def hook(self, args, kwargs, result):
        texts = _mp_arg(args, kwargs, 0, "texts", "text")
        if isinstance(texts, str):
            texts = [texts]
        texts = list(texts or [])
        _mp_boundary("embeddings", "embedding", cls=type(self).__module__ + "." + type(self).__name__, method=method,
                     count=len(texts), characters=sum(len(str(text)) for text in texts))
    return hook

def _mp_parser_hook(boundary, method):
    def hook(self, args, kwargs, result):
        _mp_boundary(boundary, "parser", cls=type(self).__name__, method=method,
                     input=_mp_safe(_mp_arg(args, kwargs, 0, "input", "text")), output=_mp_safe(result))
    return hook

_MP_SPEC = {
    "chat_request": [("StudyChat", "_get_request_payload", _mp_after_request, None)],
    "network_attempt": [("httpx.Client", "send", _mp_after_send, _mp_error_send)],
    "memory": [
        ("langchain.memory.ConversationBufferMemory", "load_memory_variables", _mp_after_load, None),
        ("langchain.memory.ConversationBufferMemory", "save_context", _mp_after_save, None),
    ],
    "retrieval": [("langchain_core.vectorstores.VectorStoreRetriever", "_get_relevant_documents", _mp_after_retrieve, None)],
    "direct_search": [("langchain_community.vectorstores.Chroma", "similarity_search", _mp_after_search, None)],
    "embeddings": [(path, method, _mp_embed_hook(method), None)
                   for path in ("langchain_openai.OpenAIEmbeddings", "langchain_community.embeddings.OpenAIEmbeddings")
                   for method in ("embed_documents", "embed_query")],
    "parsers": [(path, method, _mp_parser_hook("parsers", method), None)
                for path in ("langchain_core.output_parsers.StrOutputParser", "langchain.output_parsers.StructuredOutputParser")
                for method in ("invoke", "parse")],
    "agent_parsers": [(path, "parse", _mp_parser_hook("agent_parsers", "parse"), None)
                      for path in ("langchain.agents.chat.output_parser.ChatOutputParser",
                                   "langchain.agents.conversational_chat.output_parser.ConvoOutputParser")],
}

for _mp_name in _MP_WANTED:
    for _mp_path, _mp_method, _mp_after, _mp_on_error in _MP_SPEC.get(_mp_name, []):
        _mp_install(_mp_name, _mp_path, _mp_method, _mp_after, _mp_on_error)

if "tools" in _MP_WANTED:
    try:
        from langchain_core.callbacks import BaseCallbackHandler as _MPBase
        from langchain_core.tracers.context import register_configure_hook as _mp_register

        class _MPHandler(_MPBase):
            def on_tool_start(self, serialized, input_str, **kwargs):
                _mp_boundary("tools", "tool_call", stage="start", name=(serialized or {}).get("name"), input=_mp_safe(input_str))

            def on_tool_end(self, output, **kwargs):
                _mp_boundary("tools", "tool_call", stage="end", output=_mp_safe(output))

            def on_tool_error(self, error, **kwargs):
                _mp_boundary("tools", "boundary_error", method="tool", error_type=type(error).__name__, message=str(error)[:1000])

        _MP_HANDLER_VAR = _mp_cv.ContextVar("mp_tool_handler", default=None)
        _mp_register(_MP_HANDLER_VAR, True)
        _MP_HANDLER_VAR.set(_MPHandler())
        _mp_emit("probe_installed", boundary="tools", cls="callback_handler", method="on_tool_start", resolved_from="register_configure_hook")
    except Exception as _mp_exc:
        _mp_emit("probe_unresolved", boundary="tools", cls="callback_handler", method="on_tool_start", error=str(_mp_exc)[:300])
'''

CHILD_TEMPLATE = r'''
import json, sys, traceback, hashlib
_MP_PRELUDE = __PRELUDE__

def _mp_out(payload):
    sys.stdout.write("\n" + json.dumps(payload, default=str) + "\n")
    sys.stdout.flush()

def _mp_fail(phase, exc, code, extra=None):
    state = globals().get("_MP_STATE") or {}
    info = {
        "ok": False,
        "mp_failed_phase": phase,
        "error_type": type(exc).__name__,
        "error_mro": [klass.__name__ for klass in type(exc).__mro__],
        "error_module": type(exc).__module__,
        "error_message": str(exc)[:2000],
        "missing_module": getattr(exc, "name", None) if isinstance(exc, ImportError) else None,
        "last_boundary": state.get("last_boundary"),
        "loaded_sha256": globals().get("loaded_sha256"),
    }
    info.update(extra or {})
    try:
        globals()["_mp_emit"]("exception", failed_phase=phase, error_type=info["error_type"],
                              message=info["error_message"][:1000], last_boundary=info["last_boundary"])
    except Exception:
        pass
    traceback.print_exc()
    _mp_out(info)
    sys.exit(code)

try:
    exec(compile(_MP_PRELUDE, "<mp_prelude>", "exec"), globals())
except BaseException as exc:
    _mp_fail("prelude", exc, 10)

mode = sys.argv[1]
turns = json.loads(sys.argv[2])
_mp_phase("import")
loaded_sha256 = hashlib.sha256(open("run_buggy.py", "rb").read()).hexdigest()
_mp_emit("module_loaded", path="run_buggy.py", sha256=loaded_sha256)
try:
    import run_buggy as module
except BaseException as exc:
    _mp_fail("import", exc, 11)
_mp_emit("module_imported", file=getattr(module, "__file__", None))

if mode == "loader":
    _mp_phase("turn_1")
    try:
        tool = module.load_excel_response
        fn = tool.func if hasattr(tool, "func") else tool
        frame = fn(turns[0])
    except BaseException as exc:
        _mp_fail("turn_1", exc, 12)
    _mp_phase("flatten")
    try:
        def _column(name):
            if name not in frame.columns:
                return []
            return ["" if value != value else str(value) for value in frame[name]]
        loader = {
            "columns": [str(column) for column in frame.columns],
            "rows": int(len(frame)),
            "dtypes": {str(column): str(kind) for column, kind in frame.dtypes.items()},
            "sentiment": _column("Sentiment"),
            "location": _column("Location"),
        }
    except BaseException as exc:
        _mp_fail("flatten", exc, 13)
    _mp_emit("loader_output", boundary="loader", **loader)
    _mp_phase("emit")
    _mp_out({"ok": True, "loaded_sha256": loaded_sha256, "loader": loader, "results": [],
             "prompt": 0, "completion": 0, "chat_requests": 0})
    sys.exit(0)

from langchain_community.callbacks import get_openai_callback
results = []
with get_openai_callback() as cb:
    for index, text in enumerate(turns, 1):
        _mp_phase("turn_" + str(index))
        try:
            result = module.run_agent(text)
        except BaseException as exc:
            _mp_fail("turn_" + str(index), exc, 12, {"prompt": cb.prompt_tokens, "completion": cb.completion_tokens,
                                                     "chat_requests": cb.successful_requests, "results": results})
        _mp_phase("flatten")
        try:
            if isinstance(result, list):
                answer = "\n".join(getattr(item, "page_content", str(item)) for item in result)
                count = len(result)
            elif isinstance(result, dict):
                answer = str(result.get("answer") or result.get("output") or result)
                count = None
            else:
                answer = str(result)
                count = None
        except BaseException as exc:
            _mp_fail("flatten", exc, 13)
        _mp_emit("final", turn=index, answer=answer[:20000], python_type=type(result).__name__, count=count)
        results.append({"turn": index, "text": answer, "count": count, "type": type(result).__name__})
_mp_phase("emit")
_mp_out({"ok": True, "loaded_sha256": loaded_sha256, "results": results, "prompt": cb.prompt_tokens,
         "completion": cb.completion_tokens, "chat_requests": cb.successful_requests})
'''


def trace_prelude(path: Path | str, boundaries: list[str]) -> str:
    return (TRACE_PRELUDE
            .replace("__TRACE_PATH__", repr(str(path)))
            .replace("__BOUNDARIES__", repr(list(boundaries))))


def child_script(prelude: str) -> str:
    return CHILD_TEMPLATE.replace("__PRELUDE__", repr(prelude))


def last_json(stdout: str) -> dict | None:
    for line in reversed((stdout or "").splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                return value
    return None


def tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in Path(root).rglob("*") if p.is_file()):
        digest.update(str(path.relative_to(root)).encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def resolve(class_path: str, method: str) -> str | None:
    """The class that defines `method` for `class_path`, found through the MRO."""
    module, name = class_path.rsplit(".", 1)
    cls = getattr(importlib.import_module(module), name)
    owner = next((klass for klass in cls.__mro__ if method in klass.__dict__), None)
    return None if owner is None else f"{owner.__module__}.{owner.__qualname__}"


def read_trace(path: Path) -> list[dict]:
    if not Path(path).exists():
        return []
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def derive(events: list[dict]) -> dict:
    """Intermediate-state fields read from one run's trace."""
    attempts = [e for e in events if e["kind"] == "backend_attempt"]
    model_attempts = [e for e in attempts if (e.get("path") or "").endswith(MODEL_PATHS)]
    requests = [e for e in events if e["kind"] == "request_prepared"]
    exceptions = [e for e in events if e["kind"] == "exception"]
    return {
        "requests_prepared": len(requests),
        "backend_attempts": len(model_attempts),
        "chat_attempts": sum(1 for e in model_attempts if e["path"].endswith("/chat/completions")),
        "embedding_attempts": sum(1 for e in model_attempts if e["path"].endswith("/embeddings")),
        "failed_attempts": sum(1 for e in model_attempts if e.get("error_type") or (e.get("status") or 200) >= 400),
        "request_messages": [(e.get("payload") or {}).get("messages") for e in requests],
        "retrieved": [{"boundary": e["boundary"], "query": e.get("query"), "search_kwargs": e.get("search_kwargs"),
                       "documents": e.get("documents")} for e in events if e["kind"] == "retrieval"],
        "memory_before": [{"types": e.get("value_types"), "value": e.get("value")} for e in events if e["kind"] == "memory_before"],
        "memory_after": [e.get("messages") for e in events if e["kind"] == "memory_after"],
        "tool_calls": [{k: e.get(k) for k in ("stage", "name", "input", "output")} for e in events if e["kind"] == "tool_call"],
        "parser_io": [{k: e.get(k) for k in ("boundary", "cls", "method", "input", "output")} for e in events if e["kind"] == "parser"],
        "embeddings": [{k: e.get(k) for k in ("cls", "method", "count", "characters")} for e in events if e["kind"] == "embedding"],
        "loader_output": next((e for e in events if e["kind"] == "loader_output"), None),
        "finals": [{k: e.get(k) for k in ("turn", "answer", "python_type", "count")} for e in events if e["kind"] == "final"],
        "exception": exceptions[-1] if exceptions else None,
        "probe_errors": [e for e in events if e["kind"] == "probe_error"],
        "probe_unresolved": [e for e in events if e["kind"] == "probe_unresolved"],
        "probes_installed": [f"{e['boundary']}:{e['cls']}.{e['method']}" for e in events if e["kind"] == "probe_installed"],
    }


def boundary_states(events: list[dict], spec: dict) -> dict:
    """Observed, not reached, removed or rerouted, or probe unavailable, per boundary."""
    seen = {e.get("boundary") for e in events
            if e.get("boundary") and e["kind"] not in ("probe_installed", "probe_unresolved", "probe_error")}
    exception = next((e for e in reversed(events) if e["kind"] == "exception"), None)
    order = spec.get("order", [])
    stop = None
    if exception is not None:
        last = exception.get("last_boundary")
        stop = order.index(last) if last in order else -1
    states = {}
    for boundary in spec.get("removed", []):
        states[boundary] = "observed" if boundary in seen else "removed_or_rerouted"
    for boundary in spec.get("expected", []):
        if boundary in seen:
            states[boundary] = "observed"
        elif stop is not None and (boundary not in order or order.index(boundary) > stop):
            states[boundary] = "not_reached"
        else:
            states[boundary] = "probe_unavailable"
    for boundary in spec.get("optional", []):
        if boundary in seen:
            states[boundary] = "observed"
    return states
