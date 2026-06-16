"""Unit tests for RuntimePaths — single-root derivation (decision D5)."""

from pathlib import Path

from nasim.runtime.paths import RuntimePaths


def test_all_paths_derive_from_root(tmp_path):
    """Every runtime path is rooted under the given root; state under ~/.nasim."""
    p = RuntimePaths(root=tmp_path)
    assert p.nasim_dir == tmp_path / ".nasim"
    assert p.state_file == tmp_path / ".nasim" / "state.json"
    assert p.pid_file == tmp_path / ".nasim" / "tunnel.pid"
    assert p.saved_model_file == tmp_path / ".nasim" / "saved_model.json"
    assert p.env_file == tmp_path / ".nasim" / "env.sh"
    assert p.claude_json == tmp_path / ".claude.json"
    assert p.settings_json == tmp_path / ".claude" / "settings.json"


def test_ensure_creates_nasim_dir(tmp_path):
    """ensure() creates the ~/.nasim directory idempotently."""
    p = RuntimePaths(root=tmp_path)
    assert not p.nasim_dir.exists()
    p.ensure()
    assert p.nasim_dir.is_dir()
    p.ensure()  # idempotent
    assert p.nasim_dir.is_dir()


def test_default_roots_at_home():
    """default() roots at the user's home directory."""
    assert RuntimePaths.default().root == Path.home()
