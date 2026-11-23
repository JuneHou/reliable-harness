import os
import platform
import subprocess
from typing import Any

from pydantic import BaseModel

from minisweagent.exceptions import Submitted
from minisweagent.utils.serialize import recursive_merge


class LocalEnvironmentConfig(BaseModel):
    cwd: str = ""
    env: dict[str, str] = {}
    timeout: int = 30


def _sandboxed(command: str, cwd: str) -> tuple[list[str], str] | None:
    """stochastic-harness plan departure 4 (e): when the driver sets HF_SANDBOX_DIR (the rerun's HarnessFix copy)
    and HF_SANDBOX_TMP, the command runs in a bubblewrap sandbox that shows only the system folders, the Python
    interpreters, HarnessFix's venv and mini-swe-agent source (read only), the rerun's copy (read and write) and
    a private /tmp, with no network. Every other file on the machine (the datasets, the reference fixes, the
    tests, other methods and reruns, the home folder) does not exist inside it."""
    copy = os.environ.get("HF_SANDBOX_DIR")
    tmp = os.environ.get("HF_SANDBOX_TMP")
    if not copy or not tmp:
        return None
    os.makedirs(tmp, exist_ok=True)
    venv = os.path.realpath(os.path.join(copy, ".venv"))
    mswea = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    args = ["bwrap", "--die-with-parent", "--new-session", "--unshare-net", "--unshare-ipc",
            "--ro-bind", "/usr", "/usr", "--ro-bind", "/etc", "/etc", "--proc", "/proc", "--dev", "/dev"]
    for name in ("bin", "lib", "lib32", "lib64", "libx32", "sbin"):
        if os.path.islink("/" + name):
            args += ["--symlink", os.readlink("/" + name), "/" + name]
    for ro in ("/data/wang/junh/python", venv, os.path.dirname(mswea)):
        args += ["--ro-bind", ro, ro]
    args += ["--bind", copy, copy, "--bind", tmp, "/tmp", "--setenv", "HOME", "/tmp"]
    inside = cwd if os.path.realpath(cwd).startswith(os.path.realpath(copy)) else copy
    return args + ["--chdir", inside, "/bin/bash", "-c", command], inside


class LocalEnvironment:
    def __init__(self, *, config_class: type = LocalEnvironmentConfig, **kwargs):
        """This class executes bash commands directly on the local machine."""
        self.config = config_class(**kwargs)

    def execute(self, action: dict, cwd: str = "", *, timeout: int | None = None) -> dict[str, Any]:
        """Execute a command in the local environment and return the result as a dict."""
        command = action.get("command", "")
        cwd = cwd or self.config.cwd or os.getcwd()
        boxed = _sandboxed(command, cwd)
        try:
            result = subprocess.run(
                boxed[0] if boxed else command,
                shell=not boxed,
                # stochastic-harness plan departure 5: the class runs bash commands (docstring above, and every
                # agent prompt asks for bash), and /bin/sh is dash on this server
                executable=None if boxed else "/bin/bash",
                text=True,
                cwd=cwd,
                env=os.environ | self.config.env,
                timeout=timeout or self.config.timeout,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            output = {"output": result.stdout, "returncode": result.returncode, "exception_info": ""}
        except Exception as e:
            raw_output = getattr(e, "output", None)
            raw_output = (
                raw_output.decode("utf-8", errors="replace") if isinstance(raw_output, bytes) else (raw_output or "")
            )
            output = {
                "output": raw_output,
                "returncode": -1,
                "exception_info": f"An error occurred while executing the command: {e}",
                "extra": {"exception_type": type(e).__name__, "exception": str(e)},
            }
        self._check_finished(output)
        return output

    def _check_finished(self, output: dict):
        """Raises Submitted if the output indicates task completion."""
        lines = output.get("output", "").lstrip().splitlines(keepends=True)
        if lines and lines[0].strip() == "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT" and output["returncode"] == 0:
            submission = "".join(lines[1:])
            raise Submitted(
                {
                    "role": "exit",
                    "content": submission,
                    "extra": {"exit_status": "Submitted", "submission": submission},
                }
            )

    def get_template_vars(self, **kwargs) -> dict[str, Any]:
        return recursive_merge(self.config.model_dump(), platform.uname()._asdict(), os.environ, kwargs)

    def serialize(self) -> dict:
        return {
            "info": {
                "config": {
                    "environment": self.config.model_dump(mode="json"),
                    "environment_type": f"{self.__class__.__module__}.{self.__class__.__name__}",
                }
            }
        }
