"""Synthetic SNG fixtures for the timing providers.

Builds small, deterministic ``.sng`` containers (SNGPKG format) holding a
synthetic ``notes.mid`` chart, together with a manifest describing the
expected ground truth (tempo map, time signatures, beats, sections).

The fixtures are generated on the fly so the SNG parser can be
regression-tested without shipping multi-megabyte community charts.
"""

from __future__ import annotations

import json
import struct
from dataclasses import asdict, dataclass
from pathlib import Path

SNG_MAGIC = b"SNGPKG"
PPQ = 480

# MIDI note pitches used by the `BEAT` track (Rock Band convention).
DOWNBEAT_PITCH = 12
BEAT_PITCH = 13

CASE_NAMES = [
    "constant-tempo",
    "tempo-change",
    "multiple-timesig",
    "sections",
    "no-beat-track",
    "invalid-magic",
    "unsupported-version",
    "truncated",
    "corrupt-chart",
]


@dataclass(frozen=True, slots=True)
class SngFixture:
    """Ground truth of one synthetic SNG fixture."""

    name: str

    bpm: float | None

    tempo_map: list[dict[str, float]]

    time_signatures: list[dict[str, int]]

    beats: int

    downbeats: int

    sections: list[str]

    valid: bool


def build_sng_fixtures(output: Path) -> list[SngFixture]:
    """Generate all SNG fixtures and a manifest into ``output``."""

    output.mkdir(parents=True, exist_ok=True)

    fixtures = [
        _constant_tempo(),
        _tempo_change(),
        _multiple_timesig(),
        _sections(),
        _no_beat_track(),
        _invalid_magic(),
        _unsupported_version(),
        _truncated(),
        _corrupt_chart(),
    ]

    manifest = []

    for fixture in fixtures:
        build_sng_fixture(output / f"{fixture.name}.sng", fixture)

        manifest.append(asdict(fixture))

    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    return fixtures


def build_sng_fixture(path: Path, fixture: SngFixture) -> None:
    """Write a single ``.sng`` fixture (used by tests directly)."""

    path.write_bytes(build_sng_bytes(fixture))


