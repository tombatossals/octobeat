from __future__ import annotations

import struct
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from octobeat.models.timing import (
    Beat,
    Section,
    TempoSegment,
    TimingData,
)
from octobeat.models.timing import (
    TimeSignature as TimingSignature,
)
from octobeat.timing.base import (
    CorruptFileError,
    MissingChartError,
    TimingProvider,
    UnsupportedVersionError,
)
from octobeat.timing.midi import (
    MidiFile,
    MidiTempo,
    MidiTimeSignature,
    parse_midi,
)

SNG_MAGIC = b"SNGPKG"
SUPPORTED_VERSION = 1

# MIDI note pitches used by the `BEAT` track (Rock Band convention).
DOWNBEAT_PITCH = 12
BEAT_PITCH = 13

# Track names that identify the section/marker and beat tracks.
EVENTS_TRACK = "EVENTS"
BEAT_TRACK = "BEAT"

# Marker text pattern for section events in the EVENTS track.
SECTION_PREFIX = "[section "


@dataclass(frozen=True, slots=True)
class SngFile:
    """A parsed SNG container (before unmasking the payload files)."""

    version: int
    metadata: dict[str, str]
    files: dict[str, tuple[int, int]]  # name -> (length, absolute offset)


class SNGProvider(TimingProvider):
    """
    Timing provider for SNG (Clone Hero / YARG) containers.

    Parses the SNGPKG container, extracts the embedded ``notes.mid``
    chart and converts it into canonical ``TimingData``.
    """

    @classmethod
    def supports(cls, source: str) -> bool:
        return str(source).lower().endswith(".sng")

    def load(self, source: str) -> TimingData:
        path = Path(source)
        data = path.read_bytes()
        sng = parse_sng_container(data)
        mid = self._extract_chart(sng, data)
        return midi_to_timing(mid)

    def _extract_chart(self, sng: SngFile, data: bytes) -> bytes:
        for name in ("notes.mid", "notes.chart"):
            listing = sng.files.get(name)
            if listing is not None:
                return _unmask_file(data, listing)

        raise MissingChartError("SNG container has no notes.mid/notes.chart.")


def extract_file(data: bytes, name: str) -> bytes:
    """Unmask and return the raw bytes of a file inside the container."""

    sng = parse_sng_container(data)

    listing = sng.files.get(name)
    if listing is None:
        raise MissingChartError(f"SNG container has no '{name}' file.")

    return _unmask_file(data, listing)


# Preferred audio files inside an SNG, in priority order.
PREFERRED_AUDIO = (
    "song.opus",
    "song.ogg",
    "song.wav",
    "song.mp3",
    "guitar.opus",
    "guitar.ogg",
)


def extract_audio(data: bytes) -> tuple[str, bytes]:
    """
    Extract the preferred full-mix audio track from the container.

    Returns ``(name, bytes)``. Raises ``MissingChartError`` when the
    container has no usable audio track.
    """

    sng = parse_sng_container(data)

    for name in PREFERRED_AUDIO:
        listing = sng.files.get(name)
        if listing is not None:
            return name, _unmask_file(data, listing)

    raise MissingChartError(
        "SNG container has no usable audio track.",
    )


def parse_sng_container(data: bytes) -> SngFile:
    """
    Parse the SNGPKG container structure.

    Raises ``CorruptFileError``, ``UnsupportedVersionError`` or
    ``MissingChartError`` with a message suitable for CLI fallback.
    """

    if len(data) < 26 or data[:6] != SNG_MAGIC:
        raise CorruptFileError("Not an SNG container (bad magic).")

    version = struct.unpack("<I", data[6:10])[0]

    if version != SUPPORTED_VERSION:
        raise UnsupportedVersionError(f"Unsupported SNG version {version}.")

    pos = 26

    metadata, pos = _read_metadata(data, pos)
    files, _pos = _read_file_index(data, pos)

    return SngFile(
        version=version,
        metadata=metadata,
        files=files,
    )


def _read_metadata(data: bytes, pos: int) -> tuple[dict[str, str], int]:
    if pos + 16 > len(data):
        raise CorruptFileError("Truncated SNG metadata section.")

    metadata_len = struct.unpack("<Q", data[pos:pos + 8])[0]
    pos += 8
    pair_count = struct.unpack("<Q", data[pos:pos + 8])[0]
    pos += 8

    if pos + metadata_len - 8 > len(data):
        raise CorruptFileError("SNG metadata section exceeds file size.")

    metadata: dict[str, str] = {}

    for _ in range(pair_count):
        if pos + 4 > len(data):
            raise CorruptFileError("Truncated SNG metadata pair.")
        key_len = struct.unpack("<i", data[pos:pos + 4])[0]
        pos += 4
        if key_len < 0 or pos + key_len > len(data):
            raise CorruptFileError("Invalid SNG metadata key.")
        key = data[pos:pos + key_len].decode("utf-8", errors="replace")
        pos += key_len

        if pos + 4 > len(data):
            raise CorruptFileError("Truncated SNG metadata value.")
        value_len = struct.unpack("<i", data[pos:pos + 4])[0]
        pos += 4
        if value_len < 0 or pos + value_len > len(data):
            raise CorruptFileError("Invalid SNG metadata value.")
        value = data[pos:pos + value_len].decode("utf-8", errors="replace")
        pos += value_len

        metadata[key] = value

    return metadata, pos


