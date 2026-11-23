"""Calibrate the 50 AgentIssue-Bench evaluators (fix plan, departure 4, Jun "3 AgentIssue calib").

Per issue and model, five runs of each control through the same apply_patch and test_patched path as
the repairs, under the shipped evaluator and, for the 15 issues of evaluator/corrections.json, under the
corrected one:
  negative  the unmodified buggy code, through a null patch that only adds the empty file
            .calibration_null at the repository root (the entrypoints set up and reinstall the code
            inside apply_patch, so the control goes through it), no existing file changes
  positive  the developer patch, the git diff from the buggy tree to the fixed tree (AgentIssue-Bench
            paper 4.2, "the code changes between the buggy and correct versions"). The trees are the
            image's /app/source_code_buggy and /app/source_code_fixed, or, for issues whose entrypoint
            clones at run time, the checkouts of BUGGY_COMMIT and FIXED_COMMIT that the entrypoint's own
            clone lines make in the image. Files git reports as binary are left out and recorded.
and five runs of the shipped test_buggy as a diagnostic, whose successful exit can mean the defect was
reproduced, and five runs of the shipped test_fixed (fix plan departure 15), both run as
test_agentissue_bench.py runs them and recorded with their exit code and output, no pass rule. Mixed outcomes are reported as they are, no issue is dropped and no assertion is changed.
The developer patch is used only to check the evaluator, never as a method input. One image at a time.
Output: AgentIssue-Bench/case_check/<model>/<tag>/<evaluator>_<control>_<k>/.

  python calibrate.py [--model MODEL] [--tags TAG ...]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import time

import test_repairs as tr

ROOT = tr.ROOT
CHECK = "/data/wang/junh/githubs/stochastic-harness/AgentIssue-Bench/case_check"
ENTRY = json.load(open("/data/wang/junh/githubs/AgentIssue-Bench/motivation_experiment/artifacts/agentissue/entrypoints.json"))
ENTRY = {e["tag"]: e for e in ENTRY}
RUNS = 5
NULL_PATCH = "diff --git a/.calibration_null b/.calibration_null\nnew file mode 100644\nindex 0000000..e69de29\n"
# Fix plan departure 13, Jun (2026-11-12): autogen_4197's fix renames "docs/design/03 - Agent Worker Protocol.md",
# a name with spaces, and GNU patch in the image cannot read git's rename entry for it ("Cannot rename file
# without two valid file names"). Its patch writes every rename as a delete and an add. The other patches
# keep git's rename entries.
NO_RENAMES = {"autogen_4197"}


def fixed_tree(tag, image, dest):
    """Tracked files of the image's /app/source_code_fixed."""
    sh = ("cd /app/source_code_fixed && git config --global --add safe.directory '*' && "
          "git ls-files -z | tar --null --no-recursion -T - -cf -")
    os.makedirs(dest, exist_ok=True)
    p1 = subprocess.Popen(["docker", "run", "--rm", "--entrypoint", "sh", image, "-c", sh],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2 = subprocess.run(["tar", "-xf", "-", "-C", dest], stdin=p1.stdout, capture_output=True)
    p1.wait()
    if p1.returncode or p2.returncode:
        raise RuntimeError(f"{tag}: fixed tree not read from the image")
    return "image /app/source_code_fixed, git ls-files"


def clone_lines(tag):
    """The entrypoint's own clone lines, verbatim, from its first 'git clone' to its
    'git checkout "$commit_hash"' line, comments and blank lines left out."""
    f = os.path.join(tr.ISSUES, tag, "entrypoint_usr_local_bin.sh")
    if not os.path.exists(f):
        f = os.path.join(tr.ISSUES, tag, "entrypoint.sh")
    lines = open(f).read().splitlines()
    i = next(k for k, l in enumerate(lines) if "git clone" in l and not l.strip().startswith("#"))
    j = next(k for k in range(i, len(lines)) if re.search(r'git checkout "\$commit_hash"', lines[k]))
    return "\n".join(l for l in lines[i:j + 1] if l.strip() and not l.strip().startswith("#"))


def entrypoint_trees(tag, image, dest):
    """Both versions as the entrypoint itself checks them out at run time: its clone lines run in the
    image once with BUGGY_COMMIT and once with FIXED_COMMIT, and the tracked files of each checkout are
    streamed out. The checkout's line endings are then the ones apply_patch patches. A checkout made
    outside the image converts some files differently (autogen_1844 and autogen_3361,
    dotnet/.tools/run_all_notebook.ps1), and a diff of the commits' stored contents has LF where the
    checkout has CRLF (dotnet/AutoGen.sln in autogen_4733, autogen_4785 and autogen_5007)."""
    info = json.loads(subprocess.run(["docker", "image", "inspect", image], capture_output=True, text=True).stdout)[0]
    env = dict(x.split("=", 1) for x in info["Config"].get("Env") or [])
    commits = {"buggy": env.get("BUGGY_COMMIT"), "fixed": env.get("FIXED_COMMIT")}
    if not all(commits.values()):
        raise RuntimeError(f"{tag}: no BUGGY_COMMIT or FIXED_COMMIT in the image")
    os.makedirs(dest, exist_ok=True)
    sh = "set -e\ngit config --global --add safe.directory '*'\n"
    for v, c in commits.items():
        sh += (f"(\nsource_dir=/tmp/{v}\ncommit_hash={c}\n{clone_lines(tag)}\ncd /tmp/{v}\n"
               f"git rev-parse HEAD > /out/{v}.head\n"
               f"git ls-files -z | tar --null --no-recursion -T - -cf /out/{v}.tar\n) > /out/{v}.log 2>&1\n")
    r = subprocess.run(["docker", "run", "--rm", "--entrypoint", "bash", "-v", f"{dest}:/out", image, "-c", sh],
                       capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"{tag}: entrypoint clone failed: {r.stderr[-300:]}")
    for v, c in commits.items():
        head = open(os.path.join(dest, f"{v}.head")).read().strip()
        if head != c:
            raise RuntimeError(f"{tag}: {v} checkout is {head}, wanted {c}")
        os.makedirs(os.path.join(dest, v))
        subprocess.run(["tar", "-xf", os.path.join(dest, f"{v}.tar"), "-C", os.path.join(dest, v)], check=True)
    return commits


def developer_patch(tag, image):
    path = os.path.join(tr.ISSUES, tag, "developer.patch")
    rec_path = os.path.join(tr.ISSUES, tag, "developer_patch.json")
    if os.path.exists(path):
        # newline="": no newline translation on reading, so every CR of the patch is kept
        return open(path, encoding="utf-8", errors="surrogateescape", newline="").read()
    tmp = tempfile.mkdtemp()
    try:
        if ENTRY[tag].get("fixed_tree") == "yes":
            # The image holds both versions. apply_patch patches /app/source_code_buggy, whose tracked
            # files are our copy (inputs.py tree_from_image).
            fixed = os.path.join(tmp, "fixed")
            source = fixed_tree(tag, image, fixed)
            buggy = os.path.join(tr.ISSUES, tag, "repo")
        else:
            commits = entrypoint_trees(tag, image, os.path.join(tmp, "entry"))
            fixed, buggy = os.path.join(tmp, "entry", "fixed"), os.path.join(tmp, "entry", "buggy")
            source = (f"the entrypoint's clone lines run in the image, buggy {commits['buggy']}, "
                      f"fixed {commits['fixed']}, git ls-files of each checkout")
        repo = os.path.join(tmp, "repo")
        # A link is copied as the link itself, never followed, so both trees are compared as git stores
        # them (ai_5628 and ai_6510 hold a README.md link whose target is not in the copy).
        shutil.copytree(buggy, repo, symlinks=True)
        g = ["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=false"]
        subprocess.run(g[:3] + ["init", "-q"], check=True)
        # No line-ending conversion: a repository's .gitattributes text rules (autogen, metagpt) would
        # store CRLF files as LF, and the patch would not apply to the image's CRLF files. info/attributes
        # outranks every .gitattributes, so git compares the files' own bytes.
        os.makedirs(os.path.join(repo, ".git", "info"), exist_ok=True)
        open(os.path.join(repo, ".git", "info", "attributes"), "w").write("* -text\n")
        subprocess.run(g + ["add", "-A"], check=True)
        subprocess.run(g + ["commit", "-q", "-m", "buggy"], check=True)
        for root, dirs, files in os.walk(repo):
            if ".git" in dirs:
                dirs.remove(".git")
            for d in [d for d in dirs if os.path.islink(os.path.join(root, d))]:
                os.remove(os.path.join(root, d))
                dirs.remove(d)
            for f in files:
                os.remove(os.path.join(root, f))
        for root, dirs, files in os.walk(fixed):
            for f in files + [d for d in dirs if os.path.islink(os.path.join(root, d))]:
                src = os.path.join(root, f)
                dst = os.path.join(repo, os.path.relpath(src, fixed))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                if os.path.islink(src):
                    os.symlink(os.readlink(src), dst)
                else:
                    shutil.copy2(src, dst)
        subprocess.run(g + ["add", "-A"], check=True)
        renames = ["--no-renames"] if tag in NO_RENAMES else []
        numstat = subprocess.run(g + ["diff", "--cached", "--numstat"] + renames, capture_output=True, text=True).stdout
        binary = [l.split("\t", 2)[2] for l in numstat.splitlines() if l.startswith("-\t-\t")]
        spec = ["--"] + ["."] + [f":(exclude){b}" for b in binary]
        # The diff is kept as git writes it, byte for byte: a changed text file that is not UTF-8
        # (metagpt_1313) passes through unchanged, carried in Python as surrogateescape text.
        raw = subprocess.run(g + ["diff", "--cached", "--src-prefix=a/", "--dst-prefix=b/"] + renames + spec,
                             capture_output=True, check=True).stdout
        open(path, "wb").write(raw)
        json.dump({"fixed_tree": source, "files_changed": len(numstat.splitlines()), "binary_left_out": binary,
                   "patch_bytes": len(raw)}, open(rec_path, "w"), indent=1)
        return raw.decode("utf-8", "surrogateescape")
    finally:
        shutil.rmtree(tmp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tags", nargs="*")
    # Each model is calibrated after its own repair run ends (fix plan departure 11, Jun "yes").
    ap.add_argument("--model", choices=tr.MODELS)
    a = ap.parse_args()
    models = [a.model] if a.model else tr.MODELS
    tags = a.tags or sorted(json.load(open(os.path.join(tr.INPUTS, "named_files.json"))))
    for tag in tags:
        evaluators = ["shipped"] + (["corrected"] if tag in tr.CORRECTIONS else [])
        plan = []
        for m in models:
            for ev in evaluators:
                for control in ("negative", "positive"):
                    for k in range(1, RUNS + 1):
                        plan.append((m, ev, control, k))
            for k in range(1, RUNS + 1):
                plan.append((m, "shipped", "diagnostic", k))
            # fix plan departure 15: the benchmark's own test_fixed, five runs, no pass rule
            for k in range(1, RUNS + 1):
                plan.append((m, "shipped", "fixed", k))
        todo = [p for p in plan if not os.path.exists(os.path.join(CHECK, p[0], tag, f"{p[1]}_{p[2]}_{p[3]}", "test_record.json"))]
        if not todo:
            print(tag, "calibration done before", flush=True)
            continue
        image = tr.image_of(tag)
        pulled = image.startswith("alfin06/")
        if pulled:
            subprocess.run(["docker", "pull", "-q", image], check=True, capture_output=True)
        try:
            dev = developer_patch(tag, image)
            for m, ev, control, k in todo:
                out = os.path.join(CHECK, m, tag, f"{ev}_{control}_{k}")
                extra = {"control": control, "run": k}
                if control == "diagnostic":
                    r = tr.run_eval(tag, image, m, out, ev, diagnostic=True, extra=extra)
                elif control == "fixed":
                    r = tr.run_eval(tag, image, m, out, ev, version="test_fixed", extra=extra)
                else:
                    r = tr.run_eval(tag, image, m, out, ev, patch_text=NULL_PATCH if control == "negative" else dev, extra=extra)
                print(tag, m, ev, control, k, f"exit {r['exit']}" if r["passed"] is None else "passed" if r["passed"] else f"failed exit {r['exit']}",
                      r["seconds"], "s", time.strftime("%H:%M:%S"), flush=True)
        finally:
            if pulled:
                subprocess.run(["docker", "rmi", "-f", image], capture_output=True)
                print(tag, "image removed", flush=True)


if __name__ == "__main__":
    main()
