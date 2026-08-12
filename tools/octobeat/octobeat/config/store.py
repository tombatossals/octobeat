from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

from octobeat.config.model import Config
from octobeat.io.resource import CATALOG_FILE

DEFAULT_CONFIG_DIR = (
    Path.home()
    / ".config"
    / "octobeat"
)

DEFAULT_CONFIG_FILE = (
    DEFAULT_CONFIG_DIR
    / "config.toml"
)

CONFIG_ENV = "OCTOBEAT_CONFIG"


def config_path() -> Path:
    """
    Return the canonical configuration file path.

    An explicit location can be provided through the OCTOBEAT_CONFIG
    environment variable; otherwise the default user config path is
    used.
    """

    override = os.environ.get(CONFIG_ENV)

    if override:
        return Path(
            override,
        ).expanduser()

    return DEFAULT_CONFIG_FILE


def load_config() -> Config:
    """
    Load the workspace configuration.

    Returns the built-in defaults when no configuration file exists.
    Unknown keys from older config versions are ignored.
    """

    path = config_path()

    if not path.exists():
        return Config()

    with path.open("rb") as file:
        data = tomllib.load(file)

    data = _drop_unknown_sections(data)

    return Config.model_validate(data)


def _drop_unknown_sections(
    data: dict[str, Any],
) -> dict[str, Any]:
    """
    Remove keys that are no longer present in the configuration model,
    so stale values from older versions do not break loading.
    """

    model_sections = (
        Config.model_fields.keys()
    )

    cleaned: dict[str, Any] = {}

    for section, value in data.items():
        if section not in model_sections:
            continue

        if isinstance(value, dict):
            model = Config.model_fields[
                section
            ].annotation

            fields = (
                getattr(model, "model_fields", {})
                if isinstance(
                    model,
                    type,
                )
                else {}
            )

            if fields:
                value = {
                    key: item
                    for key, item in value.items()
                    if key in fields
                }

        cleaned[section] = value

    return cleaned


def save_config(
    config: Config,
    path: Path | None = None,
) -> Path:
    """
    Persist the configuration to disk.
    """

    path = (
        path
        or config_path()
    ).expanduser()

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        config_to_toml(config),
        encoding="utf-8",
    )

    return path


def config_to_toml(config: Config) -> str:
    """
    Serialize the configuration into a TOML document.
    """

    lines: list[str] = [
        "[paths]",
        f'datasets = "{_escape(config.paths.datasets)}"',
        "",
        "[download]",
        f'audio_format = "{_escape(config.download.audio_format)}"',
        "",
        "[catalog]",
        f'auto_rebuild = {"true" if config.catalog.auto_rebuild else "false"}',
        "",
    ]

    return "\n".join(lines)


def set_value(
    config: Config,
    key: str,
    raw: str,
) -> Config:
    """
    Return a new configuration with the dotted `key` set to `raw`.
    """

    section, field = _split_key(key)

    sections = {
        "paths": config.paths,
        "download": config.download,
        "catalog": config.catalog,
    }

    current = sections.get(section)

    if current is None:
        raise ValueError(
            f"Unknown configuration section '{section}'.",
        )

    fields = type(current).model_fields

    if field not in fields:
        raise ValueError(
            f"Unknown configuration key '{key}'.",
        )

    value: Any = raw

    if fields[field].annotation is bool:
        value = raw.strip().lower() in {
            "true",
            "1",
            "yes",
            "on",
        }

    updated = type(current).model_validate(
        {
            **current.model_dump(),
            field: value,
        },
    )

    return config.model_copy(
        update={
            section: updated,
        },
    )


def ensure_workspace() -> Config:
    """
    Initialize the workspace if needed and return the configuration.

    Creates the configuration file, the datasets directory and an
    empty catalog. The operation is idempotent.
    """

    config = load_config()

    save_config(config)

    datasets_dir = config.datasets_dir()
    datasets_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    catalog_path = (
        datasets_dir / CATALOG_FILE
    )

    if not catalog_path.exists():
        catalog_path.write_text(
            "[]\n",
            encoding="utf-8",
        )

    return config


def _split_key(key: str) -> tuple[str, str]:
    parts = key.split(".")

    if len(parts) != 2 or not all(parts):
        raise ValueError(
            "Configuration keys must be "
            "'section.field', e.g. paths.datasets.",
        )

    section, field = parts

    if section not in {
        "paths",
        "download",
        "catalog",
    }:
        raise ValueError(
            f"Unknown configuration section '{section}'.",
        )

    return section, field


def _escape(value: str) -> str:
    return (
        value.replace("\\", "\\\\").replace('"', '\\"')
    )
