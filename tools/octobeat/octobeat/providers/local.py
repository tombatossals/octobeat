from __future__ import annotations

from pathlib import Path

from octobeat.models.recording import Recording
from octobeat.models.songmap import Source
from octobeat.providers.base import SourceProvider


class LocalFileProvider(SourceProvider):
    """
    Source provider for local audio files.
    """

    SUPPORTED_EXTENSIONS = {
        ".mp3",
        ".wav",
        ".flac",
        ".ogg",
        ".m4a",
        ".webm",
        ".aac",
    }

    @classmethod
    def supports(cls, source: str) -> bool:
        path = Path(source).expanduser()

        return (
            path.exists()
            and path.is_file()
            and path.suffix.lower() in cls.SUPPORTED_EXTENSIONS
        )

    def load(self, source: str) -> Recording:
        path = Path(source).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(path)

        return Recording(
            path=path,
            title=path.stem,
            source=Source(
                type="file",
                id=str(path),
            ),
        )