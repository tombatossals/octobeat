from __future__ import annotations

from typing import Any, cast
import urllib.request
from pathlib import Path

import yt_dlp

from octobeat.cache.audio import AudioCache
from octobeat.metadata import parse_recording_title
from octobeat.models.recording import Recording
from octobeat.models.songmap import Source
from octobeat.providers.base import SourceProvider

_DOWNLOADER_OPTIONS: dict[str, Any] = {
    "quiet": True,
    "noplaylist": True,
    "extract_flat": False,
    "js_runtimes": {
        "deno": {"path": None},
        "node": {"path": None},
        "bun": {"path": None},
    },
}


class YouTubeProvider(SourceProvider):
    """
    Source provider for YouTube recordings.
    """

    def __init__(self) -> None:
        self._info: dict[str, Any] | None = None

    @classmethod
    def supports(cls, source: str) -> bool:
        return (
            source.startswith("https://www.youtube.com/")
            or source.startswith("https://youtube.com/")
            or source.startswith("https://youtu.be/")
        )

    #
    # Info
    #

    def info(self, url: str) -> dict[str, Any]:
        """
        Return the metadata for the given URL, cached per instance.
        """

        if self._info is None:
            self._info = self._fetch_info(url)

        return self._info

    def _fetch_info(self, url: str) -> dict[str, Any]:
        options = {
            **_DOWNLOADER_OPTIONS,
            "skip_download": True,
        }

        with yt_dlp.YoutubeDL(options) as downloader:
            return cast(
                dict[str, Any],
                downloader.extract_info(
                    url,
                    download=False,
                ),
            )

    #
    # Audio
    #

    def _download_audio(
        self,
        url: str,
        source: Source,
        cache: AudioCache,
    ) -> Path:
        destination = cache.source_path(source)

        output_template = str(
            destination.with_suffix(".%(ext)s"),
        )

        options = {
            **_DOWNLOADER_OPTIONS,
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                },
            ],
        }

        with yt_dlp.YoutubeDL(options) as downloader:
            downloader.download([url])

        if not destination.exists():
            raise RuntimeError(
                "yt-dlp did not produce an audio file.",
            )

        return destination

    #
    # Video
    #

    def download_video(
        self,
        url: str,
        destination: Path,
    ) -> Path:
        """
        Download the video track into the destination directory.

        Returns the path to the produced file (any extension).
        """

        destination = destination.expanduser().resolve()
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_template = str(
            destination.with_suffix(".%(ext)s"),
        )

        options = {
            **_DOWNLOADER_OPTIONS,
            "format": "bestvideo+bestaudio/best",
            "outtmpl": output_template,
            "merge_output_format": "mp4",
            "postprocessors": [
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",
                },
            ],
        }

        with yt_dlp.YoutubeDL(options) as downloader:
            downloader.download([url])

        if not destination.exists():
            raise RuntimeError(
                "yt-dlp did not produce a video file.",
            )

        return destination

    def download_thumbnail(
        self,
        url: str,
        destination: Path,
    ) -> Path:
        """
        Download the video thumbnail as a JPEG image.
        """

        destination = destination.expanduser().resolve()
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        info = self.info(url)

        thumbnail = (
            info.get("thumbnail")
            or self._best_thumbnail(info)
        )

        if not thumbnail:
            raise RuntimeError(
                "No thumbnail available for this video.",
            )

        urllib.request.urlretrieve(
            thumbnail,
            destination,
        )

        return destination

    def _best_thumbnail(self, info: dict[str, Any]) -> str | None:
        thumbnails: list[dict[str, Any]] = (
            info.get("thumbnails") or []
        )

        if not thumbnails:
            return None

        best = max(
            thumbnails,
            key=lambda entry: (
                entry.get("height") or 0,
                entry.get("width") or 0,
            ),
        )

        url = best.get("url")

        return url if isinstance(url, str) else None

    #
    # SourceProvider
    #

    def load(
        self,
        url: str,
    ) -> Recording:
        cache = AudioCache()

        info = self.info(url)

        recording_source = Source(
            type="youtube",
            id=info["id"],
        )

        metadata = parse_recording_title(
            info.get("title", ""),
        )

        audio = cache.lookup(
            recording_source,
        )

        if audio is None:
            audio = self._download_audio(
                url,
                recording_source,
                cache,
            )

        return Recording(
            path=audio,
            artist=metadata.artist,
            title=metadata.title,
            source=recording_source,
        )
