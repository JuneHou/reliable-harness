"""Build the developer patch again for the 16 issues whose entrypoint clones at run time, from the two
checkouts the entrypoint's own clone lines make in the image (calibrate.entrypoint_trees), and compare it
with the patch the calibration used (fix plan departure 4, Jun "yes" to building the developer patches as
the diff of the two commits).

The earlier patch diffed our checkout of FIXED_COMMIT, made outside the image, against our buggy copy. For
autogen_1844 and autogen_3361 that checkout converted dotnet/.tools/run_all_notebook.ps1 to CRLF, a file
the two commits leave unchanged, and the entrypoint's own checkout already holds it with CRLF, so the
hunk was reversed and apply_patch stopped.

A patch whose bytes are unchanged keeps its records. A changed patch is moved to
inputs/issues/<tag>/_replaced/developer.patch with its record, and the positive-control records it
produced are moved to case_check/<model>/_replaced_developer_patch/<tag>/, never deleted. One image at a
time, a pulled image removed after use. Writes ../developer_patch_rebuild.json.

  python rebuild_clone_patches.py
"""
import glob
import hashlib
import json
import os
import shutil
import subprocess

import calibrate as cal
import test_repairs as tr

REPORT = os.path.join(tr.ROOT, "developer_patch_rebuild.json")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    report = json.load(open(REPORT)) if os.path.exists(REPORT) else {}
    tags = [t for t in sorted(cal.ENTRY) if cal.ENTRY[t].get("fixed_tree") != "yes"
            and os.path.isdir(os.path.join(tr.ISSUES, t))]
    for tag in tags:
        if tag in report:
            print(tag, "rebuilt before", flush=True)
            continue
        path = os.path.join(tr.ISSUES, tag, "developer.patch")
        rec = os.path.join(tr.ISSUES, tag, "developer_patch.json")
        side = os.path.join(tr.ISSUES, tag, "_replaced")
        os.makedirs(side, exist_ok=True)
        if not os.path.exists(os.path.join(side, "developer.patch")):
            shutil.move(path, os.path.join(side, "developer.patch"))
            shutil.move(rec, os.path.join(side, "developer_patch.json"))
        old = open(os.path.join(side, "developer.patch"), "rb").read()
        image = tr.image_of(tag)
        pulled = image.startswith("alfin06/")
        if pulled:
            subprocess.run(["docker", "pull", "-q", image], check=True, capture_output=True)
        try:
            cal.developer_patch(tag, image)
        finally:
            if pulled:
                subprocess.run(["docker", "rmi", "-f", image], capture_output=True)
        new = open(path, "rb").read()
        moved = []
        if new == old:
            # unchanged: the earlier patch and its record stay where they were
            os.remove(path)
            os.remove(rec)
            shutil.move(os.path.join(side, "developer.patch"), path)
            shutil.move(os.path.join(side, "developer_patch.json"), rec)
            os.rmdir(side)
        else:
            for m in tr.MODELS:
                for d in sorted(glob.glob(os.path.join(cal.CHECK, m, tag, "*_positive_*"))):
                    dst = os.path.join(cal.CHECK, m, "_replaced_developer_patch", tag)
                    os.makedirs(dst, exist_ok=True)
                    shutil.move(d, os.path.join(dst, os.path.basename(d)))
                    moved.append(f"{m}/{os.path.basename(d)}")
        report[tag] = {"identical": new == old, "old_bytes": len(old), "old_sha256": sha(old),
                       "new_bytes": len(new), "new_sha256": sha(new),
                       "source": json.load(open(rec))["fixed_tree"] if new != old else "unchanged",
                       "positive_records_moved": moved}
        print(tag, "identical" if new == old else f"changed, {len(moved)} positive records moved", flush=True)
        json.dump(report, open(REPORT, "w"), indent=1)


if __name__ == "__main__":
    main()
