from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_ID = "songmap/v1"
SONGMAP_VERSION = 1


MODEL_CONFIG = ConfigDict(
    frozen=True,
    extra="forbid",
    populate_by_name=True,
)


class SongMapModel(BaseModel):
    """
    Base class for all SongMap domain models.

    All SongMap models are immutable and reject unknown fields.
    """

    model_config = MODEL_CONFIG


class Source(SongMapModel):
    """
    Identifies the origin of the analysed recording.
    """

    type: str
    id: str


class SongMetadata(SongMapModel):
    """
    Minimal metadata describing the analysed recording.
    """

    title: str
    duration: float = Field(ge=0.0)
    source: Source


class Timing(SongMapModel):
    """
    Global timing information for the recording.
    """

    bpm: float = Field(gt=0.0)
    offset: float = Field(ge=0.0)
    timeSignature: str
    confidence: float = Field(ge=0.0, le=1.0)


class Beat(SongMapModel):
    """
    A single beat in the recording.
    """

    index: int = Field(ge=1)
    time: float = Field(ge=0.0)


class Bar(SongMapModel):
    """
    A musical bar.

    firstBeat references the index of the first beat belonging
    to this bar.
    """

    index: int = Field(ge=1)
    firstBeat: int = Field(ge=1)


class SongMap(SongMapModel):
    """
    Root SongMap document.
    """

    version: Literal[SONGMAP_VERSION] = SONGMAP_VERSION
    schema_: Literal[SCHEMA_ID] = Field(
        default=SCHEMA_ID,
        alias="schema",
    )

    generatedBy: str
    createdAt: str

    metadata: SongMetadata
    timing: Timing

    beats: list[Beat]
    bars: list[Bar]