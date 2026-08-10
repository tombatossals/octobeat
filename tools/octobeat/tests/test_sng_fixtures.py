from __future__ import annotations

import json
import struct

import pytest

from octobeat.fixtures import SNG_CASE_NAMES, build_sng_fixtures

PPQ = 480

# Minimal SMF/MIDI decoding helpers used by the tests to verify what the
# fixtures actually contain (independent of the SNG parser under test).


def _sng_sections(path) -> tuple[bytes, int, dict, list[tuple[str, int, int]]]:
    data = path.read_bytes()

    assert data[:6] == b"SNGPKG"

    version = struct.unpack("<I", data[6:10])[0]
    pos = 26

    _meta_len = struct.unpack("<Q", data[pos : pos + 8])[0]
    pos += 8
    meta_count = struct.unpack("<Q", data[pos : pos + 8])[0]
    pos += 8

    meta: dict[str, str] = {}
    for _ in range(meta_count):
        key_len = struct.unpack("<i", data[pos : pos + 4])[0]
        pos += 4
        key = data[pos : pos + key_len].decode("utf-8")
        pos += key_len
        value_len = struct.unpack("<i", data[pos : pos + 4])[0]
        pos += 4
        value = data[pos : pos + value_len].decode("utf-8")
        pos += value_len
        meta[key] = value

    _file_meta_len = struct.unpack("<Q", data[pos : pos + 8])[0]
    pos += 8
    file_count = struct.unpack("<Q", data[pos : pos + 8])[0]
    pos += 8

    files: list[tuple[str, int, int]] = []
    for _ in range(file_count):
        name_len = data[pos]
        pos += 1
        name = data[pos : pos + name_len].decode("utf-8")
        pos += name_len
        content_len = struct.unpack("<Q", data[pos : pos + 8])[0]
        pos += 8
        content_index = struct.unpack("<Q", data[pos : pos + 8])[0]
        pos += 8
        files.append((name, content_len, content_index))

    return data, version, meta, files


def _extract_file(path, name: str) -> bytes | None:
    data, _, _, files = _sng_sections(path)
    xor_mask = data[10:26]

    for file_name, content_len, content_index in files:
        if file_name != name:
            continue
        raw = bytearray(data[content_index : content_index + content_len])
        for i in range(len(raw)):
            raw[i] ^= xor_mask[i % 16] ^ (i & 0xFF)
        return bytes(raw)

    return None


def _midi_tempo_map(mid: bytes) -> list[tuple[int, float]]:
    assert mid[:4] == b"MThd"

    _fmt, _ntrks, division = struct.unpack(">HHH", mid[8:14])
    assert division == PPQ

    tempos: list[tuple[int, float]] = []

    # Only look at the first track.
    track_len = struct.unpack(">I", mid[18:22])[0]
    track = mid[22 : 22 + track_len]

    i = 0
    tick = 0
    while i < len(track):
        delta = 0
        while True:
            byte = track[i]
            i += 1
            delta = (delta << 7) | (byte & 0x7F)
            if not byte & 0x80:
                break
        tick += delta

        status = track[i]
        if status == 0xFF:
            meta_type = track[i + 1]
            i += 2
            length = track[i]
            i += 1
            data = track[i : i + length]
            i += length

            if meta_type == 0x51 and length == 3:
                usec = (data[0] << 16) | (data[1] << 8) | data[2]
                tempos.append((tick, round(60_000_000 / usec, 2)))
        elif status in (0xF0, 0xF7):
            length = track[i + 1]
            i += length + 2
        else:
            if (status & 0xF0) in (0xC0, 0xD0):
                i += 1
            else:
                i += 2

    return tempos


@pytest.fixture
def fixtures(tmp_path) -> None:
    build_sng_fixtures(tmp_path)
    return tmp_path


def test_case_names():
    assert SNG_CASE_NAMES == [
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


def test_manifest_exists(fixtures):
    manifest = fixtures / "manifest.json"
    assert manifest.exists()

    entries = json.loads(manifest.read_text(encoding="utf-8"))

    assert {entry["name"] for entry in entries} <= set(SNG_CASE_NAMES)


def test_valid_containers_are_sngpkg(fixtures):
    for name in ("constant-tempo", "tempo-change", "multiple-timesig", "sections"):
        data = (fixtures / f"{name}.sng").read_bytes()
        assert data[:6] == b"SNGPKG"


def test_invalid_magic_rejected(fixtures):
    data = (fixtures / "invalid-magic.sng").read_bytes()
    assert data[:6] != b"SNGPKG"


def test_unsupported_version(fixtures):
    data, version, _, _ = _sng_sections(fixtures / "unsupported-version.sng")
    assert data[:6] == b"SNGPKG"
    assert version == 99


def test_metadata(fixtures):
    _, _, meta, files = _sng_sections(fixtures / "constant-tempo.sng")

    assert meta["name"] == "Constant Tempo"
    assert meta["artist"] == "Fixture Band"

    names = {name for name, _, _ in files}
    assert "notes.mid" in names
    assert "song.wav" in names


def test_constant_tempo_ground_truth(fixtures):
    mid = _extract_file(fixtures / "constant-tempo.sng", "notes.mid")
    assert mid is not None

    assert _midi_tempo_map(mid) == [(0, 120.0)]


def test_tempo_change_ground_truth(fixtures):
    mid = _extract_file(fixtures / "tempo-change.sng", "notes.mid")
    assert mid is not None

    assert _midi_tempo_map(mid) == [(0, 120.0), (8 * PPQ, 150.0)]


def test_corrupt_chart_has_mid_magic_missing(fixtures):
    mid = _extract_file(fixtures / "corrupt-chart.sng", "notes.mid")
    assert mid is not None
    # Chart is deliberately truncated mid-header.
    assert not mid[:4] == b"MThd"


def test_truncated_container(fixtures):
    data = (fixtures / "truncated.sng").read_bytes()
    full = (fixtures / "constant-tempo.sng").read_bytes()
    assert len(data) < len(full)
