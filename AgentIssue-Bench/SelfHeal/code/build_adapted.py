"""Build the adapted SelfHeal configuration for AgentIssue-Bench (fix plan, departure 6, Jun "choice 2").

Reads AgentDefect/SelfHeal/code/run_agent.py (SelfHeal 812e6a3 with the DuckDuckGo search), applies
exact replacements and writes AgentIssue-Bench/SelfHeal/code/run_agent_adapted.py with its diff,
run_agent_adapted.diff. The changes:
  - fix prompt: the failure may be a crash, an error or a wrong result as the bug context describes,
    each file is listed with its language, plain code fences, and the reply format is every file under
    its own "### <path>" line with its complete text
  - critic prompts: plain code fences
  - test loader: an explicit status, so the critic loses the test only when the file is missing or
    cannot be read, never because of what the file contains (Jun "Loader error only", then
    "identify test-loader failure through an explicit error status or exception")
  - format check: a structural check in place of the "def " and "return" strings (Jun "Use a
    structural format check"). Each supplied header appears exactly once with text after it, syntax is
    checked where a parser is available here and recorded where none is, and no interface is
    required because no issue or test names one
The rules, intents, file selections, critic tools and verdict rule are unchanged.

  python build_adapted.py
"""
import difflib
import os

SRC = "/data/wang/junh/githubs/stochastic-harness/AgentDefect/SelfHeal/code/run_agent.py"
DIR = os.path.dirname(os.path.abspath(__file__))

STRUCT = r'''
LANGUAGES = {".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript", ".sh": "shell",
             ".toml": "TOML", ".yml": "YAML", ".yaml": "YAML", ".cfg": "plain text", ".txt": "plain text",
             ".md": "Markdown", ".ipynb": "Jupyter notebook JSON", ".json": "JSON"}


def _input_files():
    """The repository files this rerun gave SelfHeal, in order (input_files.json, written by driver.py)."""
    with open("input_files.json", encoding="utf8") as f:
        return json.load(f)["files"]


def _language(path):
    name = os.path.basename(path)
    if name == "Dockerfile":
        return "Dockerfile"
    return LANGUAGES.get(os.path.splitext(name)[1], "plain text")


def _split_files(code, files):
    headers = {f"### {f}": f for f in files}
    lines = code.split("\n")
    idx = [i for i, l in enumerate(lines) if l in headers]
    parts = {}
    for j, i in enumerate(idx):
        end = idx[j + 1] if j + 1 < len(idx) else len(lines)
        parts.setdefault(headers[lines[i]], "\n".join(lines[i + 1:end]))
    return parts, lines


def _syntax(path, text):
    """(checked, problem or None, note)."""
    import ast as _ast
    import subprocess as _sp
    import tempfile as _tf
    ext = os.path.splitext(path)[1]
    try:
        if ext == ".py":
            _ast.parse(text)
            return True, None, "Python ast"
        if ext in (".ipynb", ".json"):
            json.loads(text)
            return True, None, "JSON"
        if ext in (".yml", ".yaml"):
            import yaml
            yaml.safe_load(text)
            return True, None, "YAML"
        if ext == ".sh":
            with _tf.NamedTemporaryFile("w", suffix=".sh", delete=False) as t:
                t.write(text)
            r = _sp.run(["bash", "-n", t.name], capture_output=True, text=True)
            os.unlink(t.name)
            return True, (r.stderr.strip()[:300] or None) if r.returncode else None, "bash -n"
    except Exception as e:
        return True, f"{type(e).__name__}: {str(e)[:300]}", ext
    return False, None, f"no parser available here for {_language(path)}"
'''

