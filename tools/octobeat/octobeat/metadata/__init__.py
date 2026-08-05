"""
Music metadata parsing.
"""

from .parser import ParsedMetadata, parse_recording_title

__all__ = [
    "ParsedMetadata",
    "parse_recording_title",
]