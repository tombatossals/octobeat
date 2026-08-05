from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CatalogMetadata(BaseModel):
    """
    Catalogue metadata describing a resource.

    This model matches the metadata.json/catalog.json documents
    consumed by VideoStick (packages/library MetadataSchema).
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    id: str

    title: str

    artist: str

    album: str | None = None

    year: int | None = None

    genres: list[str] = Field(
        default_factory=list,
    )

    bpm: float = Field(gt=0.0)

    duration: float = Field(ge=0.0)

    difficulty: int | None = None

    tags: list[str] = Field(
        default_factory=list,
    )

    timeSignature: str | None = None

    youtube: str | None = None

    resources: ResourceRefs


class ResourceRefs(BaseModel):
    """
    Relative media paths inside a resource directory.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    audio: str

    video: str | None = None
