from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_DATASETS_DIR = "~/Music/OctoBeat"

DEFAULT_AUDIO_FORMAT = "bestaudio"


class PathsConfig(BaseModel):
    """
    Filesystem paths used by the workspace.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    datasets: str = Field(
        default=DEFAULT_DATASETS_DIR,
    )

    charts: str | None = Field(
        default=None,
        description=(
            "Directory searched for community charts (SNG/MIDI/CHART) "
            "when building datasets. Falls back to the repo's sng/ "
            "directory when unset."
        ),
    )

    def datasets_dir(self) -> Path:
        return Path(
            self.datasets,
        ).expanduser().resolve()

    def charts_dir(self) -> Path | None:
        if self.charts is None:
            return None

        return Path(
            self.charts,
        ).expanduser().resolve()


class DownloadConfig(BaseModel):
    """
    Download preferences for media providers.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    audio_format: str = Field(
        default=DEFAULT_AUDIO_FORMAT,
    )


class CatalogConfig(BaseModel):
    """
    Catalog maintenance behaviour.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    auto_rebuild: bool = Field(
        default=True,
    )


class Config(BaseModel):
    """
    OctoBeat workspace configuration.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    paths: PathsConfig = Field(
        default_factory=PathsConfig,
    )

    download: DownloadConfig = Field(
        default_factory=DownloadConfig,
    )

    catalog: CatalogConfig = Field(
        default_factory=CatalogConfig,
    )

    def datasets_dir(self) -> Path:
        return self.paths.datasets_dir()
