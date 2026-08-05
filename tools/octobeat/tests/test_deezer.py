from __future__ import annotations

import json
import urllib.request

import pytest

from octobeat.providers.deezer import DeezerProvider

_SEARCH_PAYLOAD = {
    "data": [
        {
            "id": 123,
            "title": "Responsibility",
            "artist": {
                "id": 1,
                "name": "MxPx",
            },
            "album": {
                "id": 456,
                "title": "Slowly Going the Way of the Buffalo",
                "release_date": "1998-03-10",
                "cover_xl": (
                    "https://cdn-images.dzcdn.net/cover/123/"
                    "1000x1000-000000-80-0-0.jpg"
                ),
            },
        },
        {
            "id": 999,
            "title": "Responsibility (Remix)",
            "artist": {
                "id": 999,
                "name": "Someone Else",
            },
            "album": {
                "id": 999,
                "title": "Other",
                "release_date": "2000-01-01",
            },
        },
    ]
}

_ALBUM_PAYLOAD = {
    "id": 456,
    "title": "Slowly Going the Way of the Buffalo",
    "release_date": "1998-03-10",
    "genres": {
        "data": [
            {"id": 132, "name": "Rock"},
            {"id": 152, "name": "Punk"},
        ]
    },
}

_OTHER_ALBUM_PAYLOAD = {
    "id": 999,
    "title": "Other",
    "release_date": "2000-01-01",
    "genres": {
        "data": [],
    },
}


class _FakeResponse:
    def __init__(
        self,
        payload: object,
    ) -> None:
        if isinstance(payload, bytes):
            self._data = payload
        else:
            self._data = json.dumps(
                payload,
            ).encode("utf-8")

        self.headers = {
            "Content-Length": str(
                len(self._data),
            ),
        }

        self._position = 0

    def read(self, n: int = -1) -> bytes:
        if self._position >= len(self._data):
            return b""

        end = (
            len(self._data)
            if n < 0
            else self._position + n
        )

        chunk = self._data[
            self._position : end
        ]

        self._position = end

        return chunk

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def _fake_urlopen(monkeypatch) -> None:
    def open_url(url: str):
        if "api.deezer.com/album/999" in url:
            payload: object = _OTHER_ALBUM_PAYLOAD
        elif "api.deezer.com/album" in url:
            payload = _ALBUM_PAYLOAD
        elif url.startswith(
            "https://cdn-images.dzcdn.net",
        ):
            payload = b"fake-jpeg-bytes"
        else:
            payload = _SEARCH_PAYLOAD

        return _FakeResponse(payload)

    monkeypatch.setattr(
        urllib.request,
        "urlopen",
        open_url,
    )


def test_metadata_enrichment(monkeypatch) -> None:
    _fake_urlopen(monkeypatch)

    metadata = DeezerProvider().metadata(
        "MxPx",
        "Responsibility",
    )

    assert metadata is not None
    assert metadata.artist == "MxPx"
    assert metadata.title == "Responsibility"
    assert metadata.album == "Slowly Going the Way of the Buffalo"
    assert metadata.year == 1998
    assert metadata.genres == ["Rock", "Punk"]
    assert metadata.tags == ["rock", "punk"]


def test_metadata_prefers_exact_artist(monkeypatch) -> None:
    _fake_urlopen(monkeypatch)

    metadata = DeezerProvider().metadata(
        "Someone Else",
        "Responsibility",
    )

    assert metadata is not None
    assert metadata.album == "Other"
    assert metadata.genres == []


def test_metadata_no_results(monkeypatch) -> None:
    _fake_urlopen(monkeypatch)

    provider = DeezerProvider()

    provider.search = lambda *args, **kwargs: []

    assert (
        provider.metadata(
            "MxPx",
            "Responsibility",
        )
        is None
    )


def test_cover_url_max_size(monkeypatch) -> None:
    _fake_urlopen(monkeypatch)

    url = DeezerProvider().cover_url(
        "MxPx",
        "Responsibility",
    )

    assert url is not None
    assert "1200x1200" in url


def test_download_cover_writes_file(
    monkeypatch,
    tmp_path,
) -> None:
    _fake_urlopen(monkeypatch)

    destination = tmp_path / "cover.jpg"

    result = DeezerProvider().download_cover(
        "MxPx",
        "Responsibility",
        destination,
    )

    assert result == destination
    assert destination.exists()
    assert (
        destination.read_bytes()
        == b"fake-jpeg-bytes"
    )


def test_download_cover_missing(
    monkeypatch,
    tmp_path,
) -> None:
    _fake_urlopen(monkeypatch)

    provider = DeezerProvider()

    provider.search = lambda *args, **kwargs: []

    with pytest.raises(FileNotFoundError):
        provider.download_cover(
            "MxPx",
            "Responsibility",
            tmp_path / "cover.jpg",
        )
