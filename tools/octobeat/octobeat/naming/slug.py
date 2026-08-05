from __future__ import annotations

import hashlib
import re

from octobeat.models.recording import Recording
from octobeat.models.songmap import Source


def recording_slug(recording: Recording) -> str:
    """
    Return the canonical slug for a recording.
    """

    return dataset_slug(recording)


def dataset_slug(recording: Recording) -> str:
    """
    Return the canonical slug for a resource dataset directory.

    The slug combines the artist, the title and a stable source token
    (the YouTube video id or a hash of the source), so different
    versions of the same song produce distinct dataset directories.
    """

    parts = _slug_parts(recording)

    if recording.source is not None:
        parts.append(
            source_token(recording.source),
        )

    return "-".join(parts)


def source_token(source: Source) -> str:
    """
    Return a stable, human-readable discriminator for a source.

    YouTube sources use the video id directly; every other source uses
    a short hash of its identity.
    """

    if source.type == "youtube":
        return source.id.lower()

    digest = hashlib.sha256(
        f"{source.type}:{source.id}".encode(),
    ).hexdigest()

    return digest[:10]


def _slug_parts(recording: Recording) -> list[str]:
    parts: list[str] = []

    if recording.artist:
        parts.append(
            _slugify(recording.artist),
        )

    if recording.title:
        parts.append(
            _slugify(recording.title),
        )

    if not parts:
        parts.append(
            _slugify(recording.path.stem),
        )

    return parts


def _slugify(value: str) -> str:
    value = value.lower()

    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-+", "-", value)

    return value.strip("-")
