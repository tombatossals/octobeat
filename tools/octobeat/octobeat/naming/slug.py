from __future__ import annotations

import re

from octobeat.models.recording import Recording


def recording_slug(recording: Recording) -> str:
    """
    Return the canonical slug for a recording.
    """

    parts: list[str] = []

    if recording.artist:
        parts.append(_slugify(recording.artist))

    if recording.title:
        parts.append(_slugify(recording.title))

    if recording.source is not None and recording.source.id:
        parts.append(recording.source.id.lower())

    if not parts:
        parts.append(_slugify(recording.path.stem))

    return "-".join(parts)


def dataset_slug(recording: Recording) -> str:
    """
    Return the canonical slug for a resource dataset directory.

    Unlike the recording slug, this identifier does not include the
    source id, so the resulting directory is stable across re-runs.
    """

    parts: list[str] = []

    if recording.artist:
        parts.append(_slugify(recording.artist))

    if recording.title:
        parts.append(_slugify(recording.title))

    if not parts:
        parts.append(_slugify(recording.path.stem))

    return "-".join(parts)


def _slugify(value: str) -> str:
    value = value.lower()

    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-+", "-", value)

    return value.strip("-")