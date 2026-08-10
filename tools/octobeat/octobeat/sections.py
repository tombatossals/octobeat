"""Section name normalization.

Community charts use inconsistent section labels. This module maps them
to a small set of predictable names while keeping the original label.
"""

from __future__ import annotations

import re

# Canonical section names.
_INTRO = "Intro"
_VERSE = "Verse"
_CHORUS = "Chorus"
_BRIDGE = "Bridge"
_SOLO = "Solo"
_OUTRO = "Outro"

# Mapping of raw chart labels (lowercased, stripped of numbers) to a
# canonical name. Labels not present here pass through as Title Case.
_CANONICAL: dict[str, str] = {
    "intro": _INTRO,
    "introduction": _INTRO,
    "start": _INTRO,
    "verse": _VERSE,
    "verses": _VERSE,
    "vers": _VERSE,
    "chorus": _CHORUS,
    "refrain": _CHORUS,
    "hook": _CHORUS,
    "bridge": _BRIDGE,
    "break": _BRIDGE,
    "pre-bridge": _BRIDGE,
    "solo": _SOLO,
    "guitar solo": _SOLO,
    "outro": _OUTRO,
    "ending": _OUTRO,
    "end": _OUTRO,
}

# Suffixes stripped before looking up the canonical name (e.g. "verse 1",
# "verse 1a", "solo-2").
_TRAILING_SUFFIX = re.compile(
    r"\s*[-_ ]\s*(?:\d+\s*[-_ ]?\s*[a-z]?\s*|[a-z]\s*)$",
)

# Numbers-only suffix: used for the canonical lookup so "verse 1" maps to
# Verse while "verse 3a" (a non-standard sub-section) passes through.
_TRAILING_NUMBER = re.compile(r"\s*[-_ ]\s*\d+\s*$")


def normalize_section_name(label: str) -> str:
    """
    Normalize a chart section label to a canonical name.

    ``"section Chorus"`` → ``"Chorus"``, ``"verse 1"`` → ``"Verse"``,
    ``"hook"`` → ``"Chorus"``. Unrecognized labels are returned as Title
    Case without being dropped.
    """

    raw = label.strip()

    # Strip the common "[section " / "section " wrappers used by charts.
    if raw.lower().startswith("section "):
        raw = raw[len("section "):].strip()
    elif raw.lower().startswith("[section "):
        raw = raw[len("[section "):].strip(" ]")

    stripped = _strip_variants(raw)

    canonical = _CANONICAL.get(stripped)

    if canonical is not None:
        return canonical

    return _title_case(raw)


def strip_section_suffix(label: str) -> str:
    """
    Remove trailing numbers/letters used to disambiguate repeated
    sections: ``"verse 1"`` → ``"verse"``, ``"solo-2"`` → ``"solo"``,
    ``"verse 1a"`` → ``"verse"``.
    """

    return _TRAILING_SUFFIX.sub("", label).strip()


def _strip_variants(raw: str) -> str:
    """Lowercase and remove trailing numbers for the canonical lookup."""

    lowered = raw.lower().strip()

    return _TRAILING_NUMBER.sub("", lowered).strip()


def _title_case(raw: str) -> str:
    """Title-case a label, treating separators as word breaks.

    ``"gtr_intro"`` → ``"Gtr Intro"``, ``"pre-chorus"`` → ``"Pre Chorus"``.
    """

    normalized = raw.strip().replace("_", " ").replace("-", " ")
    words = [word for word in normalized.split() if word]

    if not words:
        return ""

    return " ".join(word[:1].upper() + word[1:].lower() for word in words)
