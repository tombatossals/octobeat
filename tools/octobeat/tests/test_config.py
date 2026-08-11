from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from octobeat.config import (
    Config,
    config_path,
    config_to_toml,
    ensure_workspace,
    load_config,
    save_config,
    set_value,
)


@pytest.fixture(autouse=True)
def isolated_config(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "OCTOBEAT_CONFIG",
        str(tmp_path / "config.toml"),
    )


def test_defaults() -> None:
    config = Config()

    assert config.paths.datasets == "~/Music/OctoBeat"
    assert config.download.audio_format == "bestaudio"
    assert config.catalog.auto_rebuild is True


def test_toml_roundtrip(tmp_path) -> None:
    config = Config()

    toml = config_to_toml(config)

    parsed = tomllib.loads(toml)

    assert parsed["paths"]["datasets"] == "~/Music/OctoBeat"
    assert parsed["download"]["audio_format"] == "bestaudio"
    assert parsed["catalog"]["auto_rebuild"] is True

    loaded = Config.model_validate(parsed)

    assert loaded == config


def test_save_and_load(tmp_path) -> None:
    config = Config()
    path = save_config(config)

    assert path.exists()

    loaded = load_config()

    assert loaded == config
    assert config_path() == path


def test_save_preserves_custom_values(tmp_path) -> None:
    config = set_value(
        Config(),
        "paths.datasets",
        "/custom/music",
    )
    config = set_value(
        config,
        "catalog.auto_rebuild",
        "false",
    )

    save_config(config)

    loaded = load_config()

    assert loaded.paths.datasets == "/custom/music"
    assert loaded.catalog.auto_rebuild is False


def test_set_value_bool_coercion() -> None:
    assert (
        set_value(
            Config(),
            "catalog.auto_rebuild",
            "true",
        ).catalog.auto_rebuild
        is True
    )

    assert (
        set_value(
            Config(),
            "catalog.auto_rebuild",
            "0",
        ).catalog.auto_rebuild
        is False
    )


def test_set_value_keeps_strings() -> None:
    config = set_value(
        Config(),
        "download.audio_format",
        "worst",
    )

    assert config.download.audio_format == "worst"


def test_set_value_unknown_key() -> None:
    with pytest.raises(ValueError):
        set_value(
            Config(),
            "paths.nonexistent",
            "x",
        )

    with pytest.raises(ValueError):
        set_value(
            Config(),
            "unknown.field",
            "x",
        )

    with pytest.raises(ValueError):
        set_value(
            Config(),
            "flatkey",
            "x",
        )


def test_config_path_env_override(monkeypatch) -> None:
    monkeypatch.setenv(
        "OCTOBEAT_CONFIG",
        "/tmp/custom/octobeat.toml",
    )

    assert config_path() == Path("/tmp/custom/octobeat.toml")


def test_ensure_workspace_creates_layout(tmp_path) -> None:
    config = ensure_workspace()

    assert (tmp_path / "config.toml").exists()
    assert config.datasets_dir().is_dir()
    assert (config.datasets_dir() / "catalog.json").exists()


def test_ensure_workspace_is_idempotent(tmp_path) -> None:
    ensure_workspace()
    ensure_workspace()

    assert (tmp_path / "config.toml").exists()
