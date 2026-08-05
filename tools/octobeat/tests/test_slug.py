from __future__ import annotations

from pathlib import Path

from octobeat.models.recording import Recording
from octobeat.models.songmap import Source
from octobeat.naming import (
    dataset_slug,
    recording_slug,
    source_token,
)


def _recording(
    source: Source,
    *,
    artist: str | None = "MxPx",
    title: str | None = "Responsibility",
) -> Recording:
    return Recording(
        path=Path("/tmp/song.wav"),
        artist=artist,
        title=title,
        source=source,
    )


def test_dataset_slug_includes_youtube_id() -> None:
    source = Source(
        type="youtube",
        id="KJamzD0KntE",
    )

    assert (
        dataset_slug(_recording(source))
        == "mxpx-responsibility-kjamzd0knte"
    )


def test_dataset_slug_hashes_local_source() -> None:
    source = Source(
        type="file",
        id="/music/songs/song.wav",
    )

    slug = dataset_slug(_recording(source))

    assert slug.startswith(
        "mxpx-responsibility-",
    )

    token = slug.rsplit("-", 1)[1]

    assert len(token) == 10
    assert token == source_token(source)


def test_distinct_sources_produce_distinct_slugs() -> None:
    first = dataset_slug(
        _recording(
            Source(
                type="youtube",
                id="aaaaaa",
            ),
        )
    )
    second = dataset_slug(
        _recording(
            Source(
                type="youtube",
                id="bbbbbb",
            ),
        )
    )

    assert first != second


def test_source_token_short_for_youtube() -> None:
    token = source_token(
        Source(
            type="youtube",
            id="KJamzD0KntE",
        )
    )

    assert token == "kjamzd0knte"


def test_recording_slug_matches_dataset_slug() -> None:
    recording = _recording(
        Source(
            type="youtube",
            id="abc",
        )
    )

    assert (
        recording_slug(recording)
        == dataset_slug(recording)
    )
