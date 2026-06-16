"""Live rollback contract — the full start/stop guarantee (T01-T09).

Runs the real :class:`NasimController` against the live bridge, but isolated: a
temp ``$HOME`` (seeded with realistic Claude config) and a dedicated local port,
so a developer's active nasim session on the default port is never disturbed.
Skips cleanly if the bridge is unreachable.
"""

import json

import pytest

from nasim.config import Config
from nasim.runtime.controller import _REDIRECT_ENV_NAMES, NasimController
from nasim.runtime.paths import RuntimePaths

pytestmark = pytest.mark.rollback

_ROLLBACK_PORT = 18098


def _read(a_path):
    """Parse a JSON file."""
    return json.loads(a_path.read_text(encoding="utf-8"))


@pytest.fixture
def live(cfg, tmp_path):
    """Yield a started controller over an isolated home + dedicated tunnel.

    Builds a config with the real host/bridge port but a unique local port, seeds
    a temp home with a baseline model selection and one pre-existing picker entry,
    then starts. Skips the module if start fails (bridge down). Always stops on
    teardown.
    """
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    (cfg_dir / "nasim.toml").write_text(
        f'[server]\nhost = "{cfg.remote_host}"\nbridge_port = {cfg.bridge_port}\n'
        f"[client]\nlocal_port = {_ROLLBACK_PORT}\n",
        encoding="utf-8",
    )
    rollback_cfg = Config.load(a_cfg_dir=cfg_dir)

    home = tmp_path / "home"
    paths = RuntimePaths(root=home)
    paths.ensure()
    paths.claude_json.write_text(
        json.dumps({"projects": {"/p": [1]}, "additionalModelOptionsCache": [{"value": "real"}]}),
        encoding="utf-8",
    )
    paths.settings_json.parent.mkdir(parents=True, exist_ok=True)
    paths.settings_json.write_text(json.dumps({"model": "opus", "theme": "dark"}), encoding="utf-8")

    controller = NasimController(rollback_cfg, paths)
    ok, report = controller.start()
    if not ok:
        controller.stop()
        pytest.skip(f"bridge not reachable for rollback test: {report.get('error')}")
    yield controller, paths, rollback_cfg
    controller.stop()


def test_t01_start_opens_tunnel_sets_state_backs_up(live):
    """T01 — start opens the tunnel, records state, writes env, backs up model."""
    controller, paths, _ = live
    assert controller._tunnel.is_alive()
    assert _read(paths.state_file)["backend"] == "ollama"
    assert paths.saved_model_file.is_file()
    assert _read(paths.saved_model_file) == {"present": True, "model": "opus"}
    env = paths.env_file.read_text(encoding="utf-8")
    for name in _REDIRECT_ENV_NAMES:
        assert f"export {name}=" in env


def test_t02_start_injects_marked_models(live):
    """T02 — start injects bridge models into the picker, all marked."""
    _, paths, _ = live
    cache = _read(paths.claude_json)["additionalModelOptionsCache"]
    marked = [e for e in cache if e.get("_nasim")]
    assert marked, "no nasim-marked models injected"
    assert any(e["value"] == "real" for e in cache)  # existing entry preserved


def test_t03_start_selects_recommended_model(live):
    """T03 — start selects the recommended model in settings.json."""
    _, paths, rollback_cfg = live
    assert _read(paths.settings_json)["model"] == rollback_cfg.recommended_model


def test_t04_status_reflects_running(live):
    """T04 — status reports the ollama backend, a live tunnel, and an ok bridge."""
    controller, _, _ = live
    ok, report = controller.status()
    assert ok
    assert report["backend"] == "ollama"
    assert report["tunnel_alive"] is True
    assert report["bridge"] == "ok"


def test_t05_t06_stop_full_rollback(live):
    """T05/T06 — stop kills the tunnel, ejects models, restores the exact model."""
    controller, paths, _ = live
    controller.stop()
    assert not controller._tunnel.is_alive()
    cache = _read(paths.claude_json)["additionalModelOptionsCache"]
    assert [e for e in cache if e.get("_nasim")] == []  # all marked ejected
    assert any(e["value"] == "real" for e in cache)  # AP-06: real entry survives
    assert _read(paths.claude_json)["projects"] == {"/p": [1]}  # session data intact
    assert _read(paths.settings_json)["model"] == "opus"  # T06: exact restore
    assert _read(paths.settings_json)["theme"] == "dark"
    env = paths.env_file.read_text(encoding="utf-8")
    for name in _REDIRECT_ENV_NAMES:
        assert f"unset {name}" in env


def test_t07_double_start_idempotent(live):
    """T07 — a second start leaves one tunnel and no duplicate picker entries."""
    controller, paths, _ = live
    ok, _ = controller.start()
    assert ok
    assert controller._tunnel.is_alive()
    cache = _read(paths.claude_json)["additionalModelOptionsCache"]
    values = [e["value"] for e in cache if e.get("_nasim")]
    assert len(values) == len(set(values))  # no duplicates
    # backup still reflects the original baseline, not an Ollama tag
    assert _read(paths.saved_model_file)["model"] == "opus"


def test_t08_t09_double_stop_safe_and_baseline_intact(live):
    """T08/T09 — a second stop is safe and the pre-start model stays restored."""
    controller, paths, _ = live
    controller.stop()
    controller.stop()  # must not raise or corrupt
    assert _read(paths.settings_json)["model"] == "opus"
    assert _read(paths.state_file)["backend"] == "anthropic"
