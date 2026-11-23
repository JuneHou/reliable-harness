#!/usr/bin/env python3
"""Leakage audit of one HarnessFix rerun (plan decision "leakage").

Reads every mini-swe-agent trajectory the rerun's analysis, aggregate and modify agents wrote, takes
each shell command they ran, and flags commands that touch the reference fix or the test: the
dataset archive, run_fixed.py, test.py, readme.md, developer patches, the moved-aside fix runs,
other method folders, the rerun's own test folders, or the web (a command that can reach the network,
such as curl, wget, git clone or a call that opens a web address). Commands
that name an absolute path outside the rerun's HarnessFix copy, /tmp and system folders are listed
for review. Writes leakage_audit.json in the rerun folder.

Text an agent writes through cat or tee with a here-document (a plan, a summary, a diagnosis) is left out
before matching, so a file name mentioned in written text is not a hit (plan departure 4). Everything else
in the command is matched, including here-documents fed to python, bash or another interpreter.

A shell tool that can reach the network (curl, wget and the like) counts in the shell part of a command, and inside
Python code the command runs only when that code starts a process or does not parse, so a tool name in text that a
Python script writes into a file (a Dockerfile, a plan) is not a hit. A here-document whose operator was recorded as
&lt;&lt; is read as one, since bash refuses that line and nothing after it runs, and a here-document that cat
or tee starts at the top level with no closing line is text to the end of the command, as bash reads it (plan
departure 4).

Usage: audit_leakage.py <rerun folder>
"""
import ast
import json
import os
import re
import sys

FLAGS = [
    ("dataset archive", r"AgentDefect\.zip|githubs/SelfHeal|githubs/AgentDefect\b|githubs/AgentIssue-Bench|metadata\.json|fixed_commit|inputs/issues"),
    ("reference fix", r"run_fixed\.py|developer\.patch|developer_patch\.json|_dropped_fixed_runs"),
    ("test or readme", r"\btest\.py\b|readme\.md|test_runs/"),
    ("other method folders", r"stochastic-harness/(AgentDefect|AgentIssue-Bench)/(SelfHeal|ModularRSI)|case_check"),
    # a command that can reach the network; a web address that only appears in text the command writes or
    # runs (a code comment, a plan) reaches nothing, and neither does the name urllib.request in an import line,
    # so the urllib.request calls that open an address are matched, not the module name (plan departure 4)
    # shell tools are matched anywhere in the command; the Python calls of WEB_PY only in Python code the command
    # runs (see web_python), so program code that a command writes into a file (sed, or a string a script writes)
    # is not a hit (plan departure 4)
    ("web", r"\bcurl\b|\bwget\b|git (clone|fetch|pull)|pip download|\blynx\b|\bw3m\b"),
]
WEB_PY = re.compile(r"urlopen|urlretrieve|build_opener|urllib\.request\.Request|requests\.(get|post|put|head|request|Session)"
                    r"|httpx\.|aiohttp|webbrowser\.open")
SYSTEM = ("/tmp", "/usr", "/bin", "/etc", "/proc", "/dev", "/lib", "/opt")
CMD = re.compile(r"<mswea_bash_command>(.*?)</mswea_bash_command>", re.S)
# the delimiter may be quoted, and the quote escaped with backslashes before or after it, as in
# bash -lc $'cat <<\\'EOF\\' ...' or bash -lc 'cat <<'\EOF' ...'
HEREDOC = re.compile(r"""(?:<<|&lt;&lt;)-?[ \t]*(?:\\|['"])*[ \t]*([A-Za-z_][A-Za-z0-9_]*)(?:\\|['"])*""")


def without_written_text(cmd):
    """The command with the bodies of here-documents that cat or tee write left out."""
    c = cmd.replace("\\n", "\n")
    pos = 0
    while True:
        m = HEREDOC.search(c, pos)
        if not m:
            return c
        line_start = c.rfind("\n", 0, m.start()) + 1
        line_end = c.find("\n", m.end())
        if line_end == -1:
            return c
        # the closing line is the delimiter alone, or the delimiter followed by the quote that ends a quoted
        # script such as bash -lc '... EOF' && echo ..., where the rest of that line belongs to the outer command
        close = re.compile(r"\n[ \t]*" + re.escape(m.group(1)) + r"""(?=[\\'"]|[ \t]*(?:\n|$))""").search(c, line_end)
        if not close:
            # a here-document with no closing line runs to the end of the script, as bash reads it, so a cat or
            # tee that starts its line outside any quoted script writes the rest of the command as text
            before = c[:line_start]
            top_level = len(re.findall(r"(?<!\\)'", before)) % 2 == 0 and len(re.findall(r'(?<!\\)"', before)) % 2 == 0
            if top_level and re.match(r"[ \t]*(cat|tee)\b", c[line_start:m.start()]):
                return c[:line_end]
            return c
        if re.search(r"\b(cat|tee)\b", c[line_start:m.start()] + " " + c[m.end():line_end]):
            c = c[:line_end] + c[close.start():]
            pos = line_end + 1
        else:
            pos = close.end()


def call_names(code):
    """Dotted names of the functions a Python script calls, or None when the script does not parse."""
    for text in (code, code.replace('\\"', '"').replace("\\$", "$")):
        try:
            tree = ast.parse(text)
        except (SyntaxError, ValueError):
            continue
        names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                parts, f = [], node.func
                while isinstance(f, ast.Attribute):
                    parts.append(f.attr)
                    f = f.value
                if isinstance(f, ast.Name):
                    parts.append(f.id)
                names.append(".".join(reversed(parts)))
        return names
    return None


