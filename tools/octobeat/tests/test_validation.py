from __future__ import annotations

import pytest

from octobeat.fixtures import build_fixtures
from octobeat.models.timing import TimingData
from octobeat.validation.timing import (
    AudioMetrics,
    TimingCheck,
    analyse_audio,
    confidence_from_validation,
    validate_chart,
)


@pytest.fixture
def audio_fixtures(tmp_path):
    build_fixtures(tmp_path / "audio")
    return tmp_path / "audio"


def _audio(
    *,
    bpm: float,
    duration: float = 12.0,
    tempo_map: list[tuple[float, float]] | None = None,
    offset: float = 0.0,
    bpm_score: float = 1.0,
    tempo_candidates: list[tuple[float, float]] | None = None,
) -> AudioMetrics:
    """Build an AudioMetrics with sensible defaults."""

    return AudioMetrics(
        duration=duration,
        bpm=bpm,
        bpm_score=bpm_score,
        tempo_candidates=tempo_candidates or [(bpm, bpm_score)],
        tempo_map=tempo_map or [(0.0, bpm)],
        offset=offset,
        onset_envelope=pytest.importorskip("numpy").zeros(1),
        sr=22050,
    )


# --------------------------------------------------------------------------
# BPM
# --------------------------------------------------------------------------


def test_bpm_check_matches():
    audio = _audio(bpm=120.0)

    from octobeat.models.timing import Beat, TempoSegment

    chart = TimingData(
        tempos=[TempoSegment(start_beat=1, start_time=0.0, bpm=120.0)],
        beats=[Beat(index=1, time=0.0)],
        time_signatures=[],
        sections=[],
    )

    result = validate_chart(chart, audio)

    bpm = next(c for c in result.checks if c.name == "bpm")
    assert bpm.ok


def test_bpm_check_half_time_ok():
    audio = _audio(bpm=120.0)

    from octobeat.models.timing import Beat, TempoSegment

    chart = TimingData(
        tempos=[TempoSegment(start_beat=1, start_time=0.0, bpm=60.0)],
        beats=[Beat(index=1, time=0.0)],
        time_signatures=[],
        sections=[],
    )

    result = validate_chart(chart, audio)

    bpm = next(c for c in result.checks if c.name == "bpm")
    assert bpm.ok


def test_bpm_check_half_time_noisy_audio_ok():
    """Audio that resolves to a slightly-off double tempo still matches.

    E.g. chart 95 BPM, audio detects 178 BPM (89 doubled): within the
    looser half/double tolerance even though it is outside the tight 4%."""

    audio = _audio(bpm=178.0)

    from octobeat.models.timing import Beat, TempoSegment

    chart = TimingData(
        tempos=[TempoSegment(start_beat=1, start_time=0.0, bpm=95.0)],
        beats=[Beat(index=1, time=0.0)],
        time_signatures=[],
        sections=[],
    )

    result = validate_chart(chart, audio)

    bpm = next(c for c in result.checks if c.name == "bpm")
    assert bpm.ok
    assert "half/double time" in bpm.detail


def test_tempo_changes_ignore_micro_variations():
    """Micro-variations (76.0→76.1→76.0) keep the tempo span low."""

    audio = _audio(bpm=76.0)

    from octobeat.models.timing import Beat, TempoSegment

    chart = TimingData(
        tempos=[
            TempoSegment(start_beat=1, start_time=0.0, bpm=76.0),
            TempoSegment(start_beat=17, start_time=8.0, bpm=76.1),
            TempoSegment(start_beat=33, start_time=16.0, bpm=76.0),
        ],
        beats=[Beat(index=1, time=0.0)],
        time_signatures=[],
        sections=[],
    )

    result = validate_chart(chart, audio)

    tempo_changes = next(
        c for c in result.checks if c.name == "tempo-changes"
    )
    assert tempo_changes.ok


