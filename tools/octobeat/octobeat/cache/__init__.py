"""
octobeat cache.
"""

from .audio import AudioCache

cache = AudioCache()

__all__ = [
    "AudioCache",
    "cache",
]