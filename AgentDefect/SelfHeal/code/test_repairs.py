"""Test each SelfHeal repair once with its case's own test.py.

The 37 AgentDefect cases have 15 different requirement lists, numbered as in LISTS. Each list gets
one environment, except list 1, whose eight cases in SPLIT get a second environment, list_1b (Jun
"chose the easiest one or which can be resued"), and of those 78188862 gets a third, list_1c, which
is list_1b with chromadb 1.3.7 and pydantic 2.12.5 (Jun "yes please install", "tes"). Environments are built one at a time, in order, and each is deleted before the
next is built. For each environment:
  1. Make a virtual environment test_envs/list_<n>/venv on the standalone Python 3.11.18 and
     install every pin of the list exactly as written (for list_1b, with SPLIT's nine versions, for
     list_1c, with SPLIT2's version as well), one at a time with `pip install --no-deps`,
     compiling with the system's gcc. A pin that cannot be installed is recorded and skipped.
  2. Run `pip check`. Every package it reports as not installed is installed with the version
     conditions its requiring packages state, again with --no-deps, so no listed version changes.
     Repeat until nothing is reported missing. Every pip check line still left is recorded.
  3. Load torch, transformers, openai, numpy and pandas, those the list pins, and record whether
     each loads at its pinned version. For list_1b and list_1c, also load every import of each case's
     run_buggy.py, run_fixed.py and test.py. The repairs are tested whatever this gives.
  4. For each case of the list, each ARC model and each of the five reruns, copy the case folder to
     <model>/<case>/rerun_<k>/test/, write the FINAL CODE SelfHeal returned as run_fixed.py (every
     test.py imports run_agent from run_fixed) and run `python test.py` once in the list's
     environment. The repair passes when test.py exits with 0.
  5. Delete the list's environment, so only one exists at a time.

Each list's environment record is test_env_logs/list_<n>_install.json, with pip's output in
list_<n>_install.log. The program's chat calls go through relay.py to the rerun's ARC model. Its
embedding calls go to OpenAI through the embedding store. The relay returns usage with only its
three counts (--usage-counts-only), Jun "yes".

  python test_repairs.py [--lists N ...]
"""
import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile

ROOT = "/data/wang/junh/githubs/stochastic-harness/AgentDefect/SelfHeal"
CODE = os.path.join(ROOT, "code")
INPUTS = os.path.join(ROOT, "inputs")
TEST_ENVS = os.path.join(ROOT, "test_envs")
ENV_LOGS = os.path.join(ROOT, "test_env_logs")
ZIP = "/data/wang/junh/githubs/SelfHeal/AgentDefect.zip"
PY = "/data/wang/junh/python/cpython-3.10.19/bin/python3.10"        # runs this script and the relay
PY_ENV = "/data/wang/junh/python/cpython-3.11.18/bin/python3.11"    # base of every list environment
ARC_KEY_FILE = "/data/wang/junh/.cache/keys/arc_llm_api.sh"
OPENAI_KEY_FILE = "/data/wang/junh/.cache/keys/institutional.sh"
EMBED_STORE = "/data/wang/junh/githubs/stochastic-harness/AgentDefect/embedding_store.jsonl"
MODELS = ["gpt-oss-120b", "GLM-5.3", "DeepSeek-V4.1-Flash"]
RERUNS = 5
ESSENTIAL = ["torch", "transformers", "openai", "numpy", "pandas"]

# List 1 pins langchain 0.0.245 beside langchain-core 1.2.5 and langchain-openai 1.1.6, which cannot
# load together. These eight cases import modules only a LangChain between them has. They get list 1
# with nine pins at the versions list 4 pins, keeping list 1's pydantic 1.10.26, fastapi and chromadb.
# Jun "chose the easiest one or which can be resued" (version A of three checked).
SPLIT = {"list": 1, "env": "1b", "source_list": 4,
         "cases": ["76897509", "76906469", "78020395", "78165764", "78188862", "78366661", "78429932",
                   "77555312"],
         "replace": {"langchain": "0.1.20", "langchain-classic": "1.0.0", "langchain-community": "0.0.38",
                     "langchain-core": "0.1.53", "langchain-openai": "0.1.7",
                     "langchain-text-splitters": "0.0.2", "langsmith": "0.1.147", "openai": "1.55.3",
                     "typing-extensions": "4.15.0"}}

