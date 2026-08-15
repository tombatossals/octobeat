from __future__ import annotations

import json
import wave
from pathlib import Path

import numpy as np

from octobeat.io.lyrics import (
    LYRICS_FILE,
    lyrics_to_json,
    write_lyrics,
)
from octobeat.models.timing import (
    LyricLine,
    LyricSyllable,
)


def _sample_lines() -> list[LyricLine]:
    return [
        LyricLine(
            index=1,
            text="Mississippi Queen",
            start_time=2.5,
            end_time=3.5,
            syllables=[
                LyricSyllable(
                    text="Mis-",
                    start_time=2.5,
                ),
                LyricSyllable(
                    text="Queen",
                    start_time=3.5,
                ),
            ],
        ),
        LyricLine(
            index=2,
            text="if you know what I mean",
            start_time=6.0,
            end_time=7.25,
            syllables=[
                LyricSyllable(
                    text="mean#",
                    start_time=7.25,
                ),
            ],
        ),
    ]


def test_lyrics_to_json_shape() -> None:
    doc = json.loads(
        lyrics_to_json(_sample_lines()),
    )

    assert isinstance(doc, list)
    assert len(doc) == 2

    first = doc[0]

    assert first["index"] == 1
    assert first["text"] == "Mississippi Queen"
    assert first["startTime"] == 2.5
    assert first["endTime"] == 3.5
    assert first["syllables"][0] == {
        "text": "Mis-",
        "startTime": 2.5,
    }


def test_write_lyrics_writes_utf8_file(tmp_path) -> None:
    destination = tmp_path / "dataset" / LYRICS_FILE

    write_lyrics(
        _sample_lines(),
        destination,
    )

    assert destination.exists()

    doc = json.loads(
        destination.read_text(
            encoding="utf-8",
        )
    )

    assert [line["text"] for line in doc] == [
        "Mississippi Queen",
        "if you know what I mean",
    ]


def test_write_resource_includes_lyrics(tmp_path) -> None:
    from octobeat.core.songmap_builder import build_songmap
    from octobeat.io.resource import write_resource
    from octobeat.models.metadata import (
        CatalogMetadata,
        ResourceRefs,
    )
    from octobeat.models.songmap import Source
    from octobeat.models.timing import (
        Beat,
        TempoSegment,
        TimingData,
    )

    def click_wav() -> Path:
        sr = 22050
        seconds = 1.0
        n = int(sr * seconds)
        pcm = (
            np.zeros(n) * 32767
        ).astype(np.int16)

        path = tmp_path / "click.wav"

        with wave.open(str(path), "wb") as file:
            file.setnchannels(1)
            file.setsampwidth(2)
            file.setframerate(sr)
            file.writeframes(pcm.tobytes())

        return path

    timing = TimingData(
        tempos=[
            TempoSegment(
                start_beat=1,
                start_time=0.0,
                bpm=120.0,
            ),
        ],
        beats=[
            Beat(index=1, time=0.0),
        ],
        time_signatures=[],
        sections=[],
    )

    songmap = build_songmap(
        timing,
        title="Test",
        duration=1.0,
        source=Source(
            type="file",
            id="test.wav",
        ),
        source_kind="audio-analysis",
        generated_by="test",
        created_at="2026-08-15T00:00:00+00:00",
    )

    metadata = CatalogMetadata(
        id="test",
        title="Test",
        artist="Artist",
        bpm=120.0,
        duration=1.0,
        resources=ResourceRefs(
            audio="recording.mp3",
            lyrics="lyrics.json",
        ),
    )

    write_resource(
        tmp_path / "dataset",
        songmap=songmap,
        metadata=metadata,
        audio=click_wav(),
        lyrics=_sample_lines(),
    )

    lyrics_path = (
        tmp_path
        / "dataset"
        / LYRICS_FILE
    )

    assert lyrics_path.exists()

    doc = json.loads(
        lyrics_path.read_text(
            encoding="utf-8",
        )
    )

    assert doc[0]["text"] == "Mississippi Queen"
