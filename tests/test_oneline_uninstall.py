"""Guards on oneline-uninstall.sh.

dpkg is stubbed throughout: these tests check which packages the script decides
to act on and what it tells the user, never that apt actually removes anything.
Removing a real package is covered by the container run recorded in the commit,
not here.
"""
import subprocess

from conftest import top_level_statements

SCRIPT = "oneline-uninstall.sh"

PACKAGES = ["dxrt-driver-dkms", "libdxrt-bin", "libdxrt"]


def test_syntax_is_valid_posix_sh(repo_root):
    assert subprocess.run(["sh", "-n", repo_root / SCRIPT]).returncode == 0


def test_nothing_executes_before_the_final_main_call(repo_root):
    stmts = top_level_statements(repo_root / SCRIPT)
    assert stmts[-1] == 'main "$@"'
    for s in stmts[:-1]:
        assert s == "set -eu" or "=" in s.split()[0], f"would run on a truncated download: {s}"


def test_targets_exactly_the_packages_the_installer_creates(repo_root):
    """Keeps the two scripts from drifting apart."""
    text = (repo_root / SCRIPT).read_text()
    for pkg in PACKAGES:
        assert pkg in text


def test_reports_when_no_package_is_installed(run_script, stub_bin):
    stub_bin("sudo", 'exec "$@"')
    stub_bin("dpkg", "exit 0")
    stub_bin("dpkg-query", "exit 1")          # nothing installed
    stub_bin("apt-get", 'echo "apt-get must not run" >&2; exit 1')
    r = run_script(SCRIPT)
    assert r.returncode == 0
    assert "Nothing to remove" in r.stdout


def test_purges_only_installed_packages(run_script, stub_bin, tmp_path):
    """A host that never had one of the packages must not see it mentioned."""
    log = tmp_path / "apt.log"
    # Real sudo resets PATH from secure_path, which would reach the host's apt.
    stub_bin("sudo", 'exec "$@"')
    stub_bin("dpkg", "exit 0")
    # Only libdxrt-bin reports as installed.
    stub_bin("dpkg-query", 'case "$*" in *libdxrt-bin*) echo "install ok installed";; *) exit 1;; esac')
    stub_bin("apt-get", f'echo "$@" >> {log}; exit 0')

    r = run_script(SCRIPT)

    assert r.returncode == 0
    purged = log.read_text()
    assert "libdxrt-bin" in purged
    assert "dxrt-driver-dkms" not in purged


def test_warns_about_what_it_cannot_undo(run_script, stub_bin, tmp_path):
    """Firmware and the dx_engine wheel survive, and the user is told so."""
    stub_bin("sudo", 'exec "$@"')
    stub_bin("dpkg", "exit 0")
    stub_bin("dpkg-query", 'echo "install ok installed"')
    stub_bin("apt-get", "exit 0")

    r = run_script(SCRIPT)

    assert r.returncode == 0
    assert "Firmware" in r.stderr
    assert "dx_engine" in r.stderr
    assert "reboot" in r.stdout


def test_requires_debian(run_script):
    r = run_script(SCRIPT, hide=["dpkg"])
    assert r.returncode != 0
    assert "dpkg" in r.stderr


def test_tells_an_unprivileged_user_the_command_to_run(run_script, stub_bin):
    stub_bin("id", "echo 1000")
    stub_bin("dpkg", "exit 0")
    r = run_script(SCRIPT, hide=["sudo"])
    assert r.returncode != 0
    assert "apt-get purge" in r.stderr
