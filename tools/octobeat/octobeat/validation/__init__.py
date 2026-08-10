"""
SongMap and chart validation.

This package contains the validation logic for SongMap documents and
for chart-vs-audio timing validation.
"""

from .songmap import validate_songmap
from .timing import (
    AudioMetrics,
    TimingCheck,
    TimingValidation,
    analyse_audio,
    confidence_from_validation,
    validate_chart,
    validate_chart_file,
)

__all__ = [
    "AudioMetrics",
    "TimingCheck",
    "TimingValidation",
    "analyse_audio",
    "confidence_from_validation",
    "validate_chart",
    "validate_chart_file",
    "validate_songmap",
]