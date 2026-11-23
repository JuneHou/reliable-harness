import json
import os
import difflib
import pandas as pd
import requests
from typing import Dict, Optional
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool


BASE_DIR = "Fix-Agent"
RESULTS_DIR = os.path.join(BASE_DIR, "results")
FIX_PATTERN_PATH = os.path.join(BASE_DIR, "fix_pattern_summaries.csv")
TEST_DESC_PATH = os.path.join(BASE_DIR, "test_descriptions_with_intent.csv")
DATASET_ROOT = os.path.join(BASE_DIR, "Dataset-Benchmark")

# Create results directory if it doesn't exist
os.makedirs(RESULTS_DIR, exist_ok=True)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

CURRENT_BUG_CONTEXT = ""
CURRENT_FIXED_CODE = ""
SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")


def _web_search_impl(query: str, num_results: Optional[int] = 5) -> str:
    """
    Internal implementation for web search.
    """
    import time
    from ddgs import DDGS
    items, last_error = None, None
    for wait in (0, 2, 4, 8):
        time.sleep(wait)
        try:
            items = DDGS().text(query, max_results=num_results)
            break
        except Exception as e:
            last_error = e
    if items is None:
        if "No results found" in str(last_error):
            return "No valid results found"
        return f"Search error {str(last_error)}"

    results = []

    for item in items or []:
        link = item.get("href", "")
        if "stackoverflow.com" in link.lower():
            continue
        title = item.get("title", "")
        snippet = item.get("body", "")
        results.append(f"{title}\n{snippet}")
        if len(results) >= num_results:
            break

    if not results:
        return "No valid results found"

    return "\n\n".join(results)


@tool
def web_search(query: str, num_results: Optional[int] = 5) -> str:
    """
    Search the public internet using SerpApi.
    Stack Overflow results are excluded.
    """
    return _web_search_impl(query, num_results)


def _load_buggy_code_impl(case_id: str) -> str:
    """
    Internal implementation to load buggy code.
    """
    try:
        folder = os.path.join(DATASET_ROOT, str(case_id))
        path = os.path.join(folder, "run_buggy.py")

        if not os.path.exists(path):
            return "Error run_buggy.py missing"

        with open(path, "r", encoding="utf8") as f:
            return f.read()
    except Exception as e:
        return f"Error loading buggy code {str(e)}"


def _load_test_code_impl(case_id: str) -> str:
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


@tool
def list_fix_patterns() -> str:
    """
    Return all available fix pattern names from the dataset.
    """
    try:
        df = pd.read_csv(FIX_PATTERN_PATH)
        return "\n".join(df["Fix Pattern"].tolist())
    except Exception as e:
        return f"Error loading fix patterns {str(e)}"


@tool
def get_fix_pattern_summary(name: str) -> str:
    """
    Return the unified summary for a specific fix pattern name.
    """
    try:
        df = pd.read_csv(FIX_PATTERN_PATH)
        match = df[df["Fix Pattern"].str.lower() == name.lower()]

        if match.empty:
            return "Fix pattern not found"

        return match.iloc[0]["Unified Summary"]
    except Exception as e:
        return f"Error loading fix pattern summary {str(e)}"


@tool
def submit_fixed_code(code: str) -> str:
    """
    Store the complete fixed source code proposed by the fixing agent.
    """
    global CURRENT_FIXED_CODE
    CURRENT_FIXED_CODE = code
    return "Fixed code stored successfully"


@tool
def generate_diff(case_id: str) -> str:
    """
    Generate a unified diff between the original buggy code and the fixed code.
    """
    original = _load_buggy_code_impl(case_id)

    if not CURRENT_FIXED_CODE:
        return "Error no fixed code available"

    diff_lines = difflib.unified_diff(
        original.splitlines(),
        CURRENT_FIXED_CODE.splitlines(),
        lineterm=""
    )

    diff_text = "\n".join(diff_lines)
    if not diff_text:
        return "No differences detected"

    return diff_text


