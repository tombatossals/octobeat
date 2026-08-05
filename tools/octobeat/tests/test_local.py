from __future__ import annotations

from octobeat.providers.local import LocalFileProvider


def test_local_file_with_artist_title(
    tmp_path,
) -> None:
    path = tmp_path / "MxPx - Responsibility.mp3"

    path.write_bytes(b"")

    recording = LocalFileProvider().load(
        str(path),
    )

    assert recording.artist == "MxPx"
    assert recording.title == "Responsibility"


def test_local_file_without_artist(
    tmp_path,
) -> None:
    path = tmp_path / "just a title.mp3"

    path.write_bytes(b"")

    recording = LocalFileProvider().load(
        str(path),
    )

    assert recording.artist is None
    assert recording.title == "just a title"


def test_local_file_missing() -> None:
    try:
        LocalFileProvider().load(
            "/nonexistent/song.mp3",
        )
    except FileNotFoundError:
        pass
    else:
        raise AssertionError(
            "Expected FileNotFoundError.",
        )
