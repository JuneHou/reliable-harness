"""Build SelfHeal's inputs for the 50 AgentIssue-Bench issues. No model call is made.

For each issue, one Docker image at a time:
  - the repository files at the buggy commit, as the files `git ls-files` lists,
      34 issues: taken from the image's /app/source_code_buggy,
      16 issues whose entrypoint clones at run time (agixt_1026, camel_88 and the 14 rebuilt for
      amd64): cloned on this machine from the URL in the entrypoint's clone line, at the image's
      BUGGY_COMMIT,
  - the test text, the image's /opt/reproduce.py or /opt/reproduce.js (images_amd64/<tag>/reproduce.py
    for the 14 rebuilt), and /opt/metadata.json when present,
  - the entrypoint script, for the record.
A pulled image is removed when its issue is done. The 14 rebuilt images stay for the tests.

Then the report of each issue (title and body of issues/<tag>.json, comments left out; crewai_1824
the spreadsheet title, Jun "Title only") is written to test_descriptions.csv, and the repository
files the report names are found by the rule of docs/selfheal_workflow.md section 8, in order of
appearance in the title and then the body (Jun "All, Agentless headers").

  python inputs.py [--tags TAG ...]
"""
import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = "/data/wang/junh/githubs/stochastic-harness/AgentIssue-Bench/SelfHeal"
INPUTS = os.path.join(ROOT, "inputs")
ISSUES = os.path.join(INPUTS, "issues")
AIB = "/data/wang/junh/githubs/AgentIssue-Bench"
ART = os.path.join(AIB, "motivation_experiment", "artifacts", "agentissue")
REBUILT = "/data/wang/junh/githubs/stochastic-harness/AgentIssue-Bench/images_amd64"
AD_INPUTS = "/data/wang/junh/githubs/stochastic-harness/AgentDefect/SelfHeal/inputs"
CREWAI_1824_TITLE = "Fail to build tiktoken while installing crewai"   # spreadsheet sheet "50 AgentIssue-Bench", row 31, column C
csv.field_size_limit(10**9)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def entries():
    return {e["tag"]: e for e in json.load(open(os.path.join(ART, "entrypoints.json")))}


def is_rebuilt(tag):
    return os.path.isdir(os.path.join(REBUILT, tag))


def image_of(tag):
    return f"agentissue-bench-amd64:{tag}" if is_rebuilt(tag) else f"alfin06/agentissue-bench:{tag}"


def docker_cp(cid, src, dst):
    return run(["docker", "cp", f"{cid}:{src}", dst]).returncode == 0