# 78188862's program calls chromadb.PersistentClient (run_buggy.py line 41), which list 1's chromadb
# 0.3.29 lacks. It gets list_1b with chromadb at 1.3.7, the version list 4 and 12 other lists pin
# (Jun "yes please install"), and pydantic at list 4's 2.12.5, since chromadb 1.3.7's code imports
# field_validator from pydantic (chromadb/api/types.py line 24), which pydantic 1 lacks (Jun "tes").
SPLIT2 = {"base": "1b", "env": "1c", "cases": ["78188862"], "replace": {"chromadb": "1.3.7", "pydantic": "2.12.5"}}

# The test.py of these two cases imports from run_buggy, so as shipped it never runs the repair. In
# each test copy that line imports from run_fixed instead. Jun "tested with their test.py importing
# the repair".
TEST_IMPORT_FIX = {"78366661": ("from run_buggy import run_agent", "from run_fixed import run_agent"),
                   "78235199": ("from run_buggy import prepare_test_data, run_agent",
                                "from run_fixed import prepare_test_data, run_agent")}

# What five cases need on this machine (Jun "please fix the five cases"), and the two Ollama cases
# found later (Jun "fix environment").
TOOLS = "/data/wang/junh/tools"
OLLAMA_URL = "http://127.0.0.1:11434"
OLLAMA_CASES = {"78429932": ["llama3"],                                   # readme: ollama pull llama3
                "78838421": ["nomic-embed-text", "mxbai-embed-large", "mistral", "llama3"],  # readme, and llama3 in its code
                "79149108": ["llama3", "llama3.2"],                       # readme: ollama pull llama3, its code: MODEL = "llama3.2"
                "79638234": ["qwen2.5:14b"]}                              # readme and code: qwen2.5:14b
PG_CASE, PG_IMAGE = "79497660", "pgvector/pgvector:pg17"     # its test.py: localhost:5432, postgres/password, test_db
TESSERACT_CASE = "77555312"                                   # UnstructuredFileLoader calls tesseract
ADD_FILES = {"78188862": [("docs/paper1.pdf", "docs/test.pdf")]}  # its test.py opens docs/test.pdf, not shipped

# The 15 different requirement lists and the cases sharing each, numbered as in the 15-row table.
LISTS = {
    1: ["76379440", "76456041", "76621589", "76897509", "76906469", "77099194", "77178370",
        "77555312", "78020395", "78165764", "78188862", "78366661", "78429932"],
    2: ["78235199", "78564699", "79497660", "79746620"],
    3: ["76482987", "79149108", "79638234"],
    4: ["76670856", "77385587"],
    5: ["77376190", "77921898"],
    6: ["78383658", "79343179"],
    7: ["77015160", "77625508"],
    8: ["77209128", "79776520"],
    9: ["76364591"],
    10: ["79753835"],
    11: ["78838421"],
    12: ["78486966"],
    13: ["78396549"],
    14: ["76062338"],
    15: ["hf-26"],
}

# Run inside a list environment: for each (requiring package, missing package) pair that pip check
# reports, the requiring package's own requirement on the missing one, kept when its marker holds
# with no extra.
MISSING_HELPER = r'''
import json, sys, importlib.metadata as md
from pip._vendor.packaging.requirements import Requirement
from pip._vendor.packaging.utils import canonicalize_name
out = {}
for a, b in json.loads(sys.argv[1]):
    for r in md.distribution(a).requires or []:
        q = Requirement(r)
        if canonicalize_name(q.name) != canonicalize_name(b):
            continue
        if q.marker is not None and not q.marker.evaluate({"extra": ""}):
            continue
        e = out.setdefault(canonicalize_name(b), {"conditions": [], "required_by": []})
        e["conditions"] += [str(s) for s in q.specifier]
        e["required_by"].append(a)
print(json.dumps(out))
'''

VERSION_HELPER = r'''
import json, sys, importlib.metadata as md
print(json.dumps({n: md.version(n) for n in json.loads(sys.argv[1])}))
'''

LOAD_HELPER = r'''
import importlib, sys
from pip._vendor.packaging.specifiers import SpecifierSet
name, pinned = sys.argv[1], sys.argv[2]
v = importlib.import_module(name).__version__
print(v)
sys.exit(0 if v in SpecifierSet("==" + pinned) else 3)
'''


