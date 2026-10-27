import os
import stat
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BOOTSTRAP = REPO_ROOT / "scripts" / "lib" / "node-bootstrap.sh"


def _write_node(path: Path, version: str) -> None:
    path.write_text(f"#!/bin/sh\nprintf '%s\\n' '{version}'\n", encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _run_bootstrap(tmp_path: Path, version: str) -> subprocess.CompletedProcess[str]:
    bin_dir = tmp_path / version / "bin"
    bin_dir.mkdir(parents=True)
    _write_node(bin_dir / "node", version)
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "HERMES_HOME": str(tmp_path / "hermes"),
    }
    return subprocess.run(
        ["bash", "-c", f"source {BOOTSTRAP}; _nb_have_modern_node"],
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_node_bootstrap_rejects_vulnerable_node_versions(tmp_path):
    assert _run_bootstrap(tmp_path, "v20.19.6").returncode == 1
    assert _run_bootstrap(tmp_path, "v22.23.3").returncode == 1


def test_node_bootstrap_accepts_safe_node_versions(tmp_path):
    assert _run_bootstrap(tmp_path, "v22.23.4").returncode == 0
    assert _run_bootstrap(tmp_path, "v24.22.1").returncode == 0
