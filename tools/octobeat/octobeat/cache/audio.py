from __future__ import annotations

import hashlib
from pathlib import Path

from platformdirs import user_cache_dir

from octobeat.audio import decode_to_wav
from octobeat.models.recording import Recording
from octobeat.models.songmap import Source


class AudioCache:
    """
    Local cache for source recordings and decoded audio.
    """

    def __init__(self) -> None:
        self.root = Path(user_cache_dir("octobeat"))

        self.sources_dir = self.root / "sources"
        self.decoded_dir = self.root / "decoded"

    #
    # Source recordings
    #

    def lookup(self, source: Source) -> Path | None:
        """
        Return the cached source recording if present.
        """

        path = self.source_path(source)

        if path.exists():
            return path

        return None

    def source_path(self, source: Source) -> Path:
        """
        Return the canonical cache location for the
        downloaded source recording.
        """

        path = (
            self.sources_dir
            / source.type
            / f"{self._key(source)}.wav"
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path

    #
    # Decoded audio
    #

    def decoded_path(self, source: Source) -> Path:
        """
        Return the canonical cache location for the
        decoded PCM WAV.
        """

        path = (
            self.decoded_dir
            / source.type
            / f"{self._key(source)}.wav"
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path

    def decoded(
        self,
        recording: Recording,
    ) -> Path:
        """
        Return a decoded PCM WAV for the recording.

        The file is generated on demand and regenerated
        automatically if the source recording changes.
        """

        path = self.decoded_path(
            recording.source,
        )

        needs_decode = (
            not path.exists()
            or path.stat().st_mtime
            < recording.path.stat().st_mtime
        )

        if needs_decode:
            decode_to_wav(
                recording.path,
                path,
            )

        return path

    #
    # Internals
    #

    @staticmethod
    def _key(source: Source) -> str:
        return hashlib.sha256(
            f"{source.type}:{source.id}".encode(
                "utf-8",
            ),
        ).hexdigest()