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
    source: str | None = None

    # Count-in and song start (seconds into the audio). ``songStart`` is
    # where the music really kicks in after any count-in; ``countInStart``
    # is the first audible content of that count-in. ``countInClicks``
    # lists the time of each individual count-in click so the UI can stay
    # in sync with the stick clicks.
    countInStart: float | None = Field(default=None, ge=0.0)
    songStart: float | None = Field(default=None, ge=0.0)
    countInClicks: list[float] | None = None


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


class Section(SongMapModel):
    """
    A musical section.

    startBeat references the first beat of the section; startTime is
    kept for convenience. sourceName preserves the original chart label
    when the name has been normalized.
    """

    index: int = Field(ge=1)
    name: str
    startBeat: int = Field(ge=1)
    startTime: float = Field(ge=0.0)
    sourceName: str | None = None


class LyricLine(SongMapModel):
    """
    A single synced lyric line.
    """

    time: float = Field(ge=0.0)
    text: str


class VideoMedia(SongMapModel):
    """
    An external video associated with the recording.

    ``offset`` is the video time at which the song begins:
    ``videoTime = songTime + offset``. ``syncConfidence`` records how
    reliably the offset was detected (0..1). The offset may be negative
    when the recording starts with a count-in that the video does not
    have: the video then waits at its first frame until the song starts.
    """

    file: str
    offset: float = Field(ge=-3600.0)
    syncConfidence: float = Field(ge=0.0, le=1.0)


class Media(SongMapModel):
    """
    Audiovisual resources associated with the recording.

    The media block is independent of the timing: it never modifies
    beats, tempo or sections. Designed to grow (audio, video, cover).
    """

    video: VideoMedia | None = None


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
    sections: list[Section] | None = None
    media: Media | None = None