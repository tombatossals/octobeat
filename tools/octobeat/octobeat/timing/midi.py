from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Protocol, cast

from octobeat.timing.base import CorruptFileError


class _Tickable(Protocol):
    tick: int

DEFAULT_PPQ = 480


@dataclass(frozen=True, slots=True)
class MidiTempo:
    """A Set Tempo event: absolute tick and microseconds per quarter."""

    tick: int
    usec_per_quarter: int

    @property
    def bpm(self) -> float:
        return 60_000_000 / self.usec_per_quarter


@dataclass(frozen=True, slots=True)
class MidiTimeSignature:
    """A Time Signature meta event."""

    tick: int
    numerator: int
    denominator: int


@dataclass(frozen=True, slots=True)
class MidiText:
    """A Text meta event (used for section/marker labels)."""

    tick: int
    text: str


@dataclass(frozen=True, slots=True)
class MidiNote:
    """A note-on event (velocity > 0)."""

    tick: int
    pitch: int
    velocity: int
    track: int


@dataclass(slots=True)
class MidiTrack:
    """A parsed SMF track."""

    name: str
    tempos: list[MidiTempo]
    time_signatures: list[MidiTimeSignature]
    texts: list[MidiText]
    notes: list[MidiNote]


@dataclass(slots=True)
class MidiFile:
    """A parsed SMF file (format 0 or 1)."""

    format: int
    ppq: int
    tracks: list[MidiTrack]

    def all_tempos(self) -> list[MidiTempo]:
        return _merge_tracks(
            [tempo for track in self.tracks for tempo in track.tempos],
        )

    def all_time_signatures(self) -> list[MidiTimeSignature]:
        return _merge_tracks(
            [sig for track in self.tracks for sig in track.time_signatures],
        )

    def all_notes(self) -> list[MidiNote]:
        return sorted(
            (note for track in self.tracks for note in track.notes),
            key=lambda note: note.tick,
        )


def parse_midi(data: bytes) -> MidiFile:
    """
    Parse an SMF file.

    Raises ``CorruptFileError`` when the header or chunks are invalid.
    """

    if len(data) < 14 or data[:4] != b"MThd":
        raise CorruptFileError("Not a standard MIDI file.")

    _header_len = struct.unpack(">I", data[4:8])[0]
    fmt, ntrks, division = struct.unpack(">HHH", data[8:14])

    if division & 0x8000:
        raise CorruptFileError("SMPTE division is not supported.")

    ppq = division
    pos = 14
    tracks: list[MidiTrack] = []

    for track_index in range(ntrks):
        if pos + 8 > len(data) or data[pos:pos + 4] != b"MTrk":
            raise CorruptFileError("Truncated or invalid track chunk.")

        track_len = struct.unpack(">I", data[pos + 4:pos + 8])[0]
        track_data = data[pos + 8:pos + 8 + track_len]
        pos += 8 + track_len

        if pos > len(data):
            raise CorruptFileError("Track length exceeds file size.")

        tracks.append(
            _parse_track(track_data, track_index),
        )

    return MidiFile(
        format=fmt,
        ppq=ppq,
        tracks=tracks,
    )


def _parse_track(data: bytes, track_index: int) -> MidiTrack:
    name = ""
    tempos: list[MidiTempo] = []
    time_signatures: list[MidiTimeSignature] = []
    texts: list[MidiText] = []
    notes: list[MidiNote] = []

    i = 0
    tick = 0
    running_status: int | None = None

    while i < len(data):
        delta, i = _read_vlq(data, i)
        tick += delta

        if i >= len(data):
            raise CorruptFileError("Unterminated track.")

        byte = data[i]

        if byte == 0xFF:
            # Meta events are self-delimited. Some real-world charts (Rock
            # Band/Harmonix) continue the running status across meta events,
            # so we do NOT reset it here.
            i += 1
            if i >= len(data):
                raise CorruptFileError("Truncated meta event.")
            meta_type = data[i]
            i += 1
            length, i = _read_vlq(data, i)
            if i + length > len(data):
                raise CorruptFileError("Meta event length exceeds track.")
            payload = data[i:i + length]
            i += length

            if meta_type == 0x03:
                name = payload.decode("utf-8", errors="replace")
            elif meta_type == 0x51 and length == 3:
                usec = (payload[0] << 16) | (payload[1] << 8) | payload[2]
                tempos.append(MidiTempo(tick=tick, usec_per_quarter=usec))
            elif meta_type == 0x58 and length >= 2:
                numerator = payload[0]
                denominator = 2 ** payload[1]
                time_signatures.append(
                    MidiTimeSignature(
                        tick=tick,
                        numerator=numerator,
                        denominator=denominator,
                    ),
                )
            elif meta_type == 0x01:
                texts.append(
                    MidiText(
                        tick=tick,
                        text=payload.decode("utf-8", errors="replace"),
                    ),
                )
            # 0x2F (end of track) is ignored: parsing stops at chunk end.
        elif byte in (0xF0, 0xF7):
            i += 1
            length, i = _read_vlq(data, i)
            i += length
        elif byte & 0x80:
            running_status = byte
            status = byte
            i += 1

            if status & 0xF0 == 0x90:
                pitch, velocity, i = _read_data2(data, i)
                if velocity > 0:
                    notes.append(
                        MidiNote(
                            tick=tick,
                            pitch=pitch,
                            velocity=velocity,
                            track=track_index,
                        ),
                    )
            elif status & 0xF0 == 0x80:
                _pitch, _velocity, i = _read_data2(data, i)
            elif status & 0xF0 in (0xA0, 0xB0, 0xE0):
                _data1, _data2, i = _read_data2(data, i)
            elif status & 0xF0 in (0xC0, 0xD0):
                _data1, i = _read_data1(data, i)
            else:
                raise CorruptFileError("Invalid channel status byte.")
        else:
            if running_status is None:
                raise CorruptFileError("Running status without a previous status byte.")
            status = running_status

            if status & 0xF0 == 0x90:
                pitch, velocity, i = _read_data2(data, i)
                if velocity > 0:
                    notes.append(
                        MidiNote(
                            tick=tick,
                            pitch=pitch,
                            velocity=velocity,
                            track=track_index,
                        ),
                    )
            elif status & 0xF0 in (0x80, 0xA0, 0xB0, 0xE0):
                _data1, _data2, i = _read_data2(data, i)
            elif status & 0xF0 in (0xC0, 0xD0):
                _data1, i = _read_data1(data, i)
            else:
                raise CorruptFileError("Invalid channel status byte.")

    return MidiTrack(
        name=name,
        tempos=tempos,
        time_signatures=time_signatures,
        texts=texts,
        notes=notes,
    )


def _read_data1(data: bytes, i: int) -> tuple[int, int]:
    if i >= len(data):
        raise CorruptFileError("Truncated channel event.")
    return data[i], i + 1


def _read_data2(data: bytes, i: int) -> tuple[int, int, int]:
    if i + 1 >= len(data):
        raise CorruptFileError("Truncated channel event.")
    return data[i], data[i + 1], i + 2


def _read_vlq(data: bytes, i: int) -> tuple[int, int]:
    """Read a variable-length quantity, returning (value, next_index)."""

    value = 0

    while True:
        if i >= len(data):
            raise CorruptFileError("Truncated variable-length quantity.")
        byte = data[i]
        i += 1
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return value, i


def _merge_tracks[T](
    events: list[T],
) -> list[T]:
    return cast(
        list[T],
        sorted(
            events,
            key=lambda event: cast("_Tickable", event).tick,
        ),
    )