EDITS = [
    # test loader with an explicit status
    ('''def _load_test_code_impl(case_id: str) -> str:
    """
    Internal implementation to load test code.
    """
    try:
        folder = os.path.join(DATASET_ROOT, str(case_id))
        path = os.path.join(folder, "test.py")

        if not os.path.exists(path):
            return "Error test.py missing"

        with open(path, "r", encoding="utf8") as f:
            return f.read()
    except Exception as e:
        return f"Error loading test code {str(e)}"
''',
     '''def _load_test_code_impl(case_id: str) -> str:
    """
    Internal implementation to load test code.
    """
    return _load_test_code_status(case_id)[1]


def _load_test_code_status(case_id: str):
    """
    Load the test code with an explicit status: (True, text), or (False, reason) when the file is
    missing or cannot be read. The file's contents never set the status.
    """
    try:
        folder = os.path.join(DATASET_ROOT, str(case_id))
        path = os.path.join(folder, "test.py")

        if not os.path.exists(path):
            return False, "Error test.py missing"

        with open(path, "r", encoding="utf8") as f:
            return True, f.read()
    except Exception as e:
        return False, f"Error loading test code {str(e)}"
''' + STRUCT),
    # structural format check
    ('''    test_code = _load_test_code_impl(case_id)

    if "Error" in test_code:
        return "REJECT test code unavailable"

    problems = []

    if "def " not in CURRENT_FIXED_CODE:
        problems.append("no function definition found")

    if "return" not in CURRENT_FIXED_CODE and "assert" in test_code:
        problems.append("missing return statement")

    if problems:
        return "REJECT " + "; ".join(problems)

    return "ACCEPT fixed code matches expected structure and output format"
''',
     '''    files = _input_files()
    parts, lines = _split_files(CURRENT_FIXED_CODE, files)
    problems, notes = [], []

    for f in files:
        n = sum(1 for l in lines if l == f"### {f}")
        if n != 1:
            problems.append(f"the line ### {f} appears {n} times, expected once")
        elif not parts.get(f, "").strip():
            problems.append(f"no file text after ### {f}")
        else:
            checked, problem, note = _syntax(f, parts[f])
            if problem:
                problems.append(f"syntax error in {f}: {problem}")
            elif not checked:
                notes.append(f"{f}: {note}")

    notes.append("no required interface checked, because the issue and its test name none")

    if problems:
        return "REJECT " + "; ".join(problems) + " | notes: " + "; ".join(notes)

    return "ACCEPT every file is present once with its full text | notes: " + "; ".join(notes)
'''),
    ('''    test_code = _load_test_code_impl(case_id)

    attempts = []''',
     '''    test_ok, test_code = _load_test_code_status(case_id)
    files = _input_files()
    file_list = "\\n".join(f"- {f} ({_language(f)})" for f in files)

    attempts = []'''),
    # fix prompt
    ('''IMPORTANT: This is NOT a crash bug. The issue is that the output does not match what the user expects.

Buggy code:
```python
{buggy_code}
```

Your task:
- Analyze the buggy code and understand why the output doesn't match expectations
- Produce corrected Python code that fixes the output mismatch
- Submit the full corrected code using submit_fixed_code tool

Produce corrected Python code only.
"""''',
     '''The reported problem may be a crash, an error or a wrong result, as the bug context describes.

Files and their languages:
{file_list}

Buggy code, each file starting with its own line ### <path>:
```
{buggy_code}
```

Your task:
- Analyze the buggy code and understand the reported problem
- Correct the code so the reported problem is fixed
- Submit the full corrected code using submit_fixed_code tool

Return every file, each starting with its own line ### <path> exactly as given, followed by the file's complete corrected text, in the same order. Return the files only.
"""'''),
    # critic prompt with the test, by loader status
    ('''        if "Error" not in test_code:
            critic_prompt = f"""
Evaluate the fixed code for case {case_id}.

Buggy code:
```python
{buggy_code}
```

Test code:
```python
{test_code}
```''',
     '''        if test_ok:
            critic_prompt = f"""
Evaluate the fixed code for case {case_id}.

Buggy code:
```
{buggy_code}
```

Test code:
```
{test_code}
```'''),
    ('''Evaluate the fixed code for case {case_id}.

Buggy code:
```python
{buggy_code}
```

Note: Test code is not available for this case.''',
     '''Evaluate the fixed code for case {case_id}.

Buggy code:
```
{buggy_code}
```

Note: Test code is not available for this case.'''),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    new = src
    for old, rep in EDITS:
        n = new.count(old)
        if n != 1:
            raise SystemExit(f"expected one of {old[:70]!r}, found {n}")
        new = new.replace(old, rep)
    if "import json" not in new:
        new = new.replace("import os\n", "import json\nimport os\n", 1)
    out = os.path.join(DIR, "run_agent_adapted.py")
    open(out, "w", encoding="utf-8").write(new)
    diff = "".join(difflib.unified_diff(src.splitlines(True), new.splitlines(True),
                                        fromfile="AgentDefect/SelfHeal/code/run_agent.py",
                                        tofile="AgentIssue-Bench/SelfHeal/code/run_agent_adapted.py"))
    open(os.path.join(DIR, "run_agent_adapted.diff"), "w", encoding="utf-8").write(diff)
    print("written", out, "diff lines", diff.count("\n"))


if __name__ == "__main__":
    main()
