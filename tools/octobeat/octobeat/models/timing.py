from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

MODEL_CONFIG = ConfigDict(
    frozen=True,
    extra="forbid",
)


class TimingModel(BaseModel):
    """
    Base class for canonical timing models.

    Immutable, rejects unknown fields. Mirrors the SongMap model
    conventions in ``octobeat.models.songmap``.
    """

    model_config = MODEL_CONFIG


class TempoSegment(TimingModel):
    """
    A constant-tempo segment.

    ``start_beat`` and ``start_time`` refer to the beat index (1-based)
    and absolute seconds at which this tempo takes over.
    """

    start_beat: int = Field(ge=1)
    start_time: float = Field(ge=0.0)
    bpm: float = Field(gt=0.0)


class Beat(TimingModel):
    """
    A single beat in the chart.

    ``index`` is 1-based; ``time`` is absolute seconds.
    """

    index: int = Field(ge=1)
    time: float = Field(ge=0.0)


class TimeSignature(TimingModel):
    """
    A time signature change.

    ``start_beat`` is the first beat governed by this signature.
    """

    start_beat: int = Field(ge=1)
    numerator: int = Field(ge=1)
    denominator: int = Field(ge=1)


class Section(TimingModel):
    """
    A musical section.

    ``start_beat`` is preferred for referencing; ``start_time`` is kept
    for convenience. ``source_name`` preserves the original chart label;
    ``name`` is normalized (see the normalization task).
    """

    index: int = Field(ge=1)
    name: str
    source_name: str
    start_beat: int = Field(ge=1)
    start_time: float = Field(ge=0.0)


class TimingData(TimingModel):
    """
    Canonical, source-agnostic timing information.

    Produced by every ``TimingProvider`` (SNG, MIDI, CHART, Audio) and
    consumed by the ``SongMapBuilder``. It knows nothing about SNG, MIDI,
    CHART or librosa.

    ``offset`` is the time in seconds of the first beat (the music
    start); it defaults to 0 when the source does not provide one.
    """

    tempos: list[TempoSegment]
    beats: list[Beat]
    time_signatures: list[TimeSignature]
    sections: list[Section]
    offset: float = 0.0
