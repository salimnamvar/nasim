"""Gating safety tests: the clean-toggle guarantee for Claude Code.

These assert the core promise: after a nasim session there is zero Ollama leakage —
no ``_nasim`` picker entries in ``~/.claude.json`` and the original
``settings.json["model"]`` restored exactly (or removed if it never existed).
"""

from __future__ import annotations

import json

from nasim.claude_settings import ClaudeSettings


def _write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _settings(paths):
    return ClaudeSettings(paths["settings"], paths["dot_claude"], paths["backup"])


def test_inject_adds_marked_entry_and_sets_model(claude_paths):
    """Inject surfaces the model in the picker and sets it active."""
    _write(claude_paths["settings"], {"model": "opus", "theme": "dark"})
    _write(claude_paths["dot_claude"], {"additionalModelOptionsCache": [{"label": "Fable", "value": "x"}]})

    cs = _settings(claude_paths)
    cs.inject("deepseek-r1:14b")

    dot = _read(claude_paths["dot_claude"])
    marked = [e for e in dot["additionalModelOptionsCache"] if e.get("_nasim")]
    assert len(marked) == 1
    assert marked[0]["value"] == "deepseek-r1:14b"
    # Pre-existing non-nasim entries are preserved.
    assert any(e.get("label") == "Fable" for e in dot["additionalModelOptionsCache"])
    # Active model is now the ollama tag.
    assert _read(claude_paths["settings"])["model"] == "deepseek-r1:14b"


def test_eject_restores_model_and_removes_entries(claude_paths):
    """Eject removes all marked entries and restores the original model."""
    _write(claude_paths["settings"], {"model": "opus"})
    _write(claude_paths["dot_claude"], {"additionalModelOptionsCache": [{"label": "Fable", "value": "x"}]})

    cs = _settings(claude_paths)
    cs.inject("deepseek-r1:14b")
    cs.eject()

    dot = _read(claude_paths["dot_claude"])
    assert all(not e.get("_nasim") for e in dot["additionalModelOptionsCache"])
    assert any(e.get("label") == "Fable" for e in dot["additionalModelOptionsCache"])
    assert _read(claude_paths["settings"])["model"] == "opus"
    assert not claude_paths["backup"].exists()


def test_eject_removes_model_key_when_originally_absent(claude_paths):
    """If settings had no model key, eject deletes the one nasim added."""
    _write(claude_paths["settings"], {"theme": "dark"})
    _write(claude_paths["dot_claude"], {})

    cs = _settings(claude_paths)
    cs.inject("qwen3:8b")
    assert "model" in _read(claude_paths["settings"])
    cs.eject()
    assert "model" not in _read(claude_paths["settings"])


def test_double_eject_is_idempotent(claude_paths):
    """A second eject is a harmless no-op."""
    _write(claude_paths["settings"], {"model": "opus"})
    _write(claude_paths["dot_claude"], {})
    cs = _settings(claude_paths)
    cs.inject("deepseek-r1:14b")
    cs.eject()
    cs.eject()  # must not raise or corrupt
    assert _read(claude_paths["settings"])["model"] == "opus"
    assert not cs.has_nasim_entries()


def test_sanitize_heals_stray_entry_without_backup(claude_paths):
    """Sanitize removes a stray _nasim entry left by a crashed/old session."""
    # Simulate leftover state: a marked picker entry, no backup file.
    _write(
        claude_paths["dot_claude"],
        {"additionalModelOptionsCache": [{"label": "stray", "value": "deepseek-r1:14b", "_nasim": True}]},
    )
    _write(claude_paths["settings"], {"model": "opus"})

    cs = _settings(claude_paths)
    assert cs.has_nasim_entries()
    cs.sanitize()
    assert not cs.has_nasim_entries()
    # Original model untouched (no backup existed, so nothing to restore).
    assert _read(claude_paths["settings"])["model"] == "opus"


def test_backup_is_taken_once(claude_paths):
    """A second inject does not overwrite the original-model backup."""
    _write(claude_paths["settings"], {"model": "opus"})
    _write(claude_paths["dot_claude"], {})
    cs = _settings(claude_paths)
    cs.inject("deepseek-r1:14b")  # backup records opus
    # Now settings model is the tag; a second inject must keep backup == opus.
    cs.inject("qwen3:8b")
    backup = _read(claude_paths["backup"])
    assert backup["original_model"] == "opus"
    cs.eject()
    assert _read(claude_paths["settings"])["model"] == "opus"
