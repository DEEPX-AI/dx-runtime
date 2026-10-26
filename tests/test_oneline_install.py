"""Guards on oneline-install.sh that must hold without network, root or an NPU."""
import subprocess

import pytest

from conftest import top_level_statements

SCRIPT = "oneline-install.sh"


def test_syntax_is_valid_posix_sh(repo_root):
    assert subprocess.run(["sh", "-n", repo_root / SCRIPT]).returncode == 0


def test_runs_under_plain_sh(repo_root):
    assert (repo_root / SCRIPT).read_text().startswith("#!/bin/sh\n")


def test_aborts_on_error_and_unset(repo_root):
    assert "set -eu" in (repo_root / SCRIPT).read_text()


def test_nothing_executes_before_the_final_main_call(repo_root):
    """A truncated `curl | sh` download must not half-apply."""
    stmts = top_level_statements(repo_root / SCRIPT)
    assert stmts[-1] == 'main "$@"'
    for s in stmts[:-1]:
        assert s == "set -eu" or "=" in s.split()[0], f"would run on a truncated download: {s}"


@pytest.mark.parametrize("var", ["DX_RT_VERSION", "DX_DRIVER_VERSION", "DX_FW_VERSION"])
@pytest.mark.parametrize("value", [
    "../../../evil",     # traversal: curl normalises dot-segments client-side
    "/etc/passwd",       # absolute path
    "3.4.2;rm -rf /",    # shell metacharacters
    "3.4.2 extra",       # whitespace
])
def test_rejects_unsafe_version_override(run_script, var, value):
    """Versions are spliced into download URLs, so an override is validated too.

    The check deliberately sits outside the resolver, so it cannot be skipped by
    supplying the value instead of letting the script look it up.
    """
    r = run_script(SCRIPT, env={var: value})
    assert r.returncode != 0
    assert "invalid" in r.stderr and "version" in r.stderr


def test_requires_debian_or_ubuntu(run_script):
    r = run_script(SCRIPT, hide=["dpkg"])
    assert r.returncode != 0
    assert "dpkg" in r.stderr


def test_tells_an_unprivileged_user_it_needs_root(run_script, stub_bin):
    """`id` is stubbed so this holds even when the suite runs as root in CI."""
    stub_bin("id", "echo 1000")
    r = run_script(SCRIPT, hide=["sudo"])
    assert r.returncode != 0
    assert "root" in r.stderr