def tree_from_image(image, dest, rec):
    """Tracked files of /app/source_code_buggy, streamed out of a container as a tar."""
    sh = ("cd /app/source_code_buggy && if [ -d .git ]; then git config --global --add safe.directory '*'; "
          "git ls-files -z | tar --null --no-recursion -T - -cf - ; else echo NO_GIT >&2; exit 7; fi")
    os.makedirs(dest, exist_ok=True)
    p1 = subprocess.Popen(["docker", "run", "--rm", "--entrypoint", "sh", image, "-c", sh],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2 = subprocess.run(["tar", "-xf", "-", "-C", dest], stdin=p1.stdout, capture_output=True)
    err = p1.stderr.read().decode("utf-8", "replace")
    p1.wait()
    if p1.returncode == 0 and p2.returncode == 0:
        rec["tree_source"] = "image /app/source_code_buggy, git ls-files"
        rec["has_git"] = True
        return True
    rec["tree_stream_error"] = err.strip()[-500:]
    # No git in the image or no .git: copy the whole folder and keep every file.
    shutil.rmtree(dest, ignore_errors=True)
    cid = run(["docker", "create", image]).stdout.strip()
    try:
        tmp = tempfile.mkdtemp(dir=INPUTS)
        ok = docker_cp(cid, "/app/source_code_buggy", tmp)
        if not ok:
            raise RuntimeError(f"{image}: /app/source_code_buggy not found")
        src = os.path.join(tmp, "source_code_buggy")
        if os.path.isdir(os.path.join(src, ".git")):
            files = run(["git", "-c", "safe.directory=*", "-C", src, "ls-files", "-z"]).stdout.split("\0")
            rec["has_git"] = True
            rec["tree_source"] = "image /app/source_code_buggy (docker cp), git ls-files on this machine"
        else:
            files = [os.path.relpath(os.path.join(r, f), src) for r, _, fs in os.walk(src) for f in fs]
            rec["has_git"] = False
            rec["tree_source"] = "image /app/source_code_buggy (docker cp), no .git, every file kept"
        for f in filter(None, files):
            s = os.path.join(src, f)
            if os.path.isfile(s) and not os.path.islink(s):
                os.makedirs(os.path.dirname(os.path.join(dest, f)), exist_ok=True)
                shutil.copy2(s, os.path.join(dest, f))
        shutil.rmtree(tmp)
    finally:
        run(["docker", "rm", "-f", cid])
    return True


def tree_from_clone(entrypoint_text, commit, dest, rec):
    m = re.search(r'git clone[^\n]*?"?(https://github\.com/[^\s"]+?\.git)"?', entrypoint_text)
    if not m:
        raise RuntimeError("no clone URL in the entrypoint")
    url = m.group(1)
    tmp = tempfile.mkdtemp(dir=INPUTS)
    src = os.path.join(tmp, "repo")
    # The entrypoints fetch the one commit (git fetch --depth 1 origin "$commit_hash"); the same here.
    for cmd in (["git", "init", "--quiet", src], ["git", "-C", src, "remote", "add", "origin", url],
                ["git", "-C", src, "fetch", "--quiet", "--depth", "1", "origin", commit],
                ["git", "-C", src, "checkout", "--quiet", "FETCH_HEAD"]):
        r = run(cmd)
        if r.returncode != 0:
            raise RuntimeError(f"{' '.join(cmd[:4])} failed: {r.stderr[-300:]}")
    head = run(["git", "-C", src, "rev-parse", "HEAD"]).stdout.strip()
    if head != commit:
        raise RuntimeError(f"checked out {head}, wanted {commit}")
    files = run(["git", "-C", src, "ls-files", "-z"]).stdout.split("\0")
    for f in filter(None, files):
        s = os.path.join(src, f)
        if os.path.isfile(s) and not os.path.islink(s):
            os.makedirs(os.path.dirname(os.path.join(dest, f)), exist_ok=True)
            shutil.copy2(s, os.path.join(dest, f))
    shutil.rmtree(tmp)
    rec["tree_source"] = f"git clone {url}, checkout {commit}, git ls-files"
    rec["has_git"] = True
    rec["clone_url"], rec["commit"] = url, commit


def build_issue(tag, e):
    out = os.path.join(ISSUES, tag)
    if os.path.exists(os.path.join(out, "record.json")):
        return json.load(open(os.path.join(out, "record.json")))
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    image = image_of(tag)
    rec = {"tag": tag, "image": image, "rebuilt_amd64": is_rebuilt(tag)}
    pulled = False
    if not is_rebuilt(tag):
        r = run(["docker", "pull", "-q", image])
        if r.returncode != 0:
            raise RuntimeError(f"{tag}: pull failed {r.stderr[-300:]}")
        pulled = True
    try:
        info = json.loads(run(["docker", "image", "inspect", image]).stdout)[0]
        env = dict(x.split("=", 1) for x in info["Config"].get("Env") or [])
        rec["image_id"] = info["Id"]
        rec["repo_digests"] = info.get("RepoDigests")
        rec["buggy_commit_env"] = env.get("BUGGY_COMMIT")
        cid = run(["docker", "create", image]).stdout.strip()
        try:
            # entrypoint script
            if is_rebuilt(tag):
                shutil.copy(os.path.join(REBUILT, tag, "run_test_entrypoint.sh"), os.path.join(out, "entrypoint.sh"))
                rec["entrypoint_source"] = f"images_amd64/{tag}/run_test_entrypoint.sh"
            rec["usr_local_bin_entrypoint"] = docker_cp(cid, "/usr/local/bin/run_test_entrypoint.sh",
                                                         os.path.join(out, "entrypoint_usr_local_bin.sh"))
            rec["opt_entrypoint"] = docker_cp(cid, "/opt/run_test_entrypoint.sh", os.path.join(out, "entrypoint_opt.sh"))
            if not is_rebuilt(tag):
                for name in ("entrypoint_usr_local_bin.sh", "entrypoint_opt.sh"):
                    if os.path.exists(os.path.join(out, name)):
                        shutil.copy(os.path.join(out, name), os.path.join(out, "entrypoint.sh"))
                        rec["entrypoint_source"] = name
                        break
            # test text
            rec["test"] = None
            for ext in ("py", "js"):
                if docker_cp(cid, f"/opt/reproduce.{ext}", os.path.join(out, f"test.{ext}")):
                    rec["test"] = f"/opt/reproduce.{ext}"
                    break
            if is_rebuilt(tag):
                shutil.copy(os.path.join(REBUILT, tag, "reproduce.py"), os.path.join(out, "test.py"))
                rec["test"] = f"images_amd64/{tag}/reproduce.py"
            rec["metadata_json"] = docker_cp(cid, "/opt/metadata.json", os.path.join(out, "metadata.json"))
        finally:
            run(["docker", "rm", "-f", cid])
        if rec["test"] is None:
            raise RuntimeError(f"{tag}: no reproduction script")
        # repository files
        repo = os.path.join(out, "repo")
        if e.get("buggy_tree") == "yes":
            tree_from_image(image, repo, rec)
        else:
            commit = rec["buggy_commit_env"]
            if not commit:
                raise RuntimeError(f"{tag}: no BUGGY_COMMIT in the image")
            tree_from_clone(open(os.path.join(out, "entrypoint.sh")).read(), commit, repo, rec)
        files = sorted(os.path.relpath(os.path.join(r, f), repo) for r, _, fs in os.walk(repo) for f in fs)
        open(os.path.join(out, "files.txt"), "w").write("".join(f + "\n" for f in files))
        rec["n_files"] = len(files)
    finally:
        if pulled:
            run(["docker", "rmi", "-f", image])
            rec["image_removed"] = True
    json.dump(rec, open(os.path.join(out, "record.json"), "w"), indent=1)
    return rec


def report(tag):
    d = json.load(open(os.path.join(ART, "issues", f"{tag}.json")))
    if tag == "crewai_1824":
        return CREWAI_1824_TITLE, ""
    return d["title"], d.get("body") or ""


TOKEN = re.compile(r"[A-Za-z0-9_\-./\\~@+]*[A-Za-z0-9_\-~@+]\.[A-Za-z][A-Za-z0-9]*")


def named_files(text, files):
    """Repository files named in the text, in order of first appearance. A name is a path or a file
    name with an extension. It matches the repository file whose path parts agree with it for the
    longest run counted back from the file name, the run holding at least the file name. A name
    that matches no file, or ties between two files, is left out."""
    by_name = {}
    for f in files:
        by_name.setdefault(f.split("/")[-1], []).append(f.split("/"))
    out = []
    for tok in TOKEN.findall(text):
        parts = [p for p in re.split(r"[/\\]+", tok) if p and p not in (".", "..")]
        if not parts or parts[-1] not in by_name:
            continue
        best, who = 0, []
        for fp in by_name[parts[-1]]:
            n = 0
            while n < min(len(fp), len(parts)) and fp[-1 - n] == parts[-1 - n]:
                n += 1
            if n > best:
                best, who = n, [fp]
            elif n == best:
                who.append(fp)
        if best >= 1 and len(who) == 1:
            path = "/".join(who[0])
            if path not in out:
                out.append(path)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tags", nargs="*")
    a = ap.parse_args()
    os.makedirs(ISSUES, exist_ok=True)
    for f in ("fix-pattern.csv", "train_descriptions.csv"):
        shutil.copy(os.path.join(AD_INPUTS, f), os.path.join(INPUTS, f))
    es = entries()
    tags = sorted(es) if not a.tags else a.tags
    for tag in tags:
        rec = build_issue(tag, es[tag])
        print(tag, rec.get("tree_source"), rec.get("n_files"), rec.get("test"), flush=True)
    # reports and named files, over all 50 once every tree exists
    if all(os.path.exists(os.path.join(ISSUES, t, "record.json")) for t in es):
        rows, named = [], {}
        for tag in sorted(es):
            title, body = report(tag)
            rows.append({"id": tag, "title": title, "body": body})
            files = open(os.path.join(ISSUES, tag, "files.txt")).read().split("\n")
            named[tag] = named_files(title + "\n" + body, [f for f in files if f])
        with open(os.path.join(INPUTS, "test_descriptions.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["id", "title", "body"])
            w.writeheader()
            w.writerows(rows)
        json.dump(named, open(os.path.join(INPUTS, "named_files.json"), "w"), indent=1)
        print("issues", len(rows), "| name at least one file", sum(bool(v) for v in named.values()),
              "| need picking", sum(not v for v in named.values()))


if __name__ == "__main__":
    main()