def _read_file_index(
    data: bytes,
    pos: int,
) -> tuple[dict[str, tuple[int, int]], int]:
    if pos + 16 > len(data):
        raise CorruptFileError("Truncated SNG file index.")

    index_len = struct.unpack("<Q", data[pos:pos + 8])[0]
    pos += 8
    file_count = struct.unpack("<Q", data[pos:pos + 8])[0]
    pos += 8

    if pos + index_len - 8 > len(data):
        raise CorruptFileError("SNG file index exceeds file size.")

    files: dict[str, tuple[int, int]] = {}

    for _ in range(file_count):
        if pos + 1 > len(data):
            raise CorruptFileError("Truncated SNG file entry.")
        name_len = data[pos]
        pos += 1
        if pos + name_len + 16 > len(data):
            raise CorruptFileError("Invalid SNG file name.")
        name = data[pos:pos + name_len].decode("utf-8", errors="replace")
        pos += name_len

        content_len = struct.unpack("<Q", data[pos:pos + 8])[0]
        pos += 8
        content_index = struct.unpack("<Q", data[pos:pos + 8])[0]
        pos += 8

        if content_index + content_len > len(data):
            raise CorruptFileError("SNG file data exceeds file size.")

        files[name] = (content_len, content_index)

    return files, pos


def _unmask_file(data: bytes, listing: tuple[int, int]) -> bytes:
    """Read a file's bytes from the container and unmask them."""

    content_len, content_index = listing
    xor_mask = data[10:26]
    raw = bytearray(data[content_index:content_index + content_len])

    for i in range(len(raw)):
        raw[i] ^= xor_mask[i % 16] ^ (i & 0xFF)

    return bytes(raw)


# --------------------------------------------------------------------------
# MIDI → TimingData
# --------------------------------------------------------------------------


def midi_to_timing(mid_bytes: bytes) -> TimingData:
    """
    Convert a ``notes.mid`` chart into canonical ``TimingData``.

    Raises ``CorruptFileError`` when the chart is not a valid MIDI file.
    """

    mid = parse_midi(mid_bytes)
    ppq = mid.ppq

    tempos = mid.all_tempos()
    if not tempos:
        raise CorruptFileError("Chart has no tempo map.")

    signatures = mid.all_time_signatures()

    beat_ticks, _downbeat_ticks = _extract_beats(mid)

    tick_to_time = _build_tick_converter(tempos, ppq)

    beats = [
        Beat(
            index=index,
            time=round(tick_to_time(tick), 3),
        )
        for index, tick in enumerate(beat_ticks, start=1)
    ]

    beat_index_at = {
        tick: index
        for index, tick in enumerate(beat_ticks, start=1)
    }

    tempo_segments = _build_tempo_segments(
        tempos,
        ppq,
        beat_ticks,
        beat_index_at,
    )

    time_signatures = _build_time_signatures(
        signatures,
        beat_ticks,
    )

    sections = _build_sections(
        mid,
        tick_to_time,
        beat_ticks,
    )

    return TimingData(
        tempos=tempo_segments,
        beats=beats,
        time_signatures=time_signatures,
        sections=sections,
        offset=round(beats[0].time if beats else 0.0, 3),
    )


def _extract_beats(mid: MidiFile) -> tuple[list[int], list[int]]:
    """Return (beat_ticks, downbeat_ticks) from the BEAT track.

    Falls back to deriving beats from the tempo map when there is no
    BEAT track. Downbeats are bar starts (pitch 12 in the BEAT track,
    or the first beat of every bar derived from the time signature).
    """

    for track in mid.tracks:
        if track.name.upper() == BEAT_TRACK:
            notes = sorted(
                (note for note in track.notes if note.velocity > 0),
                key=lambda note: note.tick,
            )
            if not notes:
                break
            beat_ticks = [note.tick for note in notes]
            downbeat_ticks = [
                note.tick for note in notes if note.pitch == DOWNBEAT_PITCH
            ]
            return beat_ticks, downbeat_ticks

    return _derive_beats(mid)


