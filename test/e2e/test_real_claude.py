"""End-to-end tests — the real ``claude`` binary mutates the filesystem via Ollama.

These prove the user's core requirement: with Claude Code pointed at the bridge,
a prompt actually changes files on disk (E01-E05). They drive the real binary in
headless mode (``-p`` + ``--dangerously-skip-permissions``) against the bridge,
in an isolated scratch workspace, with the redirect env that ``nasim start``
exports.

Two deliberate isolation choices, both grounded in measured behaviour on the
constrained test host (see docs/model-guidance.md):

1. A **minimal, controlled HOME** — no global ``CLAUDE.md``. A developer's real
   global config can inject 200 KB+ of unrelated rules that overflow ``num_ctx``
   and drown a small local model (it starts reaching for task/doc tools instead
   of the obvious Write). The bridge relays all of it faithfully; the model
   cannot cope. The e2e isolates the *pipeline*, not the developer's context.
2. The **GPU-resident model** (``NASIM_E2E_MODEL`` or ``models.fast``). On an
   11 GB GPU the 14b spills to CPU (~5 min/turn, non-deterministic); the 7b fits
   fully and completes reliably. The pipeline is identical for both.

Opt-in (slow, model-bound): ``pytest -m e2e`` or ``make loop E2E=1``. Skips if the
bridge is down or ``claude`` is not installed.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.e2e

_CLAUDE = shutil.which("claude")


def _run_claude(a_prompt: str, a_cwd: Path, a_home: Path, a_base_url: str, a_model: str, a_timeout: float = 300):
    """Run the real claude binary headless against the bridge; return CompletedProcess."""
    env = dict(os.environ)
    env.update(
        {
            "HOME": str(a_home),
            "ANTHROPIC_BASE_URL": a_base_url,
            "ANTHROPIC_AUTH_TOKEN": "nasim",
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
            "DISABLE_TELEMETRY": "1",
            "DISABLE_ERROR_REPORTING": "1",
        }
    )
    cmd = [_CLAUDE, "-p", a_prompt, "--model", a_model, "--dangerously-skip-permissions"]
    return subprocess.run(cmd, cwd=str(a_cwd), env=env, capture_output=True, text=True, timeout=a_timeout, check=False)


@pytest.fixture(scope="session")
def e2e_home(tmp_path_factory) -> Path:
    """Create a minimal, onboarded HOME with no global CLAUDE.md (small context)."""
    home = tmp_path_factory.mktemp("e2e_home")
    (home / ".claude.json").write_text(
        json.dumps({"hasCompletedOnboarding": True, "bypassPermissionsModeAccepted": True, "projects": {}}),
        encoding="utf-8",
    )
    return home


@pytest.fixture
def claude_run(bridge, cfg, e2e_home):
    """Return a runner bound to the live bridge + GPU-resident model; skip if no binary."""
    if not _CLAUDE:
        pytest.skip("claude binary not found on PATH")
    model = os.environ.get("NASIM_E2E_MODEL") or cfg.fast_model

    def _runner(a_prompt: str, a_cwd: Path, a_timeout: float = 300):
        return _run_claude(a_prompt, a_cwd, e2e_home, bridge, model, a_timeout)

    return _runner


def test_e01_write_new_file(claude_run, tmp_path):
    """E01 — a write prompt creates the file on disk with the requested content."""
    result = claude_run("Create a file named hello.txt containing exactly: Hello from Nasim", tmp_path)
    target = tmp_path / "hello.txt"
    assert target.is_file(), f"file not created (rc={result.returncode}); stderr={result.stderr[:500]}"
    assert "Hello from Nasim" in target.read_text(encoding="utf-8")


def test_e02_edit_existing_file(claude_run, tmp_path):
    """E02 — an edit prompt applies the change to an existing file on disk."""
    target = tmp_path / "config.txt"
    target.write_text("status = OLD\n", encoding="utf-8")
    result = claude_run("Edit config.txt: change the word OLD to NEW. Keep everything else.", tmp_path)
    content = target.read_text(encoding="utf-8")
    assert "NEW" in content, f"edit not applied (rc={result.returncode}); content={content!r}"
    assert "OLD" not in content


def test_e03_read_and_report(claude_run, tmp_path):
    """E03 — claude reads a file and reports its content in the final answer."""
    (tmp_path / "data.txt").write_text("The secret code is NASIM-4242.\n", encoding="utf-8")
    result = claude_run("Read data.txt and tell me the secret code it contains.", tmp_path)
    assert "4242" in result.stdout, f"code not reported; stdout={result.stdout[:500]}"


def test_e04_bash_command(claude_run, tmp_path):
    """E04 — claude runs a bash command and surfaces its output."""
    result = claude_run("Run the bash command: echo nasim-e2e-marker — and report its output.", tmp_path)
    assert "nasim-e2e-marker" in result.stdout, f"marker not in output; stdout={result.stdout[:500]}"


def test_e05_multistep_two_files(claude_run, tmp_path):
    """E05 — a multi-step task mutates >=2 files; all changes land on disk."""
    result = claude_run(
        "Create two files in this directory: a.txt containing 'aaa' and b.txt containing 'bbb'.",
        tmp_path,
        a_timeout=360,
    )
    a_file = tmp_path / "a.txt"
    b_file = tmp_path / "b.txt"
    assert (
        a_file.is_file() and b_file.is_file()
    ), f"both files not created (rc={result.returncode}); stderr={result.stderr[:500]}"
    assert "aaa" in a_file.read_text(encoding="utf-8")
    assert "bbb" in b_file.read_text(encoding="utf-8")
