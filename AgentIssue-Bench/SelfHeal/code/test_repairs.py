"""Test each SelfHeal repair on AgentIssue-Bench once, with the issue's own test, under the shipped
evaluator and, for the 15 issues of evaluator/corrections.json, under the corrected evaluator too.

For each issue in sorted order, one image at a time (pulled, or the local agentissue-bench-amd64 image
for the 14 rebuilt), each kept rerun and each replaced first attempt of the three ARC models is tested:
  1. The FINAL CODE is split back into files at the lines "### <path>" of the files SelfHeal read.
     A file whose line is missing stays unchanged. With one file sent and no line returned, the whole
     FINAL CODE is that file. With several files sent and no line returned, the repair is not tested
     and counts as failing (Jun "Rule as proposed"). Trailing blank lines are removed and one final
     newline kept, and a part equal to its original apart from trailing white space leaves the file
     unchanged.
  2. The patch is `git diff` (a/ and b/ prefixes) in a temporary git repository holding the originals.
  3. The benchmark's command (AgentIssue-Bench/eval_patches.py lines 100 to 109, lines 64 to 74 for
     agixt_1369) with --network host and -e OPENAI_BASE_URL (Jun "Same as AgentDefect"). The repaired
     code's model calls go through relay.py to the rerun's ARC model. 300 second limit, none for
     agixt_1369, a timeout fails.
  4. Pass as eval_patches.py: no "FAILED" in stdout, exit 0 and one of its success messages.
The corrected evaluator (fix plan departure 5, Jun "approve") mounts the corrected files, links
/app/source_code_patched to /app/source_code_buggy after apply_patch, calls the entrypoint the image
declares, and accepts the extra success messages, as evaluator/corrections.json lists per issue. For
the issues of departure 13 it also mounts the patch folder where the entrypoint reads it and runs a listed
command before apply_patch.
Shipped results go to <attempt>/test/, corrected ones to <attempt>/test_corrected/.

  python test_repairs.py [--tags TAG ...]
"""
import argparse
import glob
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import uuid

AD_CODE = "/data/wang/junh/githubs/stochastic-harness/AgentDefect/SelfHeal/code"
ROOT = "/data/wang/junh/githubs/stochastic-harness/AgentIssue-Bench/SelfHeal"
INPUTS = os.path.join(ROOT, "inputs")
ISSUES = os.path.join(INPUTS, "issues")
REBUILT = "/data/wang/junh/githubs/stochastic-harness/AgentIssue-Bench/images_amd64"
CORRECTIONS = json.load(open(os.path.join(ROOT, "evaluator", "corrections.json")))
MODELS = ["gpt-oss-120b", "GLM-5.3", "DeepSeek-V4.1-Flash"]
RERUNS = 5
TIMEOUT = 300                                    # eval_patches.py line 112
VERSION_TIMEOUT = 600                            # test_agentissue_bench.py lines 109 and 110
DEFAULT_ENTRY = "/usr/local/bin/run_test_entrypoint.sh"   # eval_patches.py line 108
PASS_MESSAGES = ["PATCH SUCCEEDED", "PATCH SUCCESSFULLY VERIFIED", "FIX SUCCESSFULLY VERIFIED",
                 "NO BUG", "FIX CONFIRMED", "PATCH VERIFIED"]          # eval_patches.py lines 123 to 128
AGIXT_1369_EXTRA = "patched succeeded"                                  # eval_patches.py line 90


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


adt = load("ad_test_repairs", os.path.join(AD_CODE, "test_repairs.py"))
adt.EMBED_STORE = "/data/wang/junh/githubs/stochastic-harness/AgentIssue-Bench/embedding_store.jsonl"


def image_of(tag):
    return f"agentissue-bench-amd64:{tag}" if os.path.isdir(os.path.join(REBUILT, tag)) else f"alfin06/agentissue-bench:{tag}"


def final_code(rerun):
    """The AgentDefect reader (AgentDefect/SelfHeal/code/test_repairs.py final_code), reading the result
    file with newline="" so that a CR SelfHeal writes in its FINAL CODE is kept (none of the result files
    so far holds one)."""
    tag = os.path.basename(os.path.dirname(rerun))
    txt = open(os.path.join(rerun, "Fix-Agent", "results", f"{tag}_result.txt"), encoding="utf-8", newline="").read()
    m = re.search(r"FINAL CODE:\n-{10,}\n(.*?)\n-{10,}\n\s*ALL ATTEMPTS:", txt, re.S)
    if not m:
        raise RuntimeError(f"{rerun}: final code not found")
    return m.group(1)


def split_final(final, files):
    headers = {f"### {f}": f for f in files}
    lines = final.split("\n")
    idx = [i for i, l in enumerate(lines) if l in headers]
    if not idx:
        if len(files) == 1:
            return {files[0]: final}, "one file sent, no header returned, whole FINAL CODE is that file"
        return None, "several files sent, no header returned"
    parts = {}
    for j, i in enumerate(idx):
        f = headers[lines[i]]
        if f in parts:
            continue
        end = idx[j + 1] if j + 1 < len(idx) else len(lines)
        parts[f] = "\n".join(lines[i + 1:end])
    missing = [f for f in files if f not in parts]
    return parts, (f"header missing, unchanged: {missing}" if missing else None)


def make_patch(tag, parts):
    tmp = tempfile.mkdtemp()
    try:
        for f in parts:
            dst = os.path.join(tmp, f)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(ISSUES, tag, "repo", f), dst)
        g = ["git", "-C", tmp, "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=false"]
        subprocess.run(g[:3] + ["init", "-q"], check=True)
        subprocess.run(g + ["add", "-A"], check=True)
        subprocess.run(g + ["commit", "-q", "-m", "buggy"], check=True)
        changed, unchanged = [], []
        for f, text in parts.items():
            orig = open(os.path.join(tmp, f), "rb").read().decode("utf-8", "replace")
            new = text.rstrip() + "\n"
            if new.rstrip() == orig.rstrip():
                unchanged.append(f)
                continue
            open(os.path.join(tmp, f), "w", encoding="utf-8").write(new)
            changed.append(f)
        # Read as bytes: text mode would turn every CRLF of the diff into LF, and the patch would then
        # fail on files with CRLF line endings ("different line endings").
        raw = subprocess.run(g + ["diff", "--src-prefix=a/", "--dst-prefix=b/"], capture_output=True,
                             check=True).stdout
        return raw.decode("utf-8", "surrogateescape"), changed, unchanged
    finally:
        shutil.rmtree(tmp)


