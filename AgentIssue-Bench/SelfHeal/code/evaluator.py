"""Build the corrected evaluator of the fix plan, departure 5 (Jun "Yes, this solution").

For the 15 AgentIssue-Bench issues whose test cannot pass any patch as shipped, the corrected
test_patched runs the issue's own fixed-version check on the patched code in /app/source_code_buggy.
Each corrected file is the image's own file (inputs/issues/<tag>/test.* or entrypoint.sh, copied from
the image) with exact string edits, written to AgentIssue-Bench/SelfHeal/evaluator/<tag>/ beside a
unified diff against the original. The file's own line endings are kept. evaluator/corrections.json
says, per issue, which corrected file is mounted where in the container, whether
/app/source_code_patched is linked to /app/source_code_buggy after apply_patch, which entrypoint the
command calls, and which extra success messages count. The shipped evaluator is used unchanged
for every issue in a separate pass, so both results are kept.

  python evaluator.py
"""
import difflib
import json
import os

ROOT = "/data/wang/junh/githubs/stochastic-harness/AgentIssue-Bench/SelfHeal"
ISSUES = os.path.join(ROOT, "inputs", "issues")
OUT = os.path.join(ROOT, "evaluator")

LINK_PATCHED = ["agixt_1030", "agixt_1369", "camel_88", "autogen_4197", "camel_1614", "metagpt_1313"]
OPT_ENTRY = ["pythagora_55", "superagent_953"]
FIX_VERIFIED = ["ai_4411", "ai_4619", "ai_5628", "ai_6510"]
# Departure 13: the entrypoint reads every *.patch in /patches/<tag>/ (PATCH_DIR, line 11 of autogen_1174 and
# line 9 of autogen_4382) and ignores the path it is given, while eval_patches.py mounts the patch folder at
# /patches. The corrected evaluator mounts it at /patches/<tag>.
PATCH_MOUNT = ["autogen_1174", "autogen_4382"]
# Departure 13, Jun "Install GNU patch": these ten images (Debian 12 or 13) have no patch program, so the
# entrypoint's own "patch -p1" stops. ai_6510 is the tenth, found when its images were read: its
# entrypoint stopped at the "local" line before reaching patch. GNU patch is installed from Debian's
# packages in the test container before apply_patch, and its version is printed. apt-get's own output
# goes to a file in the container.
NO_PATCH = ["agixt_1369", "ai_4411", "ai_4619", "ai_5628", "ai_6510",
            "evoninja_504", "evoninja_515", "evoninja_525", "evoninja_594", "evoninja_652"]
INSTALL_PATCH = ("(apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y patch) > /tmp/install_patch.log 2>&1"
                 " && patch --version | head -1")

ARGV_PY = ('if version not in ["buggy", "fixed"]:', 'if version not in ["buggy", "fixed", "patched"]:')
ARGV_PY2 = ('if version_arg not in ["buggy", "fixed"]:', 'if version_arg not in ["buggy", "fixed", "patched"]:')