def arc_key():
    m = re.search(r'API_KEY\s*=\s*["\']?([^"\'\s]+)', open(ARC_KEY_FILE).read())
    if not m:
        raise SystemExit("API_KEY not found in the ARC key file")
    return m.group(1)


def case_ids():
    z = zipfile.ZipFile(ZIP)
    return sorted({p.split("/")[1] for p in z.namelist()
                   if p.count("/") >= 2 and not p.startswith("__MACOSX") and p.split("/")[1]})


def requirements(case):
    """The case's requirements.txt as SelfHeal's archive ships it: raw bytes and its pin lines in file order."""
    z = zipfile.ZipFile(ZIP)
    name = [p for p in z.namelist() if not p.startswith("__MACOSX")
            and p.split("/")[1:] == [case, "requirements.txt"]][0]
    raw = z.read(name)
    pins = [l.strip() for l in raw.decode("utf-8").splitlines() if l.strip() and not l.strip().startswith("#")]
    return raw, pins


def canon(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def pin_map(pins):
    return {canon(p.split("==")[0]): p.split("==", 1)[1] for p in pins if "==" in p}


def environments():
    """(env name, list number, cases, pins) in run order."""
    out = []
    for n in sorted(LISTS):
        pins = requirements(LISTS[n][0])[1]
        if n != SPLIT["list"]:
            out.append((str(n), n, LISTS[n], pins))
            continue
        out.append((str(n), n, [c for c in LISTS[n] if c not in SPLIT["cases"]], pins))
        new, done = [], set()
        for p in pins:
            name = p.split("==")[0]
            if canon(name) in SPLIT["replace"]:
                new.append(f"{name}=={SPLIT['replace'][canon(name)]}")
                done.add(canon(name))
            else:
                new.append(p)
        if done != set(SPLIT["replace"]):
            raise SystemExit(f"list {n} lacks {set(SPLIT['replace']) - done}")
        out.append((SPLIT["env"], n, [c for c in SPLIT["cases"] if c not in SPLIT2["cases"]], new))
        new2, done2 = [], set()
        for p in new:
            name = p.split("==")[0]
            if canon(name) in SPLIT2["replace"]:
                new2.append(f"{name}=={SPLIT2['replace'][canon(name)]}")
                done2.add(canon(name))
            else:
                new2.append(p)
        if done2 != set(SPLIT2["replace"]):
            raise SystemExit(f"list {n} lacks {set(SPLIT2['replace']) - done2}")
        out.append((SPLIT2["env"], n, SPLIT2["cases"], new2))
    return out


def check_split():
    """SPLIT's versions are the ones its source list pins, and its cases are in its list."""
    src = pin_map(requirements(LISTS[SPLIT["source_list"]][0])[1])
    if any(src.get(k) != v for k, v in SPLIT["replace"].items()):
        raise SystemExit(f"SPLIT's versions are not list {SPLIT['source_list']}'s")
    if not set(SPLIT["cases"]) < set(LISTS[SPLIT["list"]]):
        raise SystemExit("SPLIT cases are not all in its list")
    if any(src.get(k) != v for k, v in SPLIT2["replace"].items()):
        raise SystemExit(f"SPLIT2's versions are not list {SPLIT['source_list']}'s")
    if not set(SPLIT2["cases"]) < set(SPLIT["cases"]):
        raise SystemExit("SPLIT2 cases are not all in SPLIT")


def case_imports(case):
    """Every import statement of the case's run_buggy.py, run_fixed.py and test.py, with the names
    each `from ... import` takes, so that a missing name fails as well as a missing module."""
    import ast
    z = zipfile.ZipFile(ZIP)
    mods = set()
    for f in ("run_buggy.py", "run_fixed.py", "test.py"):
        names = [p for p in z.namelist() if not p.startswith("__MACOSX") and p.split("/")[1:] == [case, f]]
        if not names:
            continue
        try:
            tree = ast.parse(z.read(names[0]).decode("utf-8", "replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods.update(f"import {a.name}" for a in node.names
                            if a.name.split(".")[0] not in ("run_fixed", "run_buggy"))
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module \
                    and node.module.split(".")[0] not in ("run_fixed", "run_buggy"):
                names = [a.name for a in node.names if a.name != "*"]
                mods.add(f"from {node.module} import {', '.join(names)}" if names else f"import {node.module}")
    return sorted(mods)


def check_lists():
    """Every case's pin set equals its list's, the lists are different, and they cover all 37 cases."""
    listed = sorted(c for cs in LISTS.values() for c in cs)
    if listed != case_ids():
        raise SystemExit("LISTS does not cover exactly the archive's cases")
    sets = {}
    for n, cases in LISTS.items():
        s = {frozenset(requirements(c)[1]) for c in cases}
        if len(s) != 1:
            raise SystemExit(f"list {n}: its cases have different pin sets")
        sets[n] = s.pop()
    if len(set(sets.values())) != len(LISTS):
        raise SystemExit("two lists have the same pin set")
    return {n: len(s) for n, s in sets.items()}


def copy_case(case, dest):
    """The whole case folder as SelfHeal's archive ships it, its subfolders included."""
    os.makedirs(dest, exist_ok=True)
    z = zipfile.ZipFile(ZIP)
    for p in z.namelist():
        parts = p.split("/")
        if p.startswith("__MACOSX") or len(parts) < 3 or parts[1] != case or not parts[-1] \
                or parts[-1].startswith("._"):
            continue
        target = os.path.join(dest, *parts[2:])
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as f:
            f.write(z.read(p))
    if case == "hf-26":
        shutil.copy(os.path.join(INPUTS, "hf-26_run_buggy.py"), os.path.join(dest, "run_buggy.py"))


RECORD_FILES = {"run_fixed.py", "test.log", "relay_log_test.jsonl", "test_record.json"}


def case_files(case):
    """Relative paths of the case folder's files in SelfHeal's archive, as copy_case writes them."""
    z = zipfile.ZipFile(ZIP)
    out = set()
    for p in z.namelist():
        parts = p.split("/")
        if p.startswith("__MACOSX") or len(parts) < 3 or parts[1] != case or not parts[-1] \
                or parts[-1].startswith("._"):
            continue
        out.add(os.path.join(*parts[2:]))
    return out


def clean_test(t, case):
    """Delete everything the program created in a finished test folder: downloaded models, caches,
    databases. The case's own files, the repair and the test records stay. Jun "make sure clean
    after every run and test"."""
    keep = case_files(case) | RECORD_FILES
    removed = 0
    for root, dirs, files in os.walk(t, topdown=False):
        for f in files:
            path = os.path.join(root, f)
            if os.path.relpath(path, t) not in keep:
                removed += os.path.getsize(path) if not os.path.islink(path) else 0
                os.remove(path)
        for d in dirs:
            path = os.path.join(root, d)
            if os.path.islink(path):
                os.remove(path)
            elif not os.listdir(path):
                os.rmdir(path)
    return removed


def final_code(rerun):
    case = os.path.basename(os.path.dirname(rerun))
    txt = open(os.path.join(rerun, "Fix-Agent", "results", f"{case}_result.txt"), encoding="utf-8").read()
    m = re.search(r"FINAL CODE:\n-{10,}\n(.*?)\n-{10,}\n\s*ALL ATTEMPTS:", txt, re.S)
    if not m:
        raise RuntimeError(f"{rerun}: final code not found")
    return m.group(1)


def pip_check(pip, out):
    r = subprocess.run([pip, "check"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
    out.write("\n===== pip check\n" + r.stdout + r.stderr)
    out.flush()
    return [l.strip() for l in r.stdout.splitlines() if l.strip() and l.strip() != "No broken requirements found."]


def build_env(env_name, n, cases, pins):
    """Steps 1 to 3 for one environment. Returns its record and the environment's python."""
    folder = os.path.join(TEST_ENVS, f"list_{env_name}")
    shutil.rmtree(folder, ignore_errors=True)
    os.makedirs(folder)
    env_dir = os.path.join(folder, "venv")
    os.makedirs(ENV_LOGS, exist_ok=True)
    t0 = time.time()
    pip_env = dict(os.environ, CC="gcc", CXX="g++")   # the standalone Python names clang, not installed here
    installed, failed = [], []
    added, not_installable = {}, {}
    with open(os.path.join(ENV_LOGS, f"list_{env_name}_install.log"), "w") as out:
        subprocess.run([PY_ENV, "-m", "venv", env_dir], stdout=out, stderr=subprocess.STDOUT, check=True)
        pip = os.path.join(env_dir, "bin", "pip")
        py = os.path.join(env_dir, "bin", "python")

        # Step 1. Every pin exactly as written, one at a time.
        for pin in pins:
            out.write(f"\n===== {pin}\n")
            out.flush()
            r = subprocess.run([pip, "install", "--no-deps", "--force-reinstall", pin], env=pip_env,
                               stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
            (installed if r.returncode == 0 else failed).append(pin)

        # Step 2. What listed packages require but the list does not name, with no listed version changed.
        rounds, helper_error = 0, None
        while True:
            pairs = []
            for line in pip_check(pip, out):
                m = re.match(r"^(\S+) (\S+) requires (\S+), which is not installed\.$", line)
                if m and re.sub(r"[-_.]+", "-", m.group(3)).lower() not in not_installable:
                    pairs.append([m.group(1), m.group(3)])
            if not pairs:
                break
            rounds += 1
            r = subprocess.run([py, "-c", MISSING_HELPER, json.dumps(pairs)], capture_output=True, text=True)
            if r.returncode != 0:
                out.write("\n===== requirement helper failed\n" + r.stderr)
                helper_error = (r.stderr.strip().splitlines() or [""])[-1]
                break
            new = 0
            for name, e in sorted(json.loads(r.stdout).items()):
                req = name + ",".join(sorted(set(e["conditions"])))
                out.write(f"\n===== added {req} (required by {', '.join(sorted(set(e['required_by'])))})\n")
                out.flush()
                ri = subprocess.run([pip, "install", "--no-deps", req], env=pip_env,
                                    stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
                if ri.returncode == 0:
                    added[name] = {"requirement": req, "required_by": sorted(set(e["required_by"]))}
                    new += 1
                else:
                    not_installable[name] = {"requirement": req, "required_by": sorted(set(e["required_by"]))}
            if new == 0:
                break
        if added:
            r = subprocess.run([py, "-c", VERSION_HELPER, json.dumps(sorted(added))], capture_output=True, text=True)
            for name, v in json.loads(r.stdout).items():
                added[name]["version"] = v
        remaining = pip_check(pip, out)

        # Step 3. Load the essential packages the list pins.
        pinned = {re.split(r"==", p)[0].lower().replace("_", "-"): p.split("==", 1)[1] for p in pins if "==" in p}
        load = {}
        for name in ESSENTIAL:
            if name not in pinned:
                continue
            r = subprocess.run([py, "-c", LOAD_HELPER, name, pinned[name]], cwd=folder, capture_output=True,
                               text=True, stdin=subprocess.DEVNULL)
            ok = r.returncode == 0
            last = (r.stdout.strip().splitlines() or [""])[-1] if ok or r.returncode == 3 else \
                (r.stderr.strip().splitlines() or [""])[-1]
            load[name] = {"pinned": pinned[name], "loaded": ok, "printed_or_error": last}
            out.write(f"\n===== load {name}: {'loaded' if ok else 'not loaded'} {last}\n")

        # For the second and third list 1 environments, every import of each of its cases.
        imports = {}
        if env_name in (SPLIT["env"], SPLIT2["env"]):
            for c in cases:
                failed_imports = {}
                for m in case_imports(c):
                    r = subprocess.run([py, "-c", m], cwd=folder, capture_output=True, text=True,
                                       stdin=subprocess.DEVNULL)
                    if r.returncode != 0:
                        failed_imports[m] = (r.stderr.strip().splitlines() or [""])[-1][:300]
                imports[c] = {"imports": case_imports(c), "failed": failed_imports}
                out.write(f"\n===== imports of {c}: {len(failed_imports)} failed {sorted(failed_imports)}\n")

    written = requirements(LISTS[n][0])[1]
    rec = {"env": env_name, "list": n, "cases": cases, "python": PY_ENV,
           "python_version": subprocess.run([PY_ENV, "-V"], capture_output=True, text=True).stdout.strip(),
           "pins": len(pins), "pins_replaced": {a: b for a, b in zip(written, pins) if a != b},
           "installed": len(installed), "failed": failed,
           "install": "all pins installed" if not failed else f"{len(failed)} pins not installed",
           "added_rounds": rounds, "added_helper_error": helper_error, "added": added, "added_not_installable": not_installable,
           "pip_check_remaining": remaining, "load": load, "case_imports": imports,
           "seconds": round(time.time() - t0, 1),
           "requirements_sha256": {c: hashlib.sha256(requirements(c)[0]).hexdigest() for c in cases}}
    json.dump(rec, open(os.path.join(ENV_LOGS, f"list_{env_name}_install.json"), "w"), indent=1)
    return rec, os.path.join(env_dir, "bin", "python")


def start_relay(model, log_path):
    port_file = log_path + ".port"
    if os.path.exists(port_file):
        os.remove(port_file)
    proc = subprocess.Popen([PY, os.path.join(CODE, "relay.py"), "--model", model, "--log", log_path,
                             "--port-file", port_file, "--embed-store", EMBED_STORE,
                             "--openai-key-file", OPENAI_KEY_FILE, "--usage-counts-only"])
    for _ in range(100):
        if os.path.exists(port_file) and open(port_file).read().strip():
            return proc, int(open(port_file).read())
        time.sleep(0.1)
    proc.kill()
    raise RuntimeError("relay did not start")


def ollama_ready(models):
    import urllib.request
    try:
        tags = json.loads(urllib.request.urlopen(OLLAMA_URL + "/api/tags", timeout=10).read())
    except Exception as e:
        raise RuntimeError(f"Ollama not reachable at {OLLAMA_URL}: {e!r}")
    # A name without a tag is the ":latest" tag, as "ollama pull llama3" stores llama3:latest.
    have = {m["name"] for m in tags.get("models", [])}
    missing = [m for m in models if (m if ":" in m else m + ":latest") not in have]
    if missing:
        raise RuntimeError(f"Ollama lacks models {missing}")
    return sorted(have)


def start_postgres(name):
    subprocess.run(["docker", "rm", "-f", name], capture_output=True)
    subprocess.run(["docker", "run", "-d", "--name", name, "-e", "POSTGRES_PASSWORD=password",
                    "-e", "POSTGRES_DB=test_db", "-p", "127.0.0.1:5432:5432", PG_IMAGE],
                   check=True, capture_output=True)
    for _ in range(120):
        r = subprocess.run(["docker", "exec", name, "pg_isready", "-h", "127.0.0.1", "-U", "postgres",
                            "-d", "test_db"], capture_output=True)
        if r.returncode == 0:
            return
        time.sleep(1)
    subprocess.run(["docker", "rm", "-f", name], capture_output=True)
    raise RuntimeError("Postgres container did not become ready")


def program_env(port):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("OPENAI_", "PIP_"))}
    env["OPENAI_API_KEY"] = arc_key()
    env["OPENAI_BASE_URL"] = f"http://127.0.0.1:{port}/v1"
    env["OPENAI_API_BASE"] = f"http://127.0.0.1:{port}/v1"
    return env


# Fix plan departure 3 (Jun "2 AgentDefect calib"): the 11 cases whose environment, fixture or test
# was changed, and the two Ollama cases found later (Jun "3. yes"). test.py runs on the archive's
# run_buggy.py and on its run_fixed.py, five runs each per model, in the same environment and with the
# same tools as the repair tests.
CALIB_ROOT = "/data/wang/junh/githubs/stochastic-harness/AgentDefect/case_check"
CALIB_FIRST = ["76897509", "76906469", "78020395", "78165764", "78366661", "78429932", "77555312",
               "78188862", "78235199", "78838421", "79497660", "79149108", "79638234"]
# Fix plan departure 16 (Jun "now. fix everything you didn't follow the plan"): Plan_bench.md step
# "Calibrate each evaluator" covers every case, so every case in the score tables is calibrated.
# 79776520 is left out of the score tables (Jun "for question 2, drop").
CALIB_LEFT_OUT = {"79776520"}
CALIB_RUNS = 5


def archive_text(case, name):
    z = zipfile.ZipFile(ZIP)
    p = [q for q in z.namelist() if not q.startswith("__MACOSX") and q.split("/")[1:] == [case, name]][0]
    return z.read(p).decode("utf-8")


def first_attempts(model, case):
    """Replaced first attempts of a planned repetition (fix plan departure 7), as move_aside.py left them."""
    out = []
    for where in ("_search_failed", "_stopped"):
        for d in sorted(glob.glob(os.path.join(ROOT, model, where, case, "rerun_*"))):
            out.append(d)
    return out


def test_one(model, case, k, py, env_rec):
    rerun = os.path.join(ROOT, model, case, f"rerun_{k}")
    t = os.path.join(rerun, "test")
    if os.path.exists(os.path.join(t, "test_record.json")):
        return "done before"
    return run_test(t, model, case, final_code(rerun), py, env_rec, {"kind": "repair", "rerun": k})


def test_first(model, case, folder, py, env_rec):
    t = os.path.join(folder, "test")
    if os.path.exists(os.path.join(t, "test_record.json")):
        return "done before"
    res = os.path.join(folder, "Fix-Agent", "results", f"{case}_result.txt")
    if not os.path.exists(res):
        os.makedirs(t, exist_ok=True)
        rec = {"case": case, "model": model, "kind": "first_attempt", "attempt": os.path.relpath(folder, ROOT),
               "passed": False, "not_run": "no SelfHeal result, the attempt stopped before it finished"}
        json.dump(rec, open(os.path.join(t, "test_record.json"), "w"), indent=1)
        return rec["not_run"]
    return run_test(t, model, case, final_code(folder), py, env_rec,
                    {"kind": "first_attempt", "attempt": os.path.relpath(folder, ROOT)})


def test_calib(model, case, which, k, py, env_rec):
    t = os.path.join(CALIB_ROOT, model, case, f"{which}_{k}")
    if os.path.exists(os.path.join(t, "test_record.json")):
        return "done before"
    if case == "hf-26" and which == "buggy":   # the archive ships no run_buggy.py, Plan_bench.md's rebuilt one
        code = open(os.path.join(INPUTS, "hf-26_run_buggy.py"), encoding="utf-8").read()
    else:
        code = archive_text(case, "run_buggy.py" if which == "buggy" else "run_fixed.py")
    return run_test(t, model, case, code, py, env_rec, {"kind": f"calibration_{which}", "run": k})


def run_test(t, model, case, code, py, env_rec, extra):
    k = extra.get("rerun") or extra.get("run") or 0
    shutil.rmtree(t, ignore_errors=True)
    copy_case(case, t)
    with open(os.path.join(t, "run_fixed.py"), "w", encoding="utf-8") as f:
        f.write(code)
    test_py_changed = None
    if case in TEST_IMPORT_FIX:
        old, new = TEST_IMPORT_FIX[case]
        src = open(os.path.join(t, "test.py"), encoding="utf-8").read()
        lines = src.split("\n")
        hits = [i for i, l in enumerate(lines) if l.strip() == old]
        if len(hits) != 1:
            raise RuntimeError(f"{case}: expected one line {old!r} in test.py, found {len(hits)}")
        lines[hits[0]] = lines[hits[0]].replace(old, new)
        open(os.path.join(t, "test.py"), "w", encoding="utf-8").write("\n".join(lines))
        test_py_changed = {"line": hits[0] + 1, "from": old, "to": new}
    files_added = []
    for src, dst in ADD_FILES.get(case, []):
        shutil.copy(os.path.join(t, src), os.path.join(t, dst))
        files_added.append({"file": dst, "copy_of": src})
    services = {}
    if case in OLLAMA_CASES:
        services["ollama"] = {"url": OLLAMA_URL, "models_present": ollama_ready(OLLAMA_CASES[case])}
    pg_name = None
    if case == PG_CASE:
        pg_name = f"selfheal-pg-{model}-{extra['kind']}-{k}".replace(".", "-").replace("_", "-").lower()
        start_postgres(pg_name)
        services["postgres"] = {"image": PG_IMAGE, "container": pg_name, "port": "127.0.0.1:5432"}
    proc, port = start_relay(model, os.path.join(t, "relay_log_test.jsonl"))
    env = program_env(port)
    if case == TESSERACT_CASE:
        env["PATH"] = os.path.join(TOOLS, "tesseract", "bin") + os.pathsep + env.get("PATH", "")
        services["tesseract"] = os.path.join(TOOLS, "tesseract", "bin", "tesseract")
    t0 = time.time()
    try:
        with open(os.path.join(t, "test.log"), "w") as out:
            r = subprocess.run([py, "test.py"], cwd=t, env=env, stdout=out,
                               stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    finally:
        proc.terminate()
        proc.wait()
        if pg_name:
            subprocess.run(["docker", "rm", "-f", pg_name], capture_output=True)
    rec = {"case": case, "model": model, **extra, "exit": r.returncode, "passed": r.returncode == 0,
           "seconds": round(time.time() - t0, 1), "python": py, "env": env_rec["env"], "env_list": env_rec["list"],
           "env_install": env_rec["install"], "env_pins_not_installed": env_rec["failed"],
           "env_load": env_rec["load"], "test_py_changed": test_py_changed,
           "files_added": files_added, "services": services,
           "final_code_sha256": hashlib.sha256(code.encode()).hexdigest()}
    json.dump(rec, open(os.path.join(t, "test_record.json"), "w"), indent=1)
    clean_test(t, case)
    return "passed" if rec["passed"] else f"failed exit {r.returncode}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lists", nargs="*", type=int)
    # Fix plan departure 16: AgentDefect and AgentIssue-Bench never use the same ARC model at once.
    ap.add_argument("--models", nargs="*", default=MODELS)
    a = ap.parse_args()
    calib_cases = set(case_ids()) - CALIB_LEFT_OUT
    sizes = check_lists()
    check_split()
    envs = environments()
    print("lists checked:", len(LISTS), "lists,", sum(map(len, LISTS.values())), "cases, pins per list",
          sizes, "| environments", [(e, len(cs)) for e, _, cs, _ in envs], flush=True)
    for env_name, n, cases, pins in envs:
        if a.lists and n not in a.lists:
            continue
        # An environment waits while any of its kept reruns has no SelfHeal result yet, so each
        # environment is built once, after its cases' reruns have ended.
        waiting = [f"{m}/{c}/rerun_{k}" for c in cases for m in MODELS for k in range(1, RERUNS + 1)
                   if not os.path.exists(os.path.join(ROOT, m, c, f"rerun_{k}", "Fix-Agent", "results", f"{c}_result.txt"))]
        if waiting:
            print("env", env_name, "deferred, reruns without a result:", " ".join(waiting), flush=True)
            continue
        todo = []
        for c in sorted(cases):
            for m in a.models:
                for k in range(1, RERUNS + 1):
                    if not os.path.exists(os.path.join(ROOT, m, c, f"rerun_{k}", "test", "test_record.json")):
                        todo.append((f"{c} {m} {k}", test_one, (m, c, k)))
                for d in first_attempts(m, c):
                    if not os.path.exists(os.path.join(d, "test", "test_record.json")):
                        todo.append((f"{c} {m} first {os.path.relpath(d, ROOT)}", test_first, (m, c, d)))
                if c in calib_cases:
                    for which in ("buggy", "fixed"):
                        for k in range(1, CALIB_RUNS + 1):
                            if not os.path.exists(os.path.join(CALIB_ROOT, m, c, f"{which}_{k}", "test_record.json")):
                                todo.append((f"{c} {m} calibration {which} {k}", test_calib, (m, c, which, k)))
        if not todo:
            print("env", env_name, "all tests done before", flush=True)
            continue
        print("env", env_name, "building", time.strftime("%H:%M:%S"), flush=True)
        try:
            env_rec, py = build_env(env_name, n, cases, pins)
            print("env", env_name, "environment", env_rec["install"], "| replaced", env_rec["pins_replaced"],
                  "| added", len(env_rec["added"]),
                  "| not installable", sorted(env_rec["added_not_installable"]),
                  "| pip check lines left", len(env_rec["pip_check_remaining"]),
                  "| load", {k: v["loaded"] for k, v in env_rec["load"].items()},
                  "| case import failures", {c: sorted(v["failed"]) for c, v in env_rec["case_imports"].items()},
                  "|", env_rec["seconds"], "s", flush=True)
            for label, fn, args in todo:
                print("env", env_name, label, fn(*args, py, env_rec), time.strftime("%H:%M:%S"), flush=True)
        finally:
            shutil.rmtree(os.path.join(TEST_ENVS, f"list_{env_name}"), ignore_errors=True)
            print("env", env_name, "environment deleted", flush=True)


if __name__ == "__main__":
    main()