def python_code(c):
    """The Python code a command runs: here-documents fed to python, and python -c arguments."""
    out, pos = [], 0
    while True:
        m = HEREDOC.search(c, pos)
        if not m:
            break
        line_start = c.rfind("\n", 0, m.start()) + 1
        line_end = c.find("\n", m.end())
        if line_end == -1:
            break
        close = re.compile(r"\n[ \t]*" + re.escape(m.group(1)) + r"""(?=[\\'"]|[ \t]*(?:\n|$))""").search(c, line_end)
        if not close:
            break
        if re.search(r"\bpython[0-9.]*\b", c[line_start:m.start()]):
            out.append(c[line_end + 1:close.start()])
        pos = close.end()
    out.extend(m.group(2) for m in re.finditer(r"""\bpython[0-9.]*\s+-c\s+(['"])(.*?)(?<!\\)\1""", c, re.S))
    return out


def web_python(c, raw):
    """True when Python code the command runs calls the network. A script that does not parse is matched as text.
    The code is read from the command as recorded, where a \\n inside a Python string stays as written, and from the
    command with \\n read as a line break when the recorded command is one line."""
    for code in python_code(raw) or python_code(c):
        names = call_names(code)
        if WEB_PY.search("\n".join(names) if names is not None else code):
            return True
    return False


# Python calls that start a process, through which Python code could run a shell tool
SPAWN = re.compile(r"(^|\.)(system|popen|Popen|run|call|check_call|check_output|getoutput|getstatusoutput"
                   r"|spawn\w*|exec\w*|create_subprocess_\w+)$")
PY_C = re.compile(r"""\bpython[0-9.]*\s+-c\s+(['"])(.*?)(?<!\\)\1""", re.S)


def without_python_code(c):
    """The command with the Python code it runs left out: here-documents fed to python, and python -c arguments."""
    pos = 0
    while True:
        m = HEREDOC.search(c, pos)
        if not m:
            break
        line_start = c.rfind("\n", 0, m.start()) + 1
        line_end = c.find("\n", m.end())
        if line_end == -1:
            break
        close = re.compile(r"\n[ \t]*" + re.escape(m.group(1)) + r"""(?=[\\'"]|[ \t]*(?:\n|$))""").search(c, line_end)
        if not close:
            break
        if re.search(r"\bpython[0-9.]*\b", c[line_start:m.start()]):
            c = c[:line_end] + c[close.start():]
            pos = line_end + 1
        else:
            pos = close.end()
    return PY_C.sub(lambda m: m.group(0)[:m.start(2) - m.start(0)] + m.group(0)[m.end(2) - m.start(0):], c)


def shell_tool_in_python(c, raw, pat):
    """True when Python code the command runs names a shell tool of pat and starts a process, or does not parse."""
    for code in python_code(raw) or python_code(c):
        if not re.search(pat, code):
            continue
        names = call_names(code)
        if names is None or any(SPAWN.search(n) for n in names):
            return True
    return False


def commands(path):
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception:
        return []
    out = []
    for m in data.get("messages", []) if isinstance(data, dict) else []:
        if m.get("role") == "assistant":
            content = m.get("content")
            if isinstance(content, list):
                content = " ".join(str(c.get("text", "")) if isinstance(c, dict) else str(c) for c in content)
            out.extend(c.strip() for c in CMD.findall(content or ""))
    return out


def main():
    rerun = os.path.abspath(sys.argv[1])
    copy = os.path.join(rerun, "harnessfix")
    trajs = []
    for root, _, files in os.walk(copy):
        if ".venv" in root.split(os.sep) or "task_agent" in root.split(os.sep):
            continue
        trajs.extend(os.path.join(root, f) for f in files if f.endswith(".traj.json"))
    hits, outside, n = [], [], 0
    issue_mode = f"{os.sep}AgentIssue-Bench{os.sep}" in rerun
    for t in sorted(trajs):
        for raw in commands(t):
            n += 1
            c = without_written_text(raw)
            for label, pat in FLAGS:
                if label == "test or readme" and issue_mode:
                    # plan departure 4: an AgentIssue-Bench repository's own readme.md files (9 of the 50 trees
                    # hold one) are part of the harness folder HarnessFix may read and edit; the readme that
                    # names the fix exists only in AgentDefect, whose 37 program folders hold no readme
                    pat = r"\btest\.py\b|test_runs/"
                if label == "web":
                    hit = (re.search(pat, without_python_code(c)) or web_python(c, raw)
                           or shell_tool_in_python(c, raw, pat))
                else:
                    hit = re.search(pat, c)
                if hit:
                    # the analysis prompt itself names test-stdout.txt and test-stderr.txt, which are allowed
                    if label == "test or readme" and not re.search(r"\btest\.py\b|readme\.md|test_runs/", c):
                        continue
                    hits.append({"trajectory": os.path.relpath(t, rerun), "flag": label, "command": raw[:500]})
            for p in re.findall(r"(/[\w.\-/]+)", c):
                if p.startswith(copy) or p.startswith(SYSTEM) or p in ("/",):
                    continue
                outside.append({"trajectory": os.path.relpath(t, rerun), "path": p, "command": raw[:300]})
    rec = {"rerun": rerun, "trajectories": len(trajs), "commands": n, "hits": hits,
           "outside_paths": outside, "clean": not hits}
    json.dump(rec, open(os.path.join(rerun, "leakage_audit.json"), "w"), indent=1)
    print(f"audit {rerun}: {len(trajs)} trajectories, {n} commands, {len(hits)} hits, {len(outside)} outside paths")


if __name__ == "__main__":
    main()
