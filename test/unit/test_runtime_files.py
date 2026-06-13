"""Unit tests for the file-surgery runtime helpers (T02, T05, T06, AP-06/07/08).

All run against an isolated temp home (the ``paths`` fixture) — no network, no
real ``~/.claude``.
"""

import json

from nasim.runtime.picker import ModelPicker
from nasim.runtime.settings import ClaudeSettings
from nasim.runtime.state import StateStore


def _read(a_path):
    """Parse a JSON file."""
    return json.loads(a_path.read_text(encoding="utf-8"))


# ── ModelPicker (T02 inject, T05 eject, AP-06 surgical, AP-08 idempotent) ─────


def test_t02_inject_marks_entries_and_preserves_existing(paths):
    """inject adds marked entries and leaves pre-existing picker entries intact."""
    paths.claude_json.write_text(
        json.dumps({"projects": {"/p": 1}, "additionalModelOptionsCache": [{"value": "real"}]}),
        encoding="utf-8",
    )
    picker = ModelPicker(paths.claude_json)
    ok, added = picker.inject([{"id": "qwen2.5-coder:14b"}, {"id": "gemma4:latest"}])
    assert ok and added == 2
    cache = _read(paths.claude_json)["additionalModelOptionsCache"]
    marked = [e for e in cache if e.get("_nasim")]
    assert {e["value"] for e in marked} == {"qwen2.5-coder:14b", "gemma4:latest"}
    assert any(e["value"] == "real" for e in cache)  # AP-06: existing entry survives


def test_ap08_inject_is_idempotent(paths):
    """A second inject of the same models adds nothing (marker-based, not count)."""
    paths.claude_json.write_text(json.dumps({"additionalModelOptionsCache": []}), encoding="utf-8")
    picker = ModelPicker(paths.claude_json)
    picker.inject([{"id": "qwen2.5-coder:14b"}])
    ok, added = picker.inject([{"id": "qwen2.5-coder:14b"}])
    assert ok and added == 0


def test_t05_eject_removes_only_marked(paths):
    """eject removes every marked entry and only those (AP-06/AP-08)."""
    paths.claude_json.write_text(
        json.dumps(
            {
                "projects": {"/p": [1, 2]},
                "additionalModelOptionsCache": [
                    {"value": "real"},
                    {"value": "qwen2.5-coder:14b", "_nasim": True},
                    {"value": "gemma4:latest", "_nasim": True},
                ],
            }
        ),
        encoding="utf-8",
    )
    picker = ModelPicker(paths.claude_json)
    ok, removed = picker.eject()
    assert ok and removed == 2
    data = _read(paths.claude_json)
    assert data["additionalModelOptionsCache"] == [{"value": "real"}]
    assert data["projects"] == {"/p": [1, 2]}  # AP-06: session data untouched


def test_eject_idempotent_when_nothing_marked(paths):
    """A second eject removes nothing and still succeeds (T08 support)."""
    paths.claude_json.write_text(json.dumps({"additionalModelOptionsCache": [{"value": "real"}]}), encoding="utf-8")
    picker = ModelPicker(paths.claude_json)
    ok, removed = picker.eject()
    assert ok and removed == 0


def test_inject_skips_when_claude_json_absent(paths):
    """With no ~/.claude.json, inject is a safe no-op (success, 0 added)."""
    picker = ModelPicker(paths.claude_json)
    ok, added = picker.inject([{"id": "x:1"}])
    assert ok is False and added == 0  # cannot inject without the file


# ── ClaudeSettings (T06 restore exact, AP-07 heal dangling pick) ──────────────


def test_t06_backup_once_and_restore_exact(paths):
    """The pre-start model is restored exactly, healing a later /model pick (AP-07)."""
    paths.settings_json.parent.mkdir(parents=True, exist_ok=True)
    paths.settings_json.write_text(json.dumps({"model": "opus", "theme": "dark"}), encoding="utf-8")
    settings = ClaudeSettings(paths.settings_json, paths.saved_model_file)

    settings.backup_and_set_model("qwen2.5-coder:14b")
    assert _read(paths.settings_json)["model"] == "qwen2.5-coder:14b"

    # user picks an Ollama tag via /model, then a repeated start must NOT re-capture
    paths.settings_json.write_text(json.dumps({"model": "qwen2.5-coder:7b", "theme": "dark"}), encoding="utf-8")
    settings.backup_and_set_model("qwen2.5-coder:14b")

    settings.restore_model()
    final = _read(paths.settings_json)
    assert final["model"] == "opus"  # exact pre-start value
    assert final["theme"] == "dark"  # other settings untouched


def test_t06_restore_removes_key_when_absent_at_start(paths):
    """If no model was set pre-start, restore removes the key (T09 baseline)."""
    paths.settings_json.parent.mkdir(parents=True, exist_ok=True)
    paths.settings_json.write_text(json.dumps({"theme": "dark"}), encoding="utf-8")
    settings = ClaudeSettings(paths.settings_json, paths.saved_model_file)
    settings.backup_and_set_model("qwen2.5-coder:14b")
    settings.restore_model()
    assert "model" not in _read(paths.settings_json)


def test_restore_is_noop_without_backup(paths):
    """A second stop (no backup file) leaves the current selection untouched (T08)."""
    paths.settings_json.parent.mkdir(parents=True, exist_ok=True)
    paths.settings_json.write_text(json.dumps({"model": "opus"}), encoding="utf-8")
    settings = ClaudeSettings(paths.settings_json, paths.saved_model_file)
    settings.restore_model()
    assert _read(paths.settings_json)["model"] == "opus"


def test_current_model(paths):
    """current_model reflects the active selection or None."""
    paths.settings_json.parent.mkdir(parents=True, exist_ok=True)
    paths.settings_json.write_text(json.dumps({"model": "opus"}), encoding="utf-8")
    settings = ClaudeSettings(paths.settings_json, paths.saved_model_file)
    assert settings.current_model() == "opus"


# ── StateStore (backend state + shell env directives) ─────────────────────────


def test_state_roundtrip_and_default(paths):
    """Backend state persists; default is 'anthropic' when unset."""
    state = StateStore(paths.state_file, paths.env_file)
    assert state.get_backend() == "anthropic"
    state.set_backend("ollama")
    assert state.get_backend() == "ollama"


def test_state_writes_sourceable_exports(paths):
    """Exports are written as shell-sourceable 'export NAME=value' lines."""
    state = StateStore(paths.state_file, paths.env_file)
    state.write_exports({"ANTHROPIC_BASE_URL": "http://localhost:18080", "DISABLE_TELEMETRY": "1"})
    text = paths.env_file.read_text(encoding="utf-8")
    assert "export ANTHROPIC_BASE_URL=http://localhost:18080" in text
    assert "export DISABLE_TELEMETRY=1" in text


def test_state_quotes_unsafe_export_values(paths):
    """A value with shell metacharacters is quoted so sourcing is safe."""
    state = StateStore(paths.state_file, paths.env_file)
    state.write_exports({"X": "a b; rm -rf /"})
    text = paths.env_file.read_text(encoding="utf-8")
    assert "export X='a b; rm -rf /'" in text


def test_state_writes_unsets(paths):
    """Unsets are written as 'unset NAME' lines."""
    state = StateStore(paths.state_file, paths.env_file)
    state.write_unsets(["A", "B"])
    assert paths.env_file.read_text(encoding="utf-8").split() == ["unset", "A", "unset", "B"]