@tool
def validate_fixed_code(case_id: str) -> str:
    """
    Validate the fixed code against test expectations and output format rules.
    """
    files = _input_files()
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


@tool
def verify_api_usage(component: str) -> str:
    """
    Verify a specific API component (function, method, class) from the fixed code.
    Searches the internet for documentation about parameters, return types, and functionality.
    
    Args:
        component: The function name, method, or API component to verify (e.g., "pandas.DataFrame.groupby", "requests.get")
    
    Returns:
        Verification results with information about parameters, return types, and correct usage.
    """
    if not component or not component.strip():
        return "Error: No component specified for verification"
    
    component = component.strip()
    
    # Enhanced search query with context about what we're looking for
    query = f"{component} Python parameters return type documentation"
    
    search_result = _web_search_impl(query, num_results=5)
    
    if "Error" in search_result:
        return f"Error: Could not search for {component} - {search_result}"
    
    if search_result == "No valid results found":
        return f"Warning: No documentation found for '{component}'. This may indicate:\n- Incorrect function/method name\n- Custom or internal function\n- Typo in the component name"
    
    # Return the search results for the LLM to analyze
    return f"Verification results for '{component}':\n\n{search_result}\n\nAnalyze the above information to determine if the usage in the fixed code is correct."


def create_fix_agent():
    """
    Create the fixing agent.
    This agent focuses only on producing corrected code.
    """
    if OPENROUTER_API_KEY:
        llm = ChatOpenAI(
            temperature=0, 
            model="google/gemini-3-pro-preview",
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY
        )
    else:
        llm = ChatOpenAI(temperature=0, model="gpt-5.2")

    tools = [
        web_search,
        list_fix_patterns,
        get_fix_pattern_summary,
        submit_fixed_code,
    ]

    return create_react_agent(llm, tools)


def create_critic_agent():
    """
    Create the critic agent.
    This agent evaluates correctness and consistency of the fixed code.
    """
    if OPENROUTER_API_KEY:
        llm = ChatOpenAI(
            temperature=0, 
            model="google/gemini-3-pro-preview",
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY
        )
    else:
        llm = ChatOpenAI(temperature=0, model="gpt-5.2")

    tools = [
        generate_diff,
        validate_fixed_code,
        verify_api_usage,
    ]

    return create_react_agent(llm, tools)