def _derive_beats(mid: MidiFile) -> tuple[list[int], list[int]]:
    """Derive the beat grid from the tempo map and time signatures.

    The grid starts at tick 0 and advances one beat (``ppq`` ticks) at a
    time until the chart's ``[end]`` marker (or the last event tick when
    no marker exists).
    """

    ppq = mid.ppq
    tempos = mid.all_tempos()
    if not tempos:
        return [], []

    last_tick = _chart_end_tick(mid)

    signatures = mid.all_time_signatures()

    def beats_per_bar(tick: int) -> int:
        sig = signatures[-1] if signatures else None
        for candidate in signatures:
            if tick >= candidate.tick:
                sig = candidate
        return sig.numerator if sig else 4

    beat_ticks: list[int] = []
    downbeat_ticks: list[int] = []
    tick = 0
    beat_in_bar = 0

    while tick <= last_tick:
        beat_ticks.append(tick)
        if beat_in_bar == 0:
            downbeat_ticks.append(tick)
        beat_in_bar = (beat_in_bar + 1) % beats_per_bar(tick)
        tick += ppq

    return beat_ticks, downbeat_ticks


def _chart_end_tick(mid: MidiFile) -> int:
    """Last meaningful tick of the chart: the ``[end]`` marker if present,
    otherwise the latest text/note/tempo tick across all tracks."""

    end_marker = None
    latest = 0

    for track in mid.tracks:
        for text in track.texts:
            latest = max(latest, text.tick)
            if text.text.strip() == "[end]":
                end_marker = text.tick
        for note in track.notes:
            latest = max(latest, note.tick)

    for tempo in mid.all_tempos():
        latest = max(latest, tempo.tick)

    if end_marker is not None:
        return max(0, end_marker - mid.ppq)

    return latest


def _build_tick_converter(
    tempos: list[MidiTempo],
    ppq: int,
) -> Callable[[int], float]:
    """
    Return ``tick_to_time(tick)`` integrating the tempo map.

    ``tempos`` must be non-empty and sorted by tick.
    """

    def tick_to_time(tick: int) -> float:
        seconds = 0.0
        prev_tick = 0
        prev_usec = tempos[0].usec_per_quarter

        for tempo in tempos[1:]:
            if tick <= tempo.tick:
                break
            seconds += (tempo.tick - prev_tick) * prev_usec / 1_000_000 / ppq
            prev_tick = tempo.tick
            prev_usec = tempo.usec_per_quarter

        seconds += (tick - prev_tick) * prev_usec / 1_000_000 / ppq

        return seconds

    return tick_to_time


def _build_tempo_segments(
    tempos: list[MidiTempo],
    ppq: int,
    beat_ticks: list[int],
    beat_index_at: dict[int, int],
) -> list[TempoSegment]:
    tick_to_time = _build_tick_converter(tempos, ppq)

    segments: list[TempoSegment] = []

    for tempo in tempos:
        beat = beat_index_at.get(tempo.tick)
        if beat is None:
            beat = _first_beat_after(beat_ticks, tempo.tick)
        segments.append(
            TempoSegment(
                start_beat=beat,
                start_time=round(tick_to_time(tempo.tick), 3),
                bpm=round(tempo.bpm, 2),
            ),
        )

    return segments


def _first_beat_after(beat_ticks: list[int], tick: int) -> int:
    for index, beat_tick in enumerate(beat_ticks, start=1):
        if beat_tick >= tick:
            return index
    return len(beat_ticks) if beat_ticks else 1


def _build_time_signatures(
    signatures: list[MidiTimeSignature],
    beat_ticks: list[int],
) -> list[TimingSignature]:
    result: list[TimingSignature] = []

    for signature in signatures:
        beat = _first_beat_after(beat_ticks, signature.tick)
        result.append(
            TimingSignature(
                start_beat=beat,
                numerator=signature.numerator,
                denominator=signature.denominator,
            ),
        )

    return result


def _build_sections(
    mid: MidiFile,
    tick_to_time: Callable[[int], float],
    beat_ticks: list[int],
) -> list[Section]:
    sections: list[Section] = []

    events_track = next(
        (track for track in mid.tracks if track.name.upper() == EVENTS_TRACK),
        None,
    )

    if events_track is None:
        return sections

    for text in events_track.texts:
        label = text.text
        if label.startswith(SECTION_PREFIX) and label.endswith("]"):
            source_name = label[len(SECTION_PREFIX):-1]
            beat = _first_beat_after(beat_ticks, text.tick)
            sections.append(
                Section(
                    index=len(sections) + 1,
                    name=source_name,
                    source_name=source_name,
                    start_beat=beat,
                    start_time=round(tick_to_time(text.tick), 3),
                ),
            )

    return sections