def build_sng_bytes(fixture: SngFixture) -> bytes:
    """Build the full SNG container for a fixture.

    Valid fixtures ship a ``notes.mid``; invalid fixtures deliberately
    deviate (bad magic, unsupported version, truncation, corrupt chart).
    """

    if fixture.name == "invalid-magic":
        return b"NOTSNG" + build_sng_bytes(_constant_tempo())[6:]

    if fixture.name == "unsupported-version":
        base = build_sng_bytes(_constant_tempo())
        return base[:6] + struct.pack("<I", 99) + base[10:]

    chart = _build_notes_mid(fixture)

    if fixture.name == "corrupt-chart":
        # Deliberately break the SMF header so the chart is unparseable.
        chart = b"\x00\x00\x00\x00" + chart[4:][: len(chart) // 2]

    files = {
        "notes.mid": chart,
        "song.wav": _fixture_audio(fixture),
    }

    metadata = {
        "name": _song_title(fixture.name),
        "artist": "Fixture Band",
        "charter": "octobeat-fixtures",
        "song_length": str(_chart_duration_ms(fixture)),
    }

    sng = _build_sng_container(metadata, files)

    if fixture.name == "truncated":
        return sng[: len(sng) // 2]

    return sng


# --------------------------------------------------------------------------
# Ground-truth definitions
# --------------------------------------------------------------------------


def _constant_tempo() -> SngFixture:
    return SngFixture(
        name="constant-tempo",
        bpm=120.0,
        tempo_map=[{"tick": 0, "bpm": 120.0}],
        time_signatures=[{"tick": 0, "numerator": 4, "denominator": 4}],
        beats=16,
        downbeats=4,
        sections=["intro", "verse"],
        valid=True,
    )


def _tempo_change() -> SngFixture:
    return SngFixture(
        name="tempo-change",
        bpm=120.0,
        tempo_map=[
            {"tick": 0, "bpm": 120.0},
            {"tick": 8 * PPQ, "bpm": 150.0},
        ],
        time_signatures=[{"tick": 0, "numerator": 4, "denominator": 4}],
        beats=24,
        downbeats=6,
        sections=["intro", "verse"],
        valid=True,
    )


def _multiple_timesig() -> SngFixture:
    return SngFixture(
        name="multiple-timesig",
        bpm=100.0,
        tempo_map=[{"tick": 0, "bpm": 100.0}],
        time_signatures=[
            {"tick": 0, "numerator": 4, "denominator": 4},
            {"tick": 4 * PPQ, "numerator": 3, "denominator": 4},
        ],
        beats=16,
        downbeats=5,
        sections=["intro"],
        valid=True,
    )


def _sections() -> SngFixture:
    return SngFixture(
        name="sections",
        bpm=140.0,
        tempo_map=[{"tick": 0, "bpm": 140.0}],
        time_signatures=[{"tick": 0, "numerator": 4, "denominator": 4}],
        beats=32,
        downbeats=8,
        sections=[
            "intro",
            "verse 1",
            "chorus",
            "verse 2",
            "chorus",
            "bridge",
            "solo",
            "outro",
        ],
        valid=True,
    )


def _no_beat_track() -> SngFixture:
    return SngFixture(
        name="no-beat-track",
        bpm=90.0,
        tempo_map=[{"tick": 0, "bpm": 90.0}],
        time_signatures=[{"tick": 0, "numerator": 4, "denominator": 4}],
        beats=12,
        downbeats=3,
        sections=["intro", "verse"],
        valid=True,
    )


def _invalid_magic() -> SngFixture:
    return SngFixture(
        name="invalid-magic",
        bpm=None,
        tempo_map=[],
        time_signatures=[],
        beats=0,
        downbeats=0,
        sections=[],
        valid=False,
    )


def _unsupported_version() -> SngFixture:
    return SngFixture(
        name="unsupported-version",
        bpm=None,
        tempo_map=[],
        time_signatures=[],
        beats=0,
        downbeats=0,
        sections=[],
        valid=False,
    )


def _truncated() -> SngFixture:
    return SngFixture(
        name="truncated",
        bpm=None,
        tempo_map=[],
        time_signatures=[],
        beats=0,
        downbeats=0,
        sections=[],
        valid=False,
    )


def _corrupt_chart() -> SngFixture:
    return SngFixture(
        name="corrupt-chart",
        bpm=None,
        tempo_map=[],
        time_signatures=[],
        beats=0,
        downbeats=0,
        sections=[],
        valid=False,
    )


def _song_title(name: str) -> str:
    return name.replace("-", " ").title()


def _fixture_audio(fixture: SngFixture) -> bytes:
    """Generate a small WAV click track at the fixture's BPM.

    Provides decodable audio so ``SngSourceProvider`` can extract and
    decode it (the timing fixtures carry a synthetic recording that
    matches the chart).
    """

    import struct
    import wave
    from io import BytesIO

    bpm = fixture.tempo_map[0]["bpm"] if fixture.tempo_map else 120.0
    sr = 22050
    interval = 60.0 / bpm

    # Two bars of clicks (enough for the provider to decode and for a
    # beat analysis to recognise the tempo).
    duration = 8 * interval
    n = int(sr * duration)
    click_frames = int(0.03 * sr)

    samples = bytearray()

    for i in range(n):
        value = 0.0

        if i % int(sr * interval) < click_frames:
            value = 0.8

        samples += struct.pack(
            "<h",
            int(value * 32767),
        )

    buffer = BytesIO()

    with wave.open(buffer, "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(sr)
        file.writeframes(bytes(samples))

    return buffer.getvalue()


def _chart_duration_ms(fixture: SngFixture) -> int:
    """Estimated chart duration from the tempo map and beat count."""

    if not fixture.tempo_map:
        return 0

    seconds = 0.0
    prev_tick = 0
    prev_bpm = fixture.tempo_map[0]["bpm"]
    last_tick = (fixture.beats - 1) * PPQ

    for segment in fixture.tempo_map[1:]:
        tick = int(segment["tick"])
        bpm = float(segment["bpm"])
        seconds += (tick - prev_tick) * 60.0 / prev_bpm / PPQ
        prev_tick = tick
        prev_bpm = bpm

    seconds += (last_tick - prev_tick) * 60.0 / prev_bpm / PPQ

    return int(round(seconds * 1000))


# --------------------------------------------------------------------------
# SNG container writer
# --------------------------------------------------------------------------


def _build_sng_container(
    metadata: dict[str, str],
    files: dict[str, bytes],
) -> bytes:
    """Serialize an SNGPKG container with metadata, file index and
    XOR-masked file data (little-endian, per the SNG spec)."""

    version = 1
    xor_mask = bytes.fromhex("5df53c5fd712f192cb4fdde70959e35d")

    # Metadata section
    meta_payload = bytearray()
    for key, value in metadata.items():
        meta_payload += struct.pack("<i", len(key))
        meta_payload += key.encode("utf-8")
        meta_payload += struct.pack("<i", len(value))
        meta_payload += value.encode("utf-8")

    metadata_section = (
        struct.pack("<Q", 8 + len(meta_payload))
        + struct.pack("<Q", len(metadata))
        + meta_payload
    )

    # File index section: absolute offsets computed after laying out data.
    file_order = list(files.items())

    header_len = 6 + 4 + 16
    metadata_len = len(metadata_section)

    # Each index entry size is fixed once the names are known, so the
    # section length does not depend on the (unknown yet) offsets.
    index_entry_size = sum(
        1 + len(name.encode("utf-8")) + 8 + 8
        for name, _ in file_order
    )
    index_len = 8 + 8 + index_entry_size

    # File data starts after the fileDataLen (uint64) field.
    file_data_len = sum(len(content) for _, content in file_order)
    contents_start = header_len + metadata_len + index_len + 8

    index_payload = bytearray()
    cursor = contents_start
    for name, content in file_order:
        name_bytes = name.encode("utf-8")
        index_payload += (
            struct.pack("<B", len(name_bytes))
            + name_bytes
            + struct.pack("<Q", len(content))
            + struct.pack("<Q", cursor)
        )
        cursor += len(content)

    file_index_section = (
        struct.pack("<Q", 8 + len(index_payload))
        + struct.pack("<Q", len(file_order))
        + index_payload
    )

    # File data section
    masked = []
    for _, content in file_order:
        raw = bytearray(content)
        for i in range(len(raw)):
            raw[i] ^= xor_mask[i % 16] ^ (i & 0xFF)
        masked.append(raw)

    file_data_section = (
        struct.pack("<Q", file_data_len) + b"".join(masked)
    )

    return (
        SNG_MAGIC
        + struct.pack("<I", version)
        + xor_mask
        + metadata_section
        + file_index_section
        + file_data_section
    )


# --------------------------------------------------------------------------
# SMF (MIDI) writer
# --------------------------------------------------------------------------


def _build_notes_mid(fixture: SngFixture) -> bytes:
    """Build a synthetic ``notes.mid`` (SMF format 1, 480 PPQ)."""

    tracks = [
        _tempo_track(fixture),
        _events_track(fixture),
        _beat_track(fixture),
    ]

    if fixture.name == "no-beat-track":
        tracks = [
            _tempo_track(fixture),
            _events_track(fixture),
        ]

    payload = b"".join(_smf_track(track) for track in tracks)

    return (
        b"MThd"
        + struct.pack(">I", 6)
        + struct.pack(">HHH", 1, len(tracks), PPQ)
        + payload
    )


def _tempo_track(fixture: SngFixture) -> list[tuple[int, bytes, bytes]]:
    """Track 0: tempo map + time signature events, ordered by tick."""

    events: list[tuple[int, bytes, bytes]] = [
        (0, b"\xff\x03", b"fixture"),
    ]

    ordered: list[tuple[int, bytes, bytes]] = []

    for segment in fixture.tempo_map:
        tick = int(segment["tick"])
        bpm = float(segment["bpm"])
        usec = int(round(60_000_000 / bpm))
        ordered.append(
            (
                tick,
                b"\xff\x51",
                struct.pack(">I", usec)[1:],
            )
        )

    for sig in fixture.time_signatures:
        tick = int(sig["tick"])
        num = int(sig["numerator"])
        denom = int(sig["denominator"])
        # denominator is stored as power of two: 4 -> 2.
        denom_pow = {4: 2, 2: 1, 8: 3}.get(denom, 2)
        ordered.append(
            (
                tick,
                b"\xff\x58",
                bytes([num, denom_pow, 24, 8]),
            )
        )

    prev_tick = 0
    for tick, event, data in sorted(ordered):
        events.append((tick - prev_tick, event, data))
        prev_tick = tick

    events.append((0, b"\xff\x2f", b""))

    return events


def _events_track(fixture: SngFixture) -> list[tuple[int, bytes, bytes]]:
    """Track 5: section + music marker text events.

    Events are emitted ordered by tick (deltas are always positive)."""

    events: list[tuple[int, bytes, bytes]] = [
        (0, b"\xff\x03", b"EVENTS")
    ]

    text_events: list[tuple[int, bytes]] = []

    for index, section in enumerate(fixture.sections):
        text_events.append(
            (
                index * 4 * PPQ,
                f"[section {section}]".encode(),
            )
        )

    if fixture.name == "constant-tempo":
        text_events.append((2 * PPQ, b"[music_start]"))

    # End marker just after the last beat, so parsers can bound the chart.
    if fixture.beats > 0:
        text_events.append((fixture.beats * PPQ, b"[end]"))

    prev_tick = 0
    for tick, text in sorted(text_events):
        events.append(
            (
                tick - prev_tick,
                b"\xff\x01",
                text,
            )
        )
        prev_tick = tick

    events.append((0, b"\xff\x2f", b""))

    return events


def _beat_track(fixture: SngFixture) -> list[tuple[int, bytes, bytes]]:
    """Track 7: explicit beats (pitch 12 downbeat, 13 regular).

    Beat positions depend on the time signatures; a time signature change
    from 4/4 to 3/4 changes the downbeat spacing."""

    events: list[tuple[int, bytes, bytes]] = [
        (0, b"\xff\x03", b"BEAT")
    ]

    # Determine bar length (in beats) per tick range.
    def beats_per_bar(tick: int) -> int:
        sig = fixture.time_signatures[-1]
        for candidate in fixture.time_signatures:
            if tick >= int(candidate["tick"]):
                sig = candidate
        return int(sig["numerator"])

    beats = fixture.beats
    ticks = []
    pitch = []
    beat_in_bar = 0
    for _ in range(beats):
        tick = _ * PPQ
        ticks.append(tick)
        pitch.append(DOWNBEAT_PITCH if beat_in_bar == 0 else BEAT_PITCH)
        beat_in_bar = (beat_in_bar + 1) % beats_per_bar(tick)

    prev_tick = 0
    events_list: list[tuple[int, bytes, bytes]] = []
    for tick, p in zip(ticks, pitch, strict=True):
        events_list.append(
            (
                tick - prev_tick,
                b"\x90",
                bytes([p, 100]),
            )
        )
        prev_tick = tick
        note_off_tick = tick + PPQ // 8
        events_list.append(
            (
                note_off_tick - prev_tick,
                b"\x80",
                bytes([p, 0]),
            )
        )
        prev_tick = note_off_tick

    events.append((0, b"\xff\x2f", b""))

    return events + events_list


def _smf_track(events: list[tuple[int, bytes, bytes]]) -> bytes:
    """Serialize one SMF track (MTrk) with VLQ deltas.

    ``event`` is a status byte (meta ``0xFF`` or channel). For meta events
    the payload length is emitted as a VLQ after the event type."""

    payload = bytearray()

    for delta, event, data in events:
        payload += _vlq(delta)
        payload += event
        if event[0] == 0xFF:
            payload += _vlq(len(data))
        payload += data

    return b"MTrk" + struct.pack(">I", len(payload)) + payload


def _vlq(value: int) -> bytes:
    """MIDI variable-length quantity."""

    result = bytearray([value & 0x7F])
    value >>= 7
    while value:
        result.insert(0, (value & 0x7F) | 0x80)
        value >>= 7
    return bytes(result)