# (tag, source file in inputs/issues/<tag>, path in the container, [(old, new, count)])
EDITS = [
    ("crewai_1532", "test.py", "/opt/reproduce.py", [ARGV_PY + (1,)]),
    ("haystack_9523", "test.py", "/opt/reproduce.py", [ARGV_PY2 + (1,)]),
    ("haystack_8912", "test.py", "/opt/reproduce.py", [
        ARGV_PY2 + (1,),
        ("            else:  # fixed\n                if has_additional_properties:",
         "            else:  # fixed\n                if not has_additional_properties:", 1)]),
    ("ai_4619", "entrypoint_usr_local_bin.sh", "/usr/local/bin/run_test_entrypoint.sh", [
        ('            if [ "${version}" == "fixed" ]; then\n                echo "✅ FIX VERIFIED',
         '            if [ "${version}" == "fixed" ] || [ "${version}" == "patched" ]; then\n                echo "✅ FIX VERIFIED', 1),
        ('            if [ "${version}" == "buggy" ] || [ "${version}" == "patched" ]; then\n                echo "✅ BUG REPRODUCED',
         '            if [ "${version}" == "buggy" ]; then\n                echo "✅ BUG REPRODUCED', 1)]),
    ("ai_5628", "test.js", "/opt/reproduce.js", [
        ("const isBuggyVersion = version === 'buggy' || version === 'patched';",
         "const isBuggyVersion = version === 'buggy';", 1)]),
    ("ai_6510", "test.js", "/opt/reproduce.js", [
        ("const isBuggyVersion = version === 'buggy' || version === 'patched';",
         "const isBuggyVersion = version === 'buggy';", 1),
        ("const entry = getEntryPoint(isBuggyVersion);",
         "const entry = getEntryPoint(version !== 'fixed');", 1)]),
    ("ai_6510", "entrypoint_usr_local_bin.sh", "/usr/local/bin/run_test_entrypoint.sh", [
        ('            echo "--- Test script executed successfully (exit code 0) ---"\n        else\n            echo "--- Test script failed (exit code $?) ---"\n        fi',
         '            echo "--- Test script executed successfully (exit code 0) ---"\n            exit 0\n        else\n            echo "--- Test script failed (exit code $?) ---"\n            exit 1\n        fi', 3),
        # departure 13: "local" outside a function stops the apply_patch case under set -e
        ('        local source_dir="/app/source_code_buggy"\n        cd "${source_dir}"\n        patch -p1 < "$2"',
         '        source_dir="/app/source_code_buggy"\n        cd "${source_dir}"\n        patch -p1 < "$2"', 1)]),
    # Departure 13: apply_patch reinstalls with "pip install --no-deps -e ." at a repository root that has no
    # setup.py or pyproject.toml. The correction repeats the install the entrypoint's own test_version runs
    # for the buggy code, or none where test_version installs nothing from the source.
    ("autogen_4733", "entrypoint_usr_local_bin.sh", "/usr/local/bin/run_test_entrypoint.sh", [
        ("    pip install --no-deps -e .\n", "    pip install python/packages/autogen-core/.\n", 1)]),
    ("autogen_4785", "entrypoint_usr_local_bin.sh", "/usr/local/bin/run_test_entrypoint.sh", [
        ("    pip install --no-deps -e .\n",
         "    pip install python/packages/autogen-ext/.\n    pip install python/packages/autogen-core/.\n", 1)]),
    ("autogen_5007", "entrypoint_usr_local_bin.sh", "/usr/local/bin/run_test_entrypoint.sh", [
        ("    pip install --no-deps -e .\n", "", 1),
        # Departure 13, Jun "2. yes": test.py reads the relative path python/packages/autogen-studio/, and
        # test_patched runs it from /app, while the entrypoint's own buggy and fixed path first runs
        # cd "$source_dir" (line 66).
        ('    python "${REPRO_SCRIPT_PY}" "patched"\n',
         '    cd "$source_dir"\n    python "${REPRO_SCRIPT_PY}" "patched"\n', 1)]),
    # Departure 13, Jun "1. tes": test_version installs autogen-agentchat and autogen-ext 0.4.0.dev6 from PyPI
    # (lines 51 and 52) and nothing from the source (its editable install is commented out, line 55).
    ("autogen_4197", "entrypoint_usr_local_bin.sh", "/usr/local/bin/run_test_entrypoint.sh", [
        ("    pip install --no-deps -e .\n", "", 1)]),
    ("chatdev_413", "entrypoint_usr_local_bin.sh", "/usr/local/bin/run_test_entrypoint.sh", [
        ("    pip install --no-deps -e .\n", "", 1)]),
    ("chatdev_465", "entrypoint_usr_local_bin.sh", "/usr/local/bin/run_test_entrypoint.sh", [
        ("    pip install --no-deps -e .\n", "", 1)]),
    # Departure 13, Jun "yes apply the same fix": the reinstall stops on a numpy version conflict, and
    # test_version installs nothing from the source (its editable install is commented out, line 52).
    ("autogen_1844", "entrypoint_usr_local_bin.sh", "/usr/local/bin/run_test_entrypoint.sh", [
        ("    pip install --no-deps -e .\n", "", 1)]),
    ("autogen_3361", "entrypoint_usr_local_bin.sh", "/usr/local/bin/run_test_entrypoint.sh", [
        ("    pip install --no-deps -e .\n", "", 1)]),
    # Departure 13: the script's patched branch prints "PATCH VERIFIED" (test.py line 15), and the
    # entrypoint counts only "FIX CONFIRMED" for a version other than buggy.
    ("gpt-engineer_1197", "entrypoint_usr_local_bin.sh", "/usr/local/bin/run_test_entrypoint.sh", [
        ('elif grep -q "FIX CONFIRMED" /tmp/test_output.log && [ "$version" != "buggy" ]; then',
         'elif grep -qE "FIX CONFIRMED|PATCH VERIFIED" /tmp/test_output.log && [ "$version" != "buggy" ]; then', 2)]),
    ("ai_4411", "test.js", "/opt/reproduce.js", [
        ("    if (cityPropertySchema === undefined) {",
         "    if (version === 'patched') {\n"
         "        if (cityPropertySchema !== undefined && 'description' in cityPropertySchema) {\n"
         "            console.log(\"\\n✅ FIX VERIFIED: Optional parameter description is preserved in the patched version.\");\n"
         "            process.exit(0);\n"
         "        }\n"
         "        console.log(\"\\n❌ FIX NOT VERIFIED: Optional parameter description is lost in the patched version.\");\n"
         "        process.exit(1);\n"
         "    }\n"
         "    if (cityPropertySchema === undefined) {", 1)]),
    ("ai_4411", "entrypoint_usr_local_bin.sh", "/usr/local/bin/run_test_entrypoint.sh", [
        ('            if [ "${version}" == "buggy" ] || [ "${version}" == "patched" ]; then\n                echo "✅ BUG REPRODUCED',
         '            if [ "${version}" == "buggy" ]; then\n                echo "✅ BUG REPRODUCED', 1),
        ('            if [ "${version}" == "buggy" ] || [ "${version}" == "patched" ]; then\n                echo "❌ BUG NOT REPRODUCED',
         '            if [ "${version}" == "buggy" ]; then\n                echo "❌ BUG NOT REPRODUCED', 1),
        # Departure 13, Jun "2": npm cannot install the repository's pnpm workspace ("workspace:*"), and
        # test_buggy installs nothing, so apply_patch's reinstall is dropped.
        ("            npm install\n            npm run build\n", "", 1)]),
    ("ai_5628", "entrypoint_usr_local_bin.sh", "/usr/local/bin/run_test_entrypoint.sh", [
        ("        npm install\n", "", 1)]),
]


