"""Remove the calibration records that two of our bugs produced, so that calibrate.py runs them again
(Jun "ok. please fix it").

  1. The developer patch lost the CR of CRLF lines in two ways: it was read from git in text mode, and a
     repository's .gitattributes text rules made git store CRLF files as LF. Either way the patch failed
     on the image's CRLF files ("different line endings"). Every developer patch built before both fixes is
     built again with the fixed calibrate.developer_patch. A patch whose new bytes equal the old ones
     keeps its records. A patch whose bytes differ has its positive-control records deleted (shipped and
     corrected), since only the positive control applies the developer patch. The old patch file is
     deleted after its size and SHA-256 are written to the report.
  2. The corrected entrypoints of ai_4411, ai_4619 and ai_6510 were mounted without execute permission.
     ai_4411 and ai_4619 ran before the mode was fixed, so their corrected-evaluator records are deleted.
     ai_6510 ran after it and is kept.
One image at a time, a pulled image removed after use. Writes ../calibration_fix_report.json.

  python fix_calibration.py --model gpt-oss-120b
"""
import argparse
import glob
import hashlib
import json
import os
import shutil
import subprocess
import time

import calibrate as cal
import test_repairs as tr

# calibrate.py with both fixes: the patch read byte for byte, and no line-ending conversion by a
# repository's .gitattributes (info/attributes "* -text"). Every patch built before this is built again
# and compared with the patch its records used.
FIX_TIME = time.mktime(time.strptime("2026-11-11 21:08:41", "%Y-%m-%d %H:%M:%S"))
PERMISSION_BUG = ["ai_4411", "ai_4619"]
REPORT = os.path.join(tr.ROOT, "calibration_fix_report.json")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=tr.MODELS)
    a = ap.parse_args()
    out = os.path.join(cal.CHECK, a.model)
    report = {"model": a.model, "patches": {}, "deleted_for_permission_bug": {}}
    if os.path.exists(REPORT):   # an earlier pass of this script, stopped to add the second fix
        report["earlier_pass"] = json.load(open(REPORT))
    for tag in sorted(json.load(open(os.path.join(tr.INPUTS, "named_files.json")))):
        path = os.path.join(tr.ISSUES, tag, "developer.patch")
        rec = os.path.join(tr.ISSUES, tag, "developer_patch.json")
        if os.path.exists(path + ".old"):   # a pass stopped half way through this issue
            for p in (path, rec):
                if os.path.exists(p):
                    os.remove(p)
                os.rename(p + ".old", p)
        if not os.path.exists(path) or os.path.getmtime(rec) >= FIX_TIME:
            continue
        old = open(path, "rb").read()
        image = tr.image_of(tag)
        pulled = image.startswith("alfin06/")
        if pulled:
            subprocess.run(["docker", "pull", "-q", image], check=True, capture_output=True)
        try:
            os.rename(path, path + ".old")
            os.rename(rec, rec + ".old")
            cal.developer_patch(tag, image)
            new = open(path, "rb").read()
        finally:
            if pulled:
                subprocess.run(["docker", "rmi", "-f", image], capture_output=True)
        same = new == old
        deleted = []
        if not same:
            for d in sorted(glob.glob(os.path.join(out, tag, "*_positive_*"))):
                shutil.rmtree(d)
                deleted.append(os.path.basename(d))
        report["patches"][tag] = {"old_bytes": len(old), "old_sha256": sha(old), "new_bytes": len(new),
                                  "new_sha256": sha(new), "identical": same,
                                  "old_cr_bytes": old.count(b"\r"), "new_cr_bytes": new.count(b"\r"),
                                  "records_deleted": deleted}
        os.remove(path + ".old")
        os.remove(rec + ".old")
        print(tag, "identical" if same else f"changed, {len(deleted)} positive records deleted", flush=True)
        json.dump(report, open(REPORT, "w"), indent=1)
    for tag in PERMISSION_BUG:
        deleted = []
        for d in sorted(glob.glob(os.path.join(out, tag, "corrected_*"))):
            if os.path.isdir(d):
                shutil.rmtree(d)
                deleted.append(os.path.basename(d))
        report["deleted_for_permission_bug"][tag] = deleted
        print(tag, len(deleted), "corrected records deleted (permission bug)", flush=True)
    json.dump(report, open(REPORT, "w"), indent=1)


if __name__ == "__main__":
    main()
