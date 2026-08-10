from __future__ import annotations

import pytest

from octobeat.sections import (
    normalize_section_name,
    strip_section_suffix,
)


@pytest.mark.parametrize(
    "label,expected",
    [
        # Canonical mappings.
        ("intro", "Intro"),
        ("Intro", "Intro"),
        ("INTRO", "Intro"),
        ("introduction", "Intro"),
        ("start", "Intro"),
        ("verse", "Verse"),
        ("verse 1", "Verse"),
        ("verse 2", "Verse"),
        ("verses", "Verse"),
        ("chorus", "Chorus"),
        ("refrain", "Chorus"),
        ("hook", "Chorus"),
        ("bridge", "Bridge"),
        ("break", "Bridge"),
        ("solo", "Solo"),
        ("solo 2", "Solo"),
        ("guitar solo", "Solo"),
        ("outro", "Outro"),
        ("ending", "Outro"),
        ("end", "Outro"),
        # Common chart wrappers.
        ("section Chorus", "Chorus"),
        ("[section gtr_lick]", "Gtr Lick"),
        ("section verse 1", "Verse"),
    ],
)
def test_normalize_section_name(label, expected):
    assert normalize_section_name(label) == expected


@pytest.mark.parametrize(
    "label,expected",
    [
        # Unknown labels pass through as Title Case.
        ("gtr_intro", "Gtr Intro"),
        ("interlude", "Interlude"),
        ("pre-chorus", "Pre Chorus"),
        ("coda", "Coda"),
        ("verse 3a", "Verse 3a"),
        # Whitespace and odd casing.
        ("  CHORUS  ", "Chorus"),
        ("Hook", "Chorus"),
    ],
)
def test_normalize_section_name_pass_through(label, expected):
    assert normalize_section_name(label) == expected


def test_empty_label_returns_empty():
    assert normalize_section_name("") == ""
    assert normalize_section_name("   ") == ""


@pytest.mark.parametrize(
    "label,expected",
    [
        ("verse 1", "verse"),
        ("verse 2", "verse"),
        ("solo-2", "solo"),
        ("chorus_3", "chorus"),
        ("verse 1a", "verse"),
        ("verse", "verse"),
        ("chorus", "chorus"),
    ],
)
def test_strip_section_suffix(label, expected):
    assert strip_section_suffix(label) == expected