def put(path, data):
    if os.path.exists(path) and open(path, "rb").read() == data:
        return
    open(path, "wb").write(data)


def main():
    os.makedirs(OUT, exist_ok=True)
    corr = {}
    for tag in LINK_PATCHED:
        corr.setdefault(tag, {})["link_patched"] = True
    for tag in OPT_ENTRY:
        corr.setdefault(tag, {})["entry"] = "/opt/run_test_entrypoint.sh"
    for tag in FIX_VERIFIED:
        corr.setdefault(tag, {})["extra_success"] = ["FIX VERIFIED"]
    for tag in PATCH_MOUNT:
        corr.setdefault(tag, {})["patch_mount"] = f"/patches/{tag}"
    for tag in NO_PATCH:
        corr.setdefault(tag, {})["pre"] = INSTALL_PATCH
    for tag, src, target, edits in EDITS:
        raw = open(os.path.join(ISSUES, tag, src), "rb").read().decode("utf-8")
        crlf = "\r\n" in raw
        text = raw.replace("\r\n", "\n")
        new = text
        for old, rep, count in edits:
            n = new.count(old)
            if n != count:
                raise SystemExit(f"{tag} {src}: expected {count} of {old[:60]!r}, found {n}")
            new = new.replace(old, rep)
        d = os.path.join(OUT, tag)
        os.makedirs(d, exist_ok=True)
        name = os.path.basename(target)
        # A file whose bytes are unchanged is not rewritten, so a test container that has it mounted
        # never reads a file in the middle of being written.
        put(os.path.join(d, name), (new.replace("\n", "\r\n") if crlf else new).encode("utf-8"))
        if name.endswith(".sh"):   # a mounted entrypoint is executed, as the image's own one is
            os.chmod(os.path.join(d, name), 0o755)
        diff ="".join(difflib.unified_diff(text.splitlines(True), new.splitlines(True),
                                            fromfile=f"image {target}", tofile=f"corrected {target}"))
        put(os.path.join(d, name + ".diff"), diff.encode("utf-8"))
        corr.setdefault(tag, {}).setdefault("mounts", []).append(
            {"host": os.path.join(d, name), "container": target, "crlf": crlf})
    json.dump(corr, open(os.path.join(OUT, "corrections.json"), "w"), indent=1)
    print(len(corr), "issues with a correction:", sorted(corr))


if __name__ == "__main__":
    main()
