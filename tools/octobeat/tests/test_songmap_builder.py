from __future__ import annotations

from pathlib import Path

import pytest

from octobeat.core.songmap_builder import build_songmap
from octobeat.fixtures import build_sng_fixtures
from octobeat.models.songmap import SCHEMA_ID, SONGMAP_VERSION, Source
from octobeat.timing import SNGProvider

CREATED_AT = "2026-08-10T00:00:00.000000+00:00"
GENERATED_BY = "octobeat test"


def _songmap_for(
    provider: SNGProvider,
    fixtures: Path,
    name: str,
) -> object:
    timing_data = provider.load(str(fixtures / f"{name}.sng"))

    return build_songmap(
        timing_data,
        title="Fixture Song",
        duration=20.0,
        source=Source(type="file", id="fixture.sng"),
        source_kind="sng",
        generated_by=GENERATED_BY,
        created_at=CREATED_AT,
    )


@pytest.fixture
def fixtures(tmp_path):
    build_sng_fixtures(tmp_path)
    return tmp_path


@pytest.fixture
def provider() -> SNGProvider:
    return SNGProvider()


def test_songmap_version_and_schema(provider, fixtures):
    songmap = _songmap_for(provider, fixtures, "constant-tempo")

    assert songmap.version == SONGMAP_VERSION
    assert songmap.schema_ == SCHEMA_ID
    assert songmap.generatedBy == GENERATED_BY


def test_songmap_metadata(provider, fixtures):
    songmap = _songmap_for(provider, fixtures, "constant-tempo")

    assert songmap.metadata.title == "Fixture Song"
    assert songmap.metadata.source.type == "file"


def test_beats_are_consecutive(provider, fixtures):
    songmap = _songmap_for(provider, fixtures, "constant-tempo")

    indices = [beat.index for beat in songmap.beats]
    assert indices == list(range(1, 17))

    # 120 BPM → 0.5s spacing.
    assert songmap.beats[0].time == 0.0
    assert songmap.beats[1].time == 0.5


def test_beats_stay_consecutive_across_tempo_change(provider, fixtures):
    songmap = _songmap_for(provider, fixtures, "tempo-change")

    indices = [beat.index for beat in songmap.beats]
    assert indices == list(range(1, 25))


def test_bars_from_time_signatures(provider, fixtures):
    songmap = _songmap_for(provider, fixtures, "constant-tempo")

    # 16 beats, 4/4 → 4 bars.
    assert [bar.index for bar in songmap.bars] == [1, 2, 3, 4]
    assert [bar.firstBeat for bar in songmap.bars] == [1, 5, 9, 13]


def test_bars_respect_signature_change(provider, fixtures):
    songmap = _songmap_for(provider, fixtures, "multiple-timesig")

    # 4/4 for beats 1-4, then 3/4. Bars: [1..4], [5..7], [8..10]...
    assert songmap.bars[0].firstBeat == 1
    assert songmap.bars[1].firstBeat == 5
    assert songmap.bars[2].firstBeat == 8


def test_tempo_map(provider, fixtures):
    songmap = _songmap_for(provider, fixtures, "tempo-change")

    assert songmap.timing.tempoMap is not None
    assert [(t.time, t.bpm) for t in songmap.timing.tempoMap] == [
        (0.0, 120.0),
        (4.0, 150.0),
    ]


def test_timing_block(provider, fixtures):
    songmap = _songmap_for(provider, fixtures, "constant-tempo")

    assert songmap.timing.bpm == 120.0
    assert songmap.timing.timeSignature == "4/4"
    assert songmap.timing.source == "sng"
    assert songmap.timing.confidence == 1.0


def test_sections_normalized(provider, fixtures):
    songmap = _songmap_for(provider, fixtures, "sections")

    names = [section.name for section in songmap.sections]
    assert names == [
        "Intro",
        "Verse",
        "Chorus",
        "Verse",
        "Chorus",
        "Bridge",
        "Solo",
        "Outro",
    ]

    # sourceName preserved where the chart label differs from the
    # normalized name.
    assert songmap.sections[1].sourceName == "verse 1"
    assert songmap.sections[0].sourceName is None


def test_sections_reference_beats(provider, fixtures):
    songmap = _songmap_for(provider, fixtures, "sections")

    assert songmap.sections[0].startBeat == 1
    assert songmap.sections[1].startBeat == 5
    assert songmap.sections[0].startTime == 0.0


def test_lyrics_extracted_from_vocals_track(provider, fixtures):
    songmap = _songmap_for(provider, fixtures, "lyrics")

    assert songmap.lyrics is not None
    assert [line.index for line in songmap.lyrics] == [1, 2]
    assert songmap.lyrics[0].text == "Mississippi Queen"
    assert songmap.lyrics[1].text == "if you know what I mean"

    first = songmap.lyrics[0]
    assert first.startTime == 2.5
    assert first.endTime == 3.5

    # Syllables keep the raw chart text; markers and sustains are skipped.
    assert [s.text for s in first.syllables] == [
        "Mis-",
        "sis-",
        "sip-",
        "pi",
        "Queen",
    ]
    assert [s.startTime for s in first.syllables] == [
        2.5,
        2.75,
        3.0,
        3.25,
        3.5,
    ]


def test_lyrics_absent_when_chart_has_no_vocals(provider, fixtures):
    songmap = _songmap_for(provider, fixtures, "constant-tempo")

    assert songmap.lyrics is None


def test_songmap_lyrics_serialize_omitted_when_empty(tmp_path):
    """Charts without lyrics must not emit a ``lyrics`` block."""

    from octobeat.io.songmap import write_songmap
    from octobeat.models.timing import TimingData

    songmap = build_songmap(
        TimingData(
            tempos=[],
            beats=[],
            time_signatures=[],
            sections=[],
        ),
        title="Empty",
        duration=0.0,
        source=Source(type="file", id="x.sng"),
        source_kind="sng",
        generated_by=GENERATED_BY,
        created_at=CREATED_AT,
    )

    destination = tmp_path / "songmap.json"
    write_songmap(songmap, destination)

    assert "lyrics" not in destination.read_text(encoding="utf-8")


def test_empty_beats_produce_empty_bars():
    from octobeat.models.timing import TimingData

    timing_data = TimingData(
        tempos=[],
        beats=[],
        time_signatures=[],
        sections=[],
    )

    songmap = build_songmap(
        timing_data,
        title="Empty",
        duration=0.0,
        source=Source(type="file", id="x.sng"),
        source_kind="sng",
        generated_by=GENERATED_BY,
        created_at=CREATED_AT,
    )

    assert songmap.beats == []
    assert songmap.bars == []
    assert songmap.timing.timeSignature == "4/4"


def test_real_world_samples_build_songmaps(tmp_path):
    samples = Path(__file__).resolve().parents[3] / "sng"
    if not samples.is_dir():
        pytest.skip("No sng/ samples directory available.")

    provider = SNGProvider()

    for path in sorted(samples.glob("*.sng")):
        timing_data = provider.load(str(path))
        songmap = build_songmap(
            timing_data,
            title=path.stem,
            duration=songmap_duration(timing_data),
            source=Source(type="file", id=path.name),
            source_kind="sng",
            generated_by=GENERATED_BY,
            created_at=CREATED_AT,
        )

        assert songmap.beats
        assert songmap.bars
        assert songmap.timing.bpm > 0


def songmap_duration(timing_data) -> float:
    return timing_data.beats[-1].time if timing_data.beats else 0.0