def run_eval(tag, image, model, out, evaluator, patch_text=None, diagnostic=False, extra=None, version=None):
    """One run of the benchmark's test in a fresh container. patch_text is applied with apply_patch and
    then test_patched runs. diagnostic runs the shipped test_buggy, and version="test_fixed" the shipped
    test_fixed, both as test_agentissue_bench.py runs them. Writes out/ and returns the record."""
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    corr = CORRECTIONS.get(tag, {}) if evaluator == "corrected" else {}
    entry = corr.get("entry", DEFAULT_ENTRY)
    rec = {"tag": tag, "model": model, "image": image, "evaluator": evaluator, **(extra or {})}
    vols = []
    if diagnostic or version:
        version = version or "test_buggy"
    else:
        pdir = os.path.join(out, "patch")
        os.makedirs(pdir)
        # surrogateescape writes back any byte that is not UTF-8 exactly as it was read
        open(os.path.join(pdir, "selfheal.patch"), "w", encoding="utf-8", errors="surrogateescape", newline="").write(patch_text)
        # The shipped command mounts the patch folder at /patches (eval_patches.py line 56). Departure 13:
        # the corrected evaluator mounts it at /patches/<tag> where the entrypoint reads it from there, and
        # runs a listed command before apply_patch.
        mount = corr.get("patch_mount", "/patches")
        vols += ["-v", f"{pdir}:{mount}"]
        link = " && ln -sfn /app/source_code_buggy /app/source_code_patched" if corr.get("link_patched") else ""
        pre = f"{corr['pre']} && " if corr.get("pre") else ""
        script = f"{pre}{entry} apply_patch {mount}/selfheal.patch{link} && {entry} test_patched"
    for m in corr.get("mounts", []):
        vols += ["-v", f"{m['host']}:{m['container']}:ro"]
    proc, port = adt.start_relay(model, os.path.join(out, "relay_log_test.jsonl"))
    base = f"http://127.0.0.1:{port}/v1"
    name = f"eval_{tag.replace('.', '_')}_{uuid.uuid4().hex[:8]}"
    if version:
        # test_agentissue_bench.py lines 95 to 110: the image's own declared entrypoint with the argument
        # test_buggy or test_fixed, BASE_URL set to OPENAI_API_BASE (lines 86 and 98), 600 seconds
        # (lines 109 and 110).
        # SERPERDEV_API_KEY and GOOGLE_GENERATIVE_AI_API_KEY are left out, since no such key exists here
        # (fix plan departure 13, haystack_9523). --network host and OPENAI_BASE_URL as in the patch test.
        cmd = ["docker", "run", "--rm", "--name", name, "--network", "host",
               "-e", f"OPENAI_API_KEY={adt.arc_key()}", "-e", f"OPENAI_API_BASE={base}", "-e", f"BASE_URL={base}",
               "-e", f"OPENAI_BASE_URL={base}", image, version]
        limit = VERSION_TIMEOUT
    else:
        cmd = ["docker", "run", "--rm", "--name", name, "--network", "host", "--entrypoint", "bash", *vols,
               "-e", f"OPENAI_API_KEY={adt.arc_key()}", "-e", f"OPENAI_API_BASE={base}", "-e", f"OPENAI_BASE_URL={base}",
               image, "-c", script]
        limit = None if tag == "agixt_1369" else TIMEOUT
    rec["command"] = [c if not c.startswith("OPENAI_API_KEY=") else "OPENAI_API_KEY=<ARC key>" for c in cmd]
    t0 = time.time()
    timed_out = False
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           stdin=subprocess.DEVNULL, timeout=limit)
        stdout, stderr, code = r.stdout or "", r.stderr or "", r.returncode
    except subprocess.TimeoutExpired as e:
        timed_out = True
        stdout = (e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else e.stdout) or ""
        stderr = (e.stderr.decode("utf-8", "replace") if isinstance(e.stderr, bytes) else e.stderr) or ""
        code = None
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)   # eval_patches.py line 143
    finally:
        proc.terminate()
        proc.wait()
    open(os.path.join(out, "test.log"), "w", encoding="utf-8").write(stdout)
    open(os.path.join(out, "test_stderr.log"), "w", encoding="utf-8").write(stderr)
    msgs = PASS_MESSAGES + ([AGIXT_1369_EXTRA] if tag == "agixt_1369" else []) + corr.get("extra_success", [])
    failed = timed_out or "FAILED" in stdout or code != 0
    # test_buggy and test_fixed get no pass rule: test_agentissue_bench.py logs output and exit code only
    # (lines 55 to 69, fix plan departure 15).
    passed = None if version else (not failed) and any(m in stdout for m in msgs)
    rec.update(exit=code, timed_out=timed_out, passed=passed, seconds=round(time.time() - t0, 1),
               failed_in_stdout="FAILED" in stdout, success_message=[m for m in msgs if m in stdout])
    json.dump(rec, open(os.path.join(out, "test_record.json"), "w"), indent=1)
    return rec


