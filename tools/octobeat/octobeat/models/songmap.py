from __future__ import annotations

from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_ID: Final = "songmap/v1"
SONGMAP_VERSION: Final = 1


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


class TempoSegment(SongMapModel):
    """
    A constant-tempo segment of the recording.

    ``time`` is the start time (seconds) of the segment; ``bpm`` is
    the tempo from that moment until the next segment (or the end of
    the recording).
    """

    time: float = Field(ge=0.0)
    bpm: float = Field(gt=0.0)


class Timing(SongMapModel):
    """
    Global timing information for the recording.
    """

    bpm: float = Field(gt=0.0)
    offset: float = Field(ge=0.0)
    timeSignature: str
    confidence: float = Field(ge=0.0, le=1.0)
    tempoMap: list[TempoSegment] | None = None


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


class LyricLine(SongMapModel):
    """
    A single synced lyric line.
    """

    time: float = Field(ge=0.0)
    text: str


class SongMap(SongMapModel):
    """
    Root SongMap document.
    """

    version: Literal[1] = SONGMAP_VERSION
    schema_: Literal["songmap/v1"] = Field(
        default=SCHEMA_ID,
        alias="schema",
    )

    generatedBy: str
    createdAt: str

    metadata: SongMetadata
    timing: Timing

    beats: list[Beat]
    bars: list[Bar]

    lyrics: list[LyricLine] | None = None