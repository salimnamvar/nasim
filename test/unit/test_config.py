"""Unit tests for the single-source config and its precedence chain.

Precedence (lowest to highest): defaults -> nasim.toml -> nasim.local.toml -> env.
"""

import pytest

from nasim.config import Config


def _write(a_dir, a_name, a_text):
    """Write a TOML file into a_dir and return the dir."""
    a_dir.mkdir(parents=True, exist_ok=True)
    (a_dir / a_name).write_text(a_text, encoding="utf-8")
    return a_dir


def test_defaults_when_no_files_or_env(tmp_path, monkeypatch):
    """With no files and a clean env, built-in defaults apply."""
    for var in ("NASIM_REMOTE_HOST", "DEFAULT_MODEL", "NASIM_LOCAL_PORT"):
        monkeypatch.delenv(var, raising=False)
    cfg = Config.load(a_cfg_dir=tmp_path / "empty")
    assert cfg.remote_host == "black"
    assert cfg.local_port == 18080
    assert cfg.default_model == "qwen2.5-coder:14b"
    assert cfg.base_url == "http://localhost:18080"


def test_toml_overrides_defaults(tmp_path, monkeypatch):
    """nasim.toml values override the built-in defaults."""
    monkeypatch.delenv("NASIM_REMOTE_HOST", raising=False)
    cfg_dir = _write(tmp_path / "cfg", "nasim.toml", '[server]\nhost = "gpu-box"\nbridge_port = 9000\n')
    cfg = Config.load(a_cfg_dir=cfg_dir)
    assert cfg.remote_host == "gpu-box"
    assert cfg.bridge_port == 9000


def test_local_toml_overrides_base_toml(tmp_path):
    """nasim.local.toml overrides nasim.toml."""
    cfg_dir = tmp_path / "cfg"
    _write(cfg_dir, "nasim.toml", '[server]\nhost = "base-host"\n')
    _write(cfg_dir, "nasim.local.toml", '[server]\nhost = "local-host"\n')
    cfg = Config.load(a_cfg_dir=cfg_dir)
    assert cfg.remote_host == "local-host"


def test_env_overrides_everything(tmp_path, monkeypatch):
    """An environment override beats both TOML files."""
    cfg_dir = tmp_path / "cfg"
    _write(cfg_dir, "nasim.toml", '[server]\nhost = "base-host"\n')
    _write(cfg_dir, "nasim.local.toml", '[server]\nhost = "local-host"\n')
    monkeypatch.setenv("NASIM_REMOTE_HOST", "env-host")
    cfg = Config.load(a_cfg_dir=cfg_dir)
    assert cfg.remote_host == "env-host"


def test_env_casts_to_type(tmp_path, monkeypatch):
    """Env overrides are cast to the field's type (int/float)."""
    monkeypatch.setenv("NASIM_LOCAL_PORT", "12345")
    monkeypatch.setenv("BRIDGE_TIMEOUT", "30.5")
    cfg = Config.load(a_cfg_dir=tmp_path / "empty")
    assert cfg.local_port == 12345
    assert isinstance(cfg.local_port, int)
    assert cfg.request_timeout == 30.5


def test_invalid_env_cast_raises(tmp_path, monkeypatch):
    """A non-castable env override raises ValueError, not a silent wrong value."""
    monkeypatch.setenv("NASIM_LOCAL_PORT", "not-an-int")
    with pytest.raises(ValueError):
        Config.load(a_cfg_dir=tmp_path / "empty")


def test_config_is_frozen(tmp_path):
    """Config is immutable — attribute assignment is rejected."""
    cfg = Config.load(a_cfg_dir=tmp_path / "empty")
    with pytest.raises(Exception):
        cfg.remote_host = "mutate"  # type: ignore[misc]
