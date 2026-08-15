from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CatalogMetadata(BaseModel):
    """
    Catalogue metadata describing a resource.

    This model matches the metadata.json/catalog.json documents
    consumed by OctoBeat (packages/library MetadataSchema).
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

    timing: TimingProvenance | None = None

    resources: ResourceRefs


class TimingProvenance(BaseModel):
    """
    Where the timing information came from and how reliable it is.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    source: str

    confidence: float = Field(ge=0.0, le=1.0)


class ResourceRefs(BaseModel):
    """
    Relative media paths inside a resource directory.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    audio: str

    lyrics: str | None = None
