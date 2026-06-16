"""Unit tests for NasimController orchestration that need no network.

start() requires a live bridge and is covered by the rollback layer. Here we
verify stop() rollback wiring and offline status() against an isolated temp
home. The controller is built with a unique local port and a bogus host so its
tunnel ``pkill`` fallback can never match a real nasim tunnel on this machine.
"""

import json

from nasim.config import Config
from nasim.runtime.controller import _REDIRECT_ENV_NAMES, NasimController


def _isolated_config(tmp_path):
    """A Config with a unique port + unreachable host (safe pkill, no real match)."""
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    (cfg_dir / "nasim.toml").write_text(
        '[server]\nhost = "nasim-test-nonexistent"\nbridge_port = 1\n[client]\nlocal_port = 19771\n',
        encoding="utf-8",
    )
    return Config.load(a_cfg_dir=cfg_dir)


def test_stop_is_full_rollback(tmp_path, paths):
    """stop() ejects models, restores the model, sets anthropic, writes unsets."""
    # Seed an 'active ollama session' state on disk.
    paths.claude_json.write_text(
        json.dumps({"additionalModelOptionsCache": [{"value": "real"}, {"value": "x:1", "_nasim": True}]}),
        encoding="utf-8",
    )
    paths.settings_json.parent.mkdir(parents=True, exist_ok=True)
    paths.settings_json.write_text(json.dumps({"model": "x:1"}), encoding="utf-8")
    paths.saved_model_file.write_text(json.dumps({"present": True, "model": "opus"}), encoding="utf-8")
    paths.state_file.write_text(json.dumps({"backend": "ollama"}), encoding="utf-8")

    controller = NasimController(_isolated_config(tmp_path), paths)
    ok, _ = controller.stop()
    assert ok

    cache = json.loads(paths.claude_json.read_text(encoding="utf-8"))["additionalModelOptionsCache"]
    assert cache == [{"value": "real"}]  # marked entry ejected, real survives
    assert json.loads(paths.settings_json.read_text(encoding="utf-8"))["model"] == "opus"  # restored
    assert json.loads(paths.state_file.read_text(encoding="utf-8"))["backend"] == "anthropic"
    env = paths.env_file.read_text(encoding="utf-8")
    for name in _REDIRECT_ENV_NAMES:
        assert f"unset {name}" in env


def test_double_stop_is_safe(tmp_path, paths):
    """A second stop with nothing running still succeeds and changes nothing bad (T08)."""
    controller = NasimController(_isolated_config(tmp_path), paths)
    controller.stop()
    ok, _ = controller.stop()
    assert ok
    assert json.loads(paths.state_file.read_text(encoding="utf-8"))["backend"] == "anthropic"


def test_status_offline_reports_anthropic(tmp_path, paths):
    """status() with the anthropic backend needs no network and reports cleanly."""
    controller = NasimController(_isolated_config(tmp_path), paths)
    controller.stop()  # ensure anthropic state
    ok, report = controller.status()
    assert ok
    assert report["backend"] == "anthropic"
    assert report["base_url"] == "http://localhost:19771"
    assert report["tunnel_alive"] is False


def test_redirect_env_names_match_exports(tmp_path, paths):
    """Every exported redirect var has a matching unset name (start/stop symmetry)."""
    controller = NasimController(_isolated_config(tmp_path), paths)
    exports = controller._redirect_exports()
    assert set(exports) == set(_REDIRECT_ENV_NAMES)
    assert exports["ANTHROPIC_BASE_URL"] == "http://localhost:19771"