def test_attempt(model, tag, folder, image, evaluator, kind):
    out = os.path.join(folder, "test" if evaluator == "shipped" else "test_corrected")
    if os.path.exists(os.path.join(out, "test_record.json")):
        return "done before"
    rec = {"model": model, "tag": tag, "kind": kind, "attempt": os.path.relpath(folder, ROOT), "evaluator": evaluator}
    result = os.path.join(folder, "Fix-Agent", "results", f"{tag}_result.txt")
    if not os.path.exists(result):
        os.makedirs(out, exist_ok=True)
        rec.update(passed=False, not_run="no SelfHeal result (no input file or stopped)")
        json.dump(rec, open(os.path.join(out, "test_record.json"), "w"), indent=1)
        return rec["not_run"]
    final = final_code(folder)
    files = json.load(open(os.path.join(folder, "input_files.json")))["files"]
    parts, note = split_final(final, files)
    if parts is None:
        os.makedirs(out, exist_ok=True)
        rec.update(passed=False, not_run=note, files=files)
        json.dump(rec, open(os.path.join(out, "test_record.json"), "w"), indent=1)
        return note
    diff, changed, unchanged = make_patch(tag, parts)
    r = run_eval(tag, image, model, out, evaluator, patch_text=diff,
                 extra={**rec, "files": files, "split_note": note, "changed": changed, "unchanged": unchanged,
                        "empty_patch": not diff.strip(), "final_code_sha256": hashlib.sha256(final.encode()).hexdigest()})
    return "passed" if r["passed"] else f"failed exit {r['exit']}{' timeout' if r['timed_out'] else ''}"


def attempts(model, tag):
    """(folder, kind): the kept reruns, then the replaced first attempts (fix plan departure 7), then the
    reruns with the corrected test as input (fix plan departure 14), which are tested under the corrected
    evaluator only."""
    out = [(os.path.join(ROOT, model, tag, f"rerun_{k}"), "repair") for k in range(1, RERUNS + 1)]
    for where in ("_search_failed", "_stopped"):
        out += [(d, "first_attempt") for d in sorted(glob.glob(os.path.join(ROOT, model, where, tag, "rerun_*")))]
    out += [(d, "corrected_input") for d in sorted(glob.glob(os.path.join(ROOT, model, "_corrected_input", tag, "rerun_*")))
            if os.path.exists(os.path.join(d, "Fix-Agent", "results", f"{tag}_result.txt"))]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tags", nargs="*")
    # Fix plan departure 16: AgentDefect and AgentIssue-Bench never use the same ARC model at once, and a
    # model is tested only after its repair run has ended.
    ap.add_argument("--models", nargs="*", default=MODELS)
    a = ap.parse_args()
    tags = a.tags or sorted(json.load(open(os.path.join(INPUTS, "named_files.json"))))
    for tag in tags:
        evaluators = ["shipped"] + (["corrected"] if tag in CORRECTIONS else [])
        todo = [(m, d, kind, ev) for m in a.models for d, kind in attempts(m, tag) for ev in evaluators
                if not (kind == "corrected_input" and ev == "shipped")
                and not os.path.exists(os.path.join(d, "test" if ev == "shipped" else "test_corrected", "test_record.json"))]
        if not todo:
            print(tag, "all tests done before", flush=True)
            continue
        image = image_of(tag)
        if image.startswith("alfin06/"):
            subprocess.run(["docker", "pull", "-q", image], check=True, capture_output=True)
        try:
            for m, d, kind, ev in todo:
                print(tag, m, os.path.relpath(d, ROOT), ev, test_attempt(m, tag, d, image, ev, kind),
                      time.strftime("%H:%M:%S"), flush=True)
        finally:
            # Only a pulled image is removed. The 14 rebuilt amd64 images are local and are needed again for
            # the other models, as calibrate.py keeps them.
            if image.startswith("alfin06/"):
                subprocess.run(["docker", "rmi", "-f", image], capture_output=True)
                print(tag, "image removed", flush=True)


if __name__ == "__main__":
    main()
