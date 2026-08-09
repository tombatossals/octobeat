from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

import octobeat.commands.dataset as dataset_cmd
import octobeat.commands.metadata as metadata_cmd
import octobeat.providers.deezer as deezer_module
from octobeat.io.resource import (
    COVER_FILE,
    METADATA_FILE,
    RECORDING_WAV,
)


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """Never hit real Deezer during these tests."""

    monkeypatch.setattr(
        deezer_module,
        "download_url",
        lambda url, destination, **kwargs: destination.write_bytes(
            b"fake-cover"
        ),
    )


def _make_dataset(
    root: Path,
    dataset_id: str,
    *,
    artist: str = "The Artist",
    title: str = "My Song",
    album: str | None = None,
    bpm: float = 120.0,
) -> Path:
    dataset_dir = root / dataset_id
    dataset_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    (dataset_dir / RECORDING_WAV).write_bytes(
        b"not-audio"
    )

    (dataset_dir / METADATA_FILE).write_text(
        json.dumps(
            {
                "id": dataset_id,
                "title": title,
                "artist": artist,
                "album": album,
                "genres": [],
                "tags": [],
                "bpm": bpm,
                "duration": 8.0,
                "resources": {
                    "audio": RECORDING_WAV,
                },
            }
        ),
        encoding="utf-8",
    )

    return dataset_dir


def _args(
    **kwargs,
) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)


class _FakeDeezer:
    """Deezer provider returning a fixed, predictable track."""

    TRACK = {
        "id": 1,
        "title": "My Song",
        "artist": {
            "id": 1,
            "name": "The Artist",
        },
        "album": {
            "id": 10,
            "title": "The Album",
            "release_date": "2001-05-05",
            "cover_xl": (
                "https://cdn-images.dzcdn.net/cover/1/"
                "1000x1000-000000-80-0-0.jpg"
            ),
        },
    }

    def tracks(
        self,
        artist: str,
        title: str,
        limit: int = 8,
    ):
        return [dict(self.TRACK)]

    def metadata_for_track(
        self,
        track,
    ):
        return deezer_module.DeezerMetadata(
            artist="The Artist",
            title="My Song",
            album="The Album",
            year=2001,
            genres=["Rock"],
            tags=["rock"],
        )

    def cover_url_for_track(
        self,
        track,
    ) -> str | None:
        return "https://cdn-images.dzcdn.net/cover/1/1200x1200-0-0.jpg"

    def download_cover_for_track(
        self,
        track,
        destination: Path,
    ) -> Path:
        destination.write_bytes(b"fake-cover")

        return destination


def test_dataset_list(
    tmp_path,
) -> None:
    _make_dataset(tmp_path, "song-a")
    _make_dataset(tmp_path, "song-b")

    (tmp_path / "not-a-dataset").mkdir()

    result = dataset_cmd._list(
        _args(
            output=tmp_path,
            incomplete=False,
        )
    )

    assert result == 0


def test_dataset_list_empty(
    tmp_path,
) -> None:
    result = dataset_cmd._list(
        _args(
            output=tmp_path,
            incomplete=False,
        )
    )

    assert result == 0


def test_dataset_list_incomplete(
    tmp_path,
) -> None:
    _make_dataset(tmp_path, "song-a")
    _make_dataset(tmp_path, "song-b")

    # Give song-a a cover so it is complete, then remove it so it is
    # flagged as incomplete. song-b stays complete.
    cover = tmp_path / "song-a" / COVER_FILE

    cover.write_bytes(b"cover")

    assert not (tmp_path / "song-b" / COVER_FILE).exists()

    cover.unlink()

    result = dataset_cmd._list(
        _args(
            output=tmp_path,
            incomplete=True,
        )
    )

    assert result == 0


def test_metadata_fetch_non_interactive(
    monkeypatch,
    tmp_path,
) -> None:
    _make_dataset(tmp_path, "song-a")

    monkeypatch.setattr(
        metadata_cmd,
        "DeezerProvider",
        _FakeDeezer,
    )

    result = metadata_cmd._fetch(
        _args(
            dataset="song-a",
            output=tmp_path,
            no_interactive=True,
        )
    )

    assert result == 0

    metadata = json.loads(
        (
            tmp_path
            / "song-a"
            / METADATA_FILE
        ).read_text(
            encoding="utf-8",
        )
    )

    assert metadata["album"] == "The Album"
    assert metadata["year"] == 2001
    assert metadata["genres"] == ["Rock"]

    assert (
        tmp_path
        / "song-a"
        / COVER_FILE
    ).exists()


def test_metadata_fetch_missing_dataset(
    tmp_path,
) -> None:
    result = metadata_cmd._fetch(
        _args(
            dataset="nope",
            output=tmp_path,
            no_interactive=True,
        )
    )

    assert result == 1


def test_metadata_fetch_prefix_match(
    monkeypatch,
    tmp_path,
) -> None:
    _make_dataset(tmp_path, "song-a")
    _make_dataset(tmp_path, "song-b")

    monkeypatch.setattr(
        metadata_cmd,
        "DeezerProvider",
        _FakeDeezer,
    )

    result = metadata_cmd._fetch(
        _args(
            dataset="song-a",
            output=tmp_path,
            no_interactive=True,
        )
    )

    assert result == 0


def test_suggest_identity_splits_colon() -> None:
    class _Meta:
        id = "song-a"
        artist = ""
        title = "The Artist: My Song"

    parsed = metadata_cmd._suggest_identity(
        _Meta(),
    )

    assert parsed == ("The Artist", "My Song")


def test_suggest_identity_splits_dash() -> None:
    class _Meta:
        id = "song-a"
        artist = ""
        title = "The Artist - My Song"

    parsed = metadata_cmd._suggest_identity(
        _Meta(),
    )

    assert parsed == ("The Artist", "My Song")


def test_suggest_identity_no_separator() -> None:
    class _Meta:
        id = "song-a"
        artist = ""
        title = "My Song"

    parsed = metadata_cmd._suggest_identity(
        _Meta(),
    )

    assert parsed == (None, "My Song")


def test_dataset_incomplete_flags(
    tmp_path,
) -> None:
    from octobeat.io.resource import SONGMAP_FILE
    from octobeat.pipeline.datasets import list_datasets

    _make_dataset(tmp_path, "complete")
    _make_dataset(tmp_path, "no-cover")

    # complete has a cover and a songmap; no-cover has neither.
    (tmp_path / "complete" / COVER_FILE).write_bytes(
        b"cover"
    )
    (tmp_path / "complete" / SONGMAP_FILE).write_text(
        "{}",
        encoding="utf-8",
    )

    by_id = {
        entry.dataset_id: entry
        for entry in list_datasets(tmp_path)
    }

    assert not by_id["complete"].incomplete()
    assert by_id["no-cover"].incomplete()
    assert "cover.jpg" in by_id["no-cover"].missing()