def test_tempo_changes_real_change_detected():
    """A genuine wide tempo change (120→90→130) raises the span above
    the tolerance and warns."""

    audio = _audio(bpm=120.0, duration=40.0)

    from octobeat.models.timing import Beat, TempoSegment

    chart = TimingData(
        tempos=[
            TempoSegment(start_beat=1, start_time=0.0, bpm=120.0),
            TempoSegment(start_beat=9, start_time=4.0, bpm=90.0),
            TempoSegment(start_beat=17, start_time=8.0, bpm=130.0),
        ],
        beats=[Beat(index=1, time=0.0)],
        time_signatures=[],
        sections=[],
    )

    result = validate_chart(chart, audio)

    tempo_changes = next(
        c for c in result.checks if c.name == "tempo-changes"
    )
    assert not tempo_changes.ok
    assert tempo_changes.warn


def test_bpm_check_mismatch_warns():
    audio = _audio(bpm=120.0)

    from octobeat.models.timing import Beat, TempoSegment

    chart = TimingData(
        tempos=[TempoSegment(start_beat=1, start_time=0.0, bpm=140.0)],
        beats=[Beat(index=1, time=0.0)],
        time_signatures=[],
        sections=[],
    )

    result = validate_chart(chart, audio)

    bpm = next(c for c in result.checks if c.name == "bpm")
    assert not bpm.ok
    assert bpm.warn


def test_bpm_check_unreliable_audio_does_not_penalise():
    """When the audio is not clearly periodic, the chart BPM is not
    penalised (the audio cannot say the chart is wrong)."""

    audio = _audio(bpm=41.5, bpm_score=0.05)

    from octobeat.models.timing import Beat, TempoSegment

    chart = TimingData(
        tempos=[TempoSegment(start_beat=1, start_time=0.0, bpm=141.0)],
        beats=[Beat(index=1, time=0.0)],
        time_signatures=[],
        sections=[],
    )

    result = validate_chart(chart, audio)

    bpm = next(c for c in result.checks if c.name == "bpm")
    assert bpm.ok
    assert "unreliable" in bpm.detail


def test_bpm_check_matches_audio_candidate():
    """The chart BPM may match a strong audio candidate even when the
    primary audio estimate picked a sub-harmonic."""

    audio = _audio(
        bpm=41.5,
        tempo_candidates=[
            (41.5, 0.20),
            (141.0, 0.15),
        ],
    )

    from octobeat.models.timing import Beat, TempoSegment

    chart = TimingData(
        tempos=[TempoSegment(start_beat=1, start_time=0.0, bpm=141.0)],
        beats=[Beat(index=1, time=0.0)],
        time_signatures=[],
        sections=[],
    )

    result = validate_chart(chart, audio)

    bpm = next(c for c in result.checks if c.name == "bpm")
    assert bpm.ok
    assert "candidate" in bpm.detail


# --------------------------------------------------------------------------
# Duration
# --------------------------------------------------------------------------


def test_duration_check_matches():
    audio = _audio(bpm=120.0, duration=10.0)

    from octobeat.models.timing import Beat, TempoSegment

    chart = TimingData(
        tempos=[TempoSegment(start_beat=1, start_time=0.0, bpm=120.0)],
        beats=[Beat(index=1, time=0.0), Beat(index=2, time=9.5)],
        time_signatures=[],
        sections=[],
    )

    result = validate_chart(chart, audio)

    duration = next(c for c in result.checks if c.name == "duration")
    assert duration.ok


def test_duration_check_mismatch_warns():
    audio = _audio(bpm=120.0, duration=10.0)

    from octobeat.models.timing import Beat, TempoSegment

    chart = TimingData(
        tempos=[TempoSegment(start_beat=1, start_time=0.0, bpm=120.0)],
        beats=[Beat(index=1, time=0.0), Beat(index=2, time=5.0)],
        time_signatures=[],
        sections=[],
    )

    result = validate_chart(chart, audio)

    duration = next(c for c in result.checks if c.name == "duration")
    assert not duration.ok
    assert duration.warn


# --------------------------------------------------------------------------
# Offset
# --------------------------------------------------------------------------


def test_offset_check_within_tolerance():
    audio = _audio(bpm=120.0, offset=0.050)

    from octobeat.models.timing import Beat, TempoSegment

    chart = TimingData(
        tempos=[TempoSegment(start_beat=1, start_time=0.0, bpm=120.0)],
        beats=[Beat(index=1, time=0.0)],
        time_signatures=[],
        sections=[],
    )

    result = validate_chart(chart, audio)

    offset = next(c for c in result.checks if c.name == "offset")
    assert offset.ok
    assert result.corrected_offset is None


def test_offset_check_mismatch_suggests_correction():
    audio = _audio(bpm=120.0, offset=1.000)

    from octobeat.models.timing import Beat, TempoSegment

    chart = TimingData(
        tempos=[TempoSegment(start_beat=1, start_time=0.0, bpm=120.0)],
        beats=[Beat(index=1, time=0.0)],
        time_signatures=[],
        sections=[],
    )

    result = validate_chart(chart, audio)

    offset = next(c for c in result.checks if c.name == "offset")
    assert not offset.ok
    assert offset.warn
    assert result.corrected_offset == 1.0


# --------------------------------------------------------------------------
# Confidence
# --------------------------------------------------------------------------


def test_confidence_perfect_chart():
    checks = [
        TimingCheck(name="bpm", ok=True, detail=""),
        TimingCheck(name="duration", ok=True, detail=""),
        TimingCheck(name="offset", ok=True, detail=""),
        TimingCheck(name="tempo-changes", ok=True, detail=""),
        TimingCheck(name="drift", ok=True, detail=""),
    ]

    assert confidence_from_validation(checks) == 1.0


def test_confidence_penalised():
    checks = [
        TimingCheck(name="bpm", ok=False, warn=True, detail=""),
        TimingCheck(name="drift", ok=False, warn=True, detail=""),
    ]

    confidence = confidence_from_validation(checks)
    assert confidence < 1.0
    assert confidence >= 0.0


def test_confidence_clamped():
    checks = [
        TimingCheck(name="bpm", ok=False, warn=True, detail=""),
        TimingCheck(name="duration", ok=False, warn=True, detail=""),
        TimingCheck(name="offset", ok=False, warn=True, detail=""),
        TimingCheck(name="tempo-changes", ok=False, warn=True, detail=""),
        TimingCheck(name="drift", ok=False, warn=True, detail=""),
    ]

    assert confidence_from_validation(checks) == 0.0


# --------------------------------------------------------------------------
# End-to-end with synthetic audio + chart
# --------------------------------------------------------------------------


def test_validate_chart_against_real_audio(audio_fixtures):
    """A chart matching the audio (120 BPM, 24 beats) should validate."""

    audio = analyse_audio(audio_fixtures / "constant-tempo.wav")

    chart = _matching_chart(120.0, 24)

    result = validate_chart(chart, audio)

    bpm = next(c for c in result.checks if c.name == "bpm")
    assert bpm.ok


def test_validation_result_has_no_warnings_on_match(audio_fixtures):
    audio = analyse_audio(audio_fixtures / "constant-tempo.wav")
    chart = _matching_chart(120.0, 24)

    result = validate_chart(chart, audio)

    assert result.has_warnings is False


def test_validated_chart_builds_songmap_with_provenance(audio_fixtures):
    """The validation confidence flows into the built SongMap."""

    from octobeat.core.songmap_builder import build_songmap
    from octobeat.models.songmap import Source

    audio = analyse_audio(audio_fixtures / "constant-tempo.wav")
    chart = _matching_chart(120.0, 24)

    result = validate_chart(chart, audio)

    songmap = build_songmap(
        chart,
        title="Fixture",
        duration=audio.duration,
        source=Source(type="file", id="fixture.wav"),
        source_kind="sng",
        generated_by="test",
        created_at="2026-08-10T00:00:00+00:00",
        offset=result.corrected_offset or chart.offset,
        confidence=result.confidence,
    )

    assert songmap.timing.source == "sng"
    assert songmap.timing.confidence == result.confidence
    assert songmap.timing.confidence > 0.5


def _matching_chart(
    bpm: float,
    beats: int,
) -> TimingData:
    """Build a chart whose beat grid matches the audio fixture.

    The ``constant-tempo`` audio fixture is 12 s of clicks at 120 BPM
    (24 beats), starting at 0.0.
    """

    from octobeat.models.timing import Beat, TempoSegment

    interval = 60.0 / bpm

    return TimingData(
        tempos=[
            TempoSegment(
                start_beat=1,
                start_time=0.0,
                bpm=bpm,
            ),
        ],
        beats=[
            Beat(
                index=index,
                time=round((index - 1) * interval, 3),
            )
            for index in range(1, beats + 1)
        ],
        time_signatures=[],
        sections=[],
    )
