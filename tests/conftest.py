"""Shared fixtures for the one-line installer tests.

Everything here runs offline, as an ordinary user, and without dpkg touching
the host. The scripts resolve versions and reach apt only after their input and
prerequisite checks, so those guards can be exercised with neither the network
nor a package manager — which also means these tests say nothing about the DKMS
driver install itself, which needs real kernel headers.
"""
import os
import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def stub_bin(tmp_path):
    """Build a directory of stub executables to put in front of PATH.

    Used to make a test deterministic regardless of the host: to hide a command
    the script probes for, or to make `id -u` report a non-root user even when
    the suite runs as root in CI.
    """
    bindir = tmp_path / "stubbin"
    bindir.mkdir()

    def add(name: str, body: str = "exit 0"):
        p = bindir / name
        p.write_text(f"#!/bin/sh\n{body}\n")
        p.chmod(0o755)
        return p

    add.dir = bindir
    return add


@pytest.fixture
def run_script(tmp_path, stub_bin):
    """Run one of the repo's scripts with a throwaway HOME and optional stubs.

    hide=[...] removes a command from PATH by shadowing the whole PATH with a
    minimal one, which is how the "this needs Debian/Ubuntu" guards are tested.
    """
    def _run(script: str, env=None, hide=(), isolate_path=False, timeout=60):
        home = tmp_path / "home"
        home.mkdir(exist_ok=True)

        if isolate_path or hide:
            # A minimal PATH built from real tool locations, minus anything in
            # `hide`. Symlinking keeps the stub dir first so overrides still win.
            realbin = tmp_path / "realbin"
            realbin.mkdir(exist_ok=True)
            for tool in ("sh", "env", "mkdir", "rm", "rmdir", "readlink", "printf",
                         "id", "sudo", "curl", "python3", "dpkg", "dpkg-query",
                         "apt-get", "sha256sum", "uname", "mktemp", "grep", "sed"):
                if tool in hide:
                    continue
                found = subprocess.run(["which", tool], capture_output=True, text=True).stdout.strip()
                if found and not (realbin / tool).exists():
                    (realbin / tool).symlink_to(found)
            path = f"{stub_bin.dir}:{realbin}"
        else:
            path = f"{stub_bin.dir}:{os.environ['PATH']}"

        full_env = {"HOME": str(home), "PATH": path}
        full_env.update(env or {})
        return subprocess.run(
            ["sh", str(REPO_ROOT / script)],
            capture_output=True, text=True, env=full_env, timeout=timeout,
        )

    _run.home = tmp_path / "home"
    return _run


def top_level_statements(script_path: Path):
    """Lines that execute when the file is sourced, i.e. outside any function.

    A `curl | sh` installer must do nothing until the final `main "$@"`, so a
    truncated download cannot half-apply. This is how that is checked.
    """
    func_def = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\s*\(\)\s*\{")
    out, depth = [], 0
    for raw in script_path.read_text().splitlines():
        line = raw.strip()
        depth_before = depth
        depth += raw.count("{") - raw.count("}")
        if depth_before != 0:
            continue                      # inside a function body
        if not line or line.startswith("#"):
            continue
        if func_def.match(line):
            continue                      # a definition, one-line or opening a block
        out.append(line)
    return out