def run_fix_loop(case_id: str, max_attempts: int = 3) -> Dict:
    """
    Execute the fixing and evaluation loop for a single bug case.
    """
    global CURRENT_BUG_CONTEXT, CURRENT_FIXED_CODE
    CURRENT_FIXED_CODE = ""
    
    start_time = datetime.now()

    meta = pd.read_csv(TEST_DESC_PATH)
    row = meta[meta["id"].astype(str) == str(case_id)].iloc[0]
    CURRENT_BUG_CONTEXT = f"{row['intent']}"
    
    # Load buggy code and test code
    buggy_code = _load_buggy_code_impl(case_id)
    test_ok, test_code = _load_test_code_status(case_id)
    files = _input_files()
    file_list = "\n".join(f"- {f} ({_language(f)})" for f in files)

    attempts = []

    for attempt in range(1, max_attempts + 1):
        attempt_start_time = datetime.now()
        
        fixer = create_fix_agent()

        # Build fix prompt with buggy code included
        fix_prompt = f"""
Bug context:
{CURRENT_BUG_CONTEXT}

The reported problem may be a crash, an error or a wrong result, as the bug context describes.

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
"""

        for _ in fixer.stream(
            {"messages": [("user", fix_prompt)]},
            stream_mode="values"
        ):
            pass

        critic = create_critic_agent()

        # Build critic prompt with buggy code and test code (if available)
        if test_ok:
            critic_prompt = f"""
Evaluate the fixed code for case {case_id}.

Buggy code:
```
{buggy_code}
```

Test code:
```
{test_code}
```

Your task:
1. Use generate_diff to see what changed
2. Use validate_fixed_code to check structural correctness
3. Use verify_api_usage to verify any suspicious functions or API calls (pass the function/method name to check)
4. Respond with ACCEPT or REJECT and detailed reasoning

Respond with ACCEPT or REJECT and reasoning.
"""
        else:
            critic_prompt = f"""
Evaluate the fixed code for case {case_id}.

Buggy code:
```
{buggy_code}
```

Note: Test code is not available for this case.

Your task:
1. Use generate_diff to see what changed
2. Use validate_fixed_code to check structural correctness
3. Use verify_api_usage to verify any suspicious functions or API calls (pass the function/method name to check)
4. Based on the bug context and code changes, determine if the fix is reasonable

Respond with ACCEPT or REJECT and reasoning.
"""

        critic_output = ""
        for chunk in critic.stream(
            {"messages": [("user", critic_prompt)]},
            stream_mode="values"
        ):
            critic_output = chunk["messages"][-1].content
        
        attempt_end_time = datetime.now()
        attempt_duration = (attempt_end_time - attempt_start_time).total_seconds()

        attempts.append({
            "attempt": attempt,
            "verdict": critic_output,
            "code": CURRENT_FIXED_CODE,
            "duration_seconds": attempt_duration,
            "timestamp": attempt_end_time.strftime("%Y-%m-%d %H:%M:%S"),
        })

        if "ACCEPT" in critic_output:
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            
            return {
                "status": "ACCEPTED",
                "attempt": attempt,
                "final_code": CURRENT_FIXED_CODE,
                "all_attempts": attempts,
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_duration_seconds": total_duration,
            }

    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()
    
    return {
        "status": "FAILED",
        "attempt": max_attempts,
        "final_code": CURRENT_FIXED_CODE,
        "all_attempts": attempts,
        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_duration_seconds": total_duration,
    }


if __name__ == "__main__":
    meta = pd.read_csv(TEST_DESC_PATH)
    total_cases = 10
    
    for i in range(len(meta)):
        case_id = str(meta["id"].tolist()[i])
        output_path = os.path.join(RESULTS_DIR, f"{case_id}_result.txt")
    
        # Check if result already exists (right after getting case_id)
        if os.path.exists(output_path):
            print(f"⊘ Case {i+1}/{total_cases} ({case_id}) already processed - Skipping\n")
            continue
        print(f"Processing case {i+1}/{total_cases}: {case_id}...")

        result = run_fix_loop(case_id)

        output_path = os.path.join(RESULTS_DIR, f"{case_id}_result.txt")
        with open(output_path, "w", encoding="utf8") as f:
            f.write(f"Case ID: {case_id}\n")
            f.write(f"Status: {result['status']}\n")
            f.write(f"Final Attempt: {result['attempt']}\n")
            f.write(f"Start Time: {result['start_time']}\n")
            f.write(f"End Time: {result['end_time']}\n")
            f.write(f"Total Duration: {result['total_duration_seconds']:.2f} seconds\n")
            f.write("="*80 + "\n\n")
            
            f.write("FINAL CODE:\n")
            f.write("-"*80 + "\n")
            f.write(result['final_code'])
            f.write("\n" + "-"*80 + "\n\n")
            
            f.write("ALL ATTEMPTS:\n")
            f.write("="*80 + "\n")
            for att in result['all_attempts']:
                f.write(f"\nAttempt {att['attempt']}:\n")
                f.write(f"Timestamp: {att['timestamp']}\n")
                f.write(f"Duration: {att['duration_seconds']:.2f} seconds\n")
                f.write(f"Verdict: {att['verdict']}\n")
                f.write("-"*80 + "\n")
                f.write(att['code'])
                f.write("\n" + "-"*80 + "\n")

        print(f"✓ Case {i+1}/{total_cases} ({case_id}) completed - Status: {result['status']} - Saved to {output_path}\n")
