"""SongMapBuilder: converts canonical TimingData into a SongMap.

This is the single conversion path used by every timing source:

    SNG → TimingData → SongMap
    Audio → BeatEngine → TimingData → SongMap

The builder knows nothing about SNG, MIDI, CHART or librosa.
"""

from __future__ import annotations

from octobeat.models.songmap import (
    SCHEMA_ID,
    SONGMAP_VERSION,
    Bar,
    Section,
    SongMap,
    SongMetadata,
    Source,
    TempoSegment,
    Timing,
)
from octobeat.models.songmap import (
    Beat as SongMapBeat,
)
from octobeat.models.timing import TimingData
from octobeat.sections import normalize_section_name

DEFAULT_TIME_SIGNATURE = "4/4"
DEFAULT_BEATS_PER_BAR = 4


def build_songmap(
    timing_data: TimingData,
    *,
    title: str,
    duration: float,
    source: Source,
    source_kind: str,
    generated_by: str,
    created_at: str,
    offset: float = 0.0,
    confidence: float = 1.0,
    downbeat_shift: int = 0,
    count_in_start: float | None = None,
    song_start: float | None = None,
    count_in_clicks: list[float] | None = None,
) -> SongMap:
    """
    Build a complete SongMap from canonical ``TimingData``.

    ``source_kind`` is recorded in ``timing.source`` (e.g. ``"sng"``,
    ``"midi"``, ``"chart"``, ``"audio-analysis"``). ``downbeat_shift``
    is the audio-detection residue (0-based) of the beat that begins a
    bar; structured charts start on a downbeat so it defaults to 0.

    ``count_in_start`` and ``song_start`` describe a count-in lead-in
    before the music starts; ``song_start`` defaults to ``offset`` when
    not provided.
    """

    beats = _build_beats(timing_data)
    bars = _build_bars(timing_data, downbeat_shift)
    sections = _build_sections(timing_data)
    tempo_map = _build_tempo_map(timing_data)

    return SongMap(
        version=SONGMAP_VERSION,
        schema=SCHEMA_ID,
        generatedBy=generated_by,
        createdAt=created_at,
        metadata=SongMetadata(
            title=title,
            duration=round(duration, 3),
            source=source,
        ),
        timing=Timing(
            bpm=_global_bpm(timing_data),
            offset=round(offset, 3),
            timeSignature=_time_signature(timing_data),
            confidence=round(confidence, 2),
            tempoMap=tempo_map,
            source=source_kind,
            countInStart=(
                round(count_in_start, 3)
                if count_in_start is not None
                else None
            ),
            songStart=(
                round(song_start, 3)
                if song_start is not None
                else round(offset, 3)
            ),
            countInClicks=(
                [
                    round(time, 3)
                    for time in count_in_clicks
                ]
                if count_in_clicks
                else None
            ),
        ),
        beats=beats,
        bars=bars,
        sections=sections,
    )


def _build_beats(timing_data: TimingData) -> list[SongMapBeat]:
    return [
        SongMapBeat(
            index=beat.index,
            time=beat.time,
        )
        for beat in timing_data.beats
    ]


def _build_bars(
    timing_data: TimingData,
    downbeat_shift: int = 0,
) -> list[Bar]:
    """Group beats into bars.

    The first bar starts on the first downbeat. Structured charts
    declare it via the time signatures; audio analysis may detect a
    ``downbeat_shift`` residue (a recording beginning on a pickup), which
    shifts the grid before bar grouping.
    """

    beats = timing_data.beats
    if not beats:
        return []

    signatures = timing_data.time_signatures

    beats_per_bar = (
        signatures[0].numerator
        if signatures
        else DEFAULT_BEATS_PER_BAR
    )

    first_beat = (
        signatures[0].start_beat
        if signatures
        else beats[0].index
    )

    residue = (first_beat - 1) % beats_per_bar
    first_beat += (downbeat_shift - residue) % beats_per_bar

    last_beat = beats[-1].index

    bars: list[Bar] = []
    bar_index = 1
    cursor = first_beat

    while cursor <= last_beat:
        bars.append(
            Bar(
                index=bar_index,
                firstBeat=cursor,
            ),
        )
        bar_index += 1
        cursor += _beats_per_bar_at(timing_data, cursor)

    return bars


def _beats_per_bar_at(timing_data: TimingData, beat: int) -> int:
    """Beats per bar for the signature active at ``beat`` (1-based)."""

    signature = None
    for candidate in timing_data.time_signatures:
        if beat >= candidate.start_beat:
            signature = candidate

    if signature is None:
        return DEFAULT_BEATS_PER_BAR

    return signature.numerator


def _build_sections(timing_data: TimingData) -> list[Section]:
    sections: list[Section] = []

    for section in timing_data.sections:
        name = normalize_section_name(section.name)
        sections.append(
            Section(
                index=section.index,
                name=name,
                startBeat=section.start_beat,
                startTime=section.start_time,
                sourceName=_source_name(section.source_name, name),
            ),
        )

    return sections


def _source_name(source_name: str, normalized: str) -> str | None:
    """Keep the original chart label when it carries extra meaning.

    ``"verse 1"`` → ``"verse 1"``; ``"intro"`` → ``None`` (only a case
    difference from ``"Intro"``).
    """

    if source_name.strip().lower() == normalized.lower():
        return None

    return source_name


def _build_tempo_map(timing_data: TimingData) -> list[TempoSegment]:
    return [
        TempoSegment(
            time=segment.start_time,
            bpm=segment.bpm,
        )
        for segment in timing_data.tempos
    ]


def _global_bpm(timing_data: TimingData) -> float:
    """The global BPM: the tempo of the first segment (most charts have
    a single dominant tempo; multi-segment maps keep the first)."""

    if not timing_data.tempos:
        return 120.0

    return timing_data.tempos[0].bpm


def _time_signature(timing_data: TimingData) -> str:
    """The time signature string.

    Prefers the signature active at beat 1; otherwise the first one.
    """

    if timing_data.beats:
        first_beat = timing_data.beats[0].index
        for signature in timing_data.time_signatures:
            if signature.start_beat <= first_beat:
                return f"{signature.numerator}/{signature.denominator}"

    if timing_data.time_signatures:
        first = timing_data.time_signatures[0]
        return f"{first.numerator}/{first.denominator}"

    return DEFAULT_TIME_SIGNATURE
