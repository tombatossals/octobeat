from __future__ import annotations

import pytest

from octobeat.fixtures import build_sng_fixtures
from octobeat.timing import (
    SNGProvider,
    get_timing_provider,
    supports_timing_source,
)
from octobeat.timing.base import (
    CorruptFileError,
    UnsupportedVersionError,
)


@pytest.fixture
def fixtures(tmp_path):
    build_sng_fixtures(tmp_path)
    return tmp_path


@pytest.fixture
def provider() -> SNGProvider:
    return SNGProvider()


def _load(provider: SNGProvider, fixtures, name: str):
    return provider.load(str(fixtures / f"{name}.sng"))


# --------------------------------------------------------------------------
# Provider interface / factory
# --------------------------------------------------------------------------


def test_supports_sng_extension():
    assert SNGProvider.supports("song.sng")
    assert SNGProvider.supports("SONG.SNG")


def test_does_not_support_other_extensions():
    assert not SNGProvider.supports("song.mid")
    assert not SNGProvider.supports("song.chart")


def test_factory_resolves_sng():
    provider = get_timing_provider("song.sng")
    assert isinstance(provider, SNGProvider)


def test_factory_rejects_unknown_source():
    with pytest.raises(ValueError):
        get_timing_provider("song.mid")


def test_supports_timing_source():
    assert supports_timing_source("song.sng")
    assert not supports_timing_source("song.wav")


# --------------------------------------------------------------------------
# Metadata and basic timing
# --------------------------------------------------------------------------


def test_metadata_extracted(provider, fixtures):
    td = _load(provider, fixtures, "constant-tempo")
    assert len(td.beats) == 16
    assert td.tempos[0].bpm == 120.0


def test_constant_tempo_beats(provider, fixtures):
    td = _load(provider, fixtures, "constant-tempo")

    assert [beat.index for beat in td.beats] == list(
        range(1, 17)
    )

    # 120 BPM -> 0.5s per beat.
    assert td.beats[0].time == 0.0
    assert td.beats[3].time == 1.5
    assert td.beats[-1].time == 7.5


def test_tempo_change_segments(provider, fixtures):
    td = _load(provider, fixtures, "tempo-change")

    assert [(t.bpm, t.start_beat) for t in td.tempos] == [
        (120.0, 1),
        (150.0, 9),
    ]

    # Beats remain continuous across the tempo change.
    assert len(td.beats) == 24
    assert [b.index for b in td.beats] == list(range(1, 25))


def test_multiple_time_signatures(provider, fixtures):
    td = _load(provider, fixtures, "multiple-timesig")

    assert [(ts.numerator, ts.denominator, ts.start_beat) for ts in td.time_signatures] == [
        (4, 4, 1),
        (3, 4, 5),
    ]


def test_sections_extracted(provider, fixtures):
    td = _load(provider, fixtures, "sections")

    names = [section.name for section in td.sections]
    assert names == [
        "intro",
        "verse 1",
        "chorus",
        "verse 2",
        "chorus",
        "bridge",
        "solo",
        "outro",
    ]

    # Sections reference beats and times.
    assert td.sections[0].start_beat == 1
    assert td.sections[1].start_beat == 5


def test_no_beat_track_derives_beats(provider, fixtures):
    td = _load(provider, fixtures, "no-beat-track")

    # No BEAT track in the chart; beats derived from the tempo map.
    assert len(td.beats) == 12
    assert [b.index for b in td.beats] == list(range(1, 13))


def test_offset_is_first_beat(provider, fixtures):
    """The chart offset is the first beat, not the [music_start] marker.

    [music_start] is a Rock Band section marker that may be after the
    first beat; using it as the SongMap offset desynchronises the grid.
    """

    td = _load(provider, fixtures, "constant-tempo")
    assert td.offset == 0.0
    assert td.beats[0].time == 0.0


# --------------------------------------------------------------------------
# Tick → seconds conversion
# --------------------------------------------------------------------------


def test_tick_conversion_respects_tempo_changes(provider, fixtures):
    td = _load(provider, fixtures, "tempo-change")

    # 120 BPM: beats 1-8 at 0.5s spacing (4.0s total to beat 9).
    assert td.beats[0].time == 0.0
    assert td.beats[8].time == 4.0

    # 150 BPM after tick 3840: beat 9 is at 4.0s, beat 10 at 4.4s.
    assert td.beats[9].time == 4.4
    assert td.beats[-1].time == 10.0


def test_section_times_from_tempo_map(provider, fixtures):
    td = _load(provider, fixtures, "sections")

    # 140 BPM = 0.4286s per beat.
    assert abs(td.sections[1].start_time - 4 * (60 / 140)) < 0.001


# --------------------------------------------------------------------------
# Error handling
# --------------------------------------------------------------------------


def test_invalid_magic_raises(provider, fixtures):
    with pytest.raises(CorruptFileError):
        _load(provider, fixtures, "invalid-magic")


def test_unsupported_version_raises(provider, fixtures):
    with pytest.raises(UnsupportedVersionError):
        _load(provider, fixtures, "unsupported-version")


def test_truncated_container_raises(provider, fixtures):
    with pytest.raises(CorruptFileError):
        _load(provider, fixtures, "truncated")


def test_corrupt_chart_raises(provider, fixtures):
    with pytest.raises(CorruptFileError):
        _load(provider, fixtures, "corrupt-chart")


def test_missing_file_raises(provider, fixtures):
    with pytest.raises(FileNotFoundError):
        provider.load(str(fixtures / "missing.sng"))


def test_errors_are_catchable_timing_errors(provider, fixtures):
    from octobeat.timing.base import TimingError

    for name in ("invalid-magic", "unsupported-version", "truncated", "corrupt-chart"):
        with pytest.raises(TimingError):
            _load(provider, fixtures, name)


# --------------------------------------------------------------------------
# Real samples (optional, skipped if sng/ directory is absent)
# --------------------------------------------------------------------------


def test_real_world_samples(tmp_path):
    """The bundled real .sng samples must parse end-to-end."""

    from pathlib import Path

    samples = Path(__file__).resolve().parents[3] / "sng"
    if not samples.is_dir():
        pytest.skip("No sng/ samples directory available.")

    files = sorted(samples.glob("*.sng"))
    assert files, "Expected at least one .sng sample."

    provider = SNGProvider()

    for path in files:
        td = provider.load(str(path))
        assert len(td.beats) > 0
        assert len(td.tempos) > 0
        assert td.beats[0].index == 1
