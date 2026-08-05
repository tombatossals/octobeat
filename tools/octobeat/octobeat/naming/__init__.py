"""
Canonical naming utilities for octobeat.
"""

from .output import resolve_output_path
from .slug import dataset_slug, recording_slug

__all__ = [
    "dataset_slug",
    "recording_slug",
    "resolve_output_path",
]