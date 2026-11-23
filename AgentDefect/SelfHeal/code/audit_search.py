"""Search leakage audit (fix plan departure 9, Jun "4 Audits"), both datasets.

SelfHeal's search tools return each result as its title and snippet, without its link
(run_agent.py, _web_search_impl). This audit reads every web_search and verify_api_usage result the
model received in every SelfHeal relay log and flags results that may carry the case's own answer:
  AgentDefect       a result title close to the case's Stack Overflow or HuggingFace post title, or
                    holding the post id
  AgentIssue-Bench  a result naming the issue's repository together with its issue number, a result
                    title close to the issue title, or a result naming the repository together with
                    "pull request", "PR #" or "commit"
Flagged results are written to audit_search.csv for reading by hand. Nothing is changed.

  python audit_search.py
"""
import csv
import difflib
import glob
import json
import os
import re

H = "/data/wang/junh/githubs/stochastic-harness"
AD = f"{H}/AgentDefect/SelfHeal"
AI = f"{H}/AgentIssue-Bench/SelfHeal"
ISSUES = "/data/wang/junh/githubs/AgentIssue-Bench/motivation_experiment/artifacts/agentissue/issues"
csv.field_size_limit(10**9)


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s.lower())).strip()


def close(a, b):
    a, b = norm(a), norm(b)
    return bool(a) and bool(b) and difflib.SequenceMatcher(None, a, b).ratio() >= 0.8


def results_in(log):
    """(tool, query, title, snippet) of every search result in one relay log, once per tool call."""
    seen, out = set(), []
    for line in open(log, encoding="utf-8"):
        msgs = json.loads(line)["request"].get("messages", [])
        calls = {}
        for m in msgs:
            for tc in m.get("tool_calls") or []:
                calls[tc["id"]] = (tc["function"]["name"], tc["function"].get("arguments", ""))
        for m in msgs:
            cid = m.get("tool_call_id")
            if m.get("role") != "tool" or cid in seen or cid not in calls:
                continue
            name, args = calls[cid]
            if name not in ("web_search", "verify_api_usage"):
                continue
            seen.add(cid)
            text = str(m.get("content") or "")
            for block in text.split("\n\n"):
                lines = block.strip().split("\n")
                if not lines or not lines[0].strip():
                    continue
                out.append((name, args, lines[0].strip(), " ".join(lines[1:]).strip()))
    return out


def ad_targets():
    rows = {r["id"]: r for r in csv.DictReader(open(f"{AD}/inputs/test_descriptions.csv", encoding="utf-8"))}
    return {c: {"title": r["title"], "ids": [c] if c != "hf-26" else ["145964"]} for c, r in rows.items()}


def ai_targets():
    out = {}
    for f in glob.glob(f"{ISSUES}/*.json"):
        tag = os.path.basename(f)[:-5]
        d = json.load(open(f))
        m = re.match(r"https://github\.com/([^/]+)/([^/]+)/issues/(\d+)", d["url"])
        title = d.get("title") or ("Fail to build tiktoken while installing crewai" if tag == "crewai_1824" else "")
        out[tag] = {"owner": m.group(1), "repo": m.group(2), "number": m.group(3), "title": title}
    return out


def flag_ad(case, t, title, snippet):
    why = []
    if close(title, t["title"]):
        why.append("title close to the post title")
    if any(i in title + " " + snippet for i in t["ids"]):
        why.append("holds the post id")
    return why


def flag_ai(tag, t, title, snippet):
    text = f"{title} {snippet}"
    low = text.lower()
    repo = t["repo"].lower()
    why = []
    if repo in low and re.search(rf"#\s*{t['number']}\b|issues/{t['number']}\b|issue {t['number']}\b", low):
        why.append("repository and issue number")
    if close(title, t["title"]):
        why.append("title close to the issue title")
    if repo in low and re.search(r"pull request|\bpr #|\bcommit\b", low):
        why.append("repository with pull request or commit")
    return why


def main():
    out = []
    summary = {}
    adt, ait = ad_targets(), ai_targets()
    for ds, base, targets, flag in [("AgentDefect", AD, adt, flag_ad), ("AgentIssue-Bench", AI, ait, flag_ai)]:
        for log in sorted(glob.glob(f"{base}/**/relay_log_run_agent.jsonl", recursive=True)):
            rel = os.path.relpath(os.path.dirname(log), base)
            parts = rel.split("/")
            case = next((p for p in parts if p in targets), None)
            if case is None:
                continue
            res = results_in(log)
            key = (ds, parts[0], "/".join(p for p in parts[1:] if p.startswith("_")) or "kept")
            s = summary.setdefault(key, {"logs": 0, "results": 0, "flagged results": 0, "logs with a flag": 0})
            s["logs"] += 1
            s["results"] += len(res)
            hit = False
            for tool, query, title, snippet in res:
                why = flag(case, targets[case], title, snippet)
                if why:
                    hit = True
                    s["flagged results"] += 1
                    out.append({"dataset": ds, "folder": rel, "case": case, "tool": tool, "query": query[:300],
                                "title": title[:300], "snippet": snippet[:500], "why": "; ".join(why)})
            s["logs with a flag"] += hit
    path = f"{AD}/audit_search.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["dataset", "folder", "case", "tool", "query", "title", "snippet", "why"])
        w.writeheader()
        w.writerows(out)
    print(f"{len(out)} flagged results written to {path}")
    print("| dataset | model | runs | relay logs | search results | flagged results | logs with a flag |")
    print("|---|---|---|---|---|---|---|")
    for (ds, m, which), s in sorted(summary.items()):
        print(f"| {ds} | {m} | {which} | {s['logs']} | {s['results']} | {s['flagged results']} | {s['logs with a flag']} |")


if __name__ == "__main__":
    main()
