"""Parity unit tests: config precedence, env builder, vram, dispatch, probe parsing."""

from __future__ import annotations

import json

from nasim import config as config_mod
from nasim.agents.base import build_anthropic_env


def test_config_precedence_env_over_file(tmp_path, monkeypatch):
    """Environment variables override the config file, which overrides defaults."""
    cfg_file = tmp_path / "nasim.conf"
    cfg_file.write_text("BLACK_HOST=fromfile\nDEFAULT_MODEL=fromfile-model\n", encoding="utf-8")
    monkeypatch.setattr(config_mod, "CONFIG_FILE", cfg_file)
    monkeypatch.setenv("BLACK_HOST", "fromenv")
    cfg = config_mod.reload_config()
    assert cfg.black_host == "fromenv"  # env wins
    assert cfg.default_model == "fromfile-model"  # file wins over default
    assert cfg.default_local_port == 11435  # untouched default


def test_config_int_coercion(tmp_path, monkeypatch):
    """Numeric config values are coerced to int."""
    cfg_file = tmp_path / "nasim.conf"
    cfg_file.write_text("DEFAULT_LOCAL_PORT=12000\n", encoding="utf-8")
    monkeypatch.setattr(config_mod, "CONFIG_FILE", cfg_file)
    monkeypatch.delenv("DEFAULT_LOCAL_PORT", raising=False)
    cfg = config_mod.reload_config()
    assert cfg.default_local_port == 12000
    assert isinstance(cfg.default_local_port, int)


def test_build_anthropic_env_maps_all_tiers():
    """All three Claude tiers map to the chosen model and base URL is normalised."""
    env = build_anthropic_env("deepseek-r1:14b", "http://127.0.0.1:11435/", a_workspace="/tmp/ws")
    assert env["ANTHROPIC_BASE_URL"] == "http://127.0.0.1:11435"
    assert env["ANTHROPIC_API_URL"] == "http://127.0.0.1:11435/v1"
    assert env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] == "deepseek-r1:14b"
    assert env["ANTHROPIC_DEFAULT_SONNET_MODEL"] == "deepseek-r1:14b"
    assert env["ANTHROPIC_DEFAULT_OPUS_MODEL"] == "deepseek-r1:14b"
    assert env["ANTHROPIC_AUTH_TOKEN"] == "ollama"
    assert env["CLAUDE_WORKSPACE"] == "/tmp/ws"


def test_vram_estimate():
    """VRAM estimate parses params + quant and rounds up; unknown tags return None."""
    from nasim import vram

    assert vram.estimate("deepseek-r1:14b") == 10  # 14 * 0.55 * 1.2 -> ceil 10
    assert vram.estimate("qwen3:8b") == 6
    assert vram.estimate("nomic-embed-text:latest") is None


def test_detect_agent_prefers_available(monkeypatch):
    """detect_agent returns the first available agent in priority order."""
    from nasim import agents

    monkeypatch.setattr(agents, "have", lambda name: name == "aider")
    assert agents.detect_agent() == "aider"
    monkeypatch.setattr(agents, "have", lambda name: False)
    assert agents.detect_agent() == "terminal"


def test_launch_agent_dry_returns_zero(capsys):
    """Dry-run agent dispatch prints a DRY line and returns 0 without side effects."""
    from nasim.agents import launch_agent

    rc = launch_agent("claude", "http://127.0.0.1:11435", "deepseek-r1:14b", [])
    out = capsys.readouterr().out
    assert rc == 0
    assert "DRY:" in out


def test_probe_url_false_on_unreachable():
    """probe_url returns False for an unreachable endpoint (no exception)."""
    from nasim.probe import probe_url

    assert probe_url("http://127.0.0.1:1") is False


def test_free_port_returns_open_port():
    """free_port returns a bindable port at/above the base."""
    from nasim.transport import free_port

    port = free_port(53000)
    assert 53000 <= port <= 53100
