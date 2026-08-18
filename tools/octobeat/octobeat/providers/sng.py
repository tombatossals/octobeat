from __future__ import annotations

import tempfile
from pathlib import Path

from octobeat.audio.decoder import decode_to_wav_from_bytes
from octobeat.audio.mix import mix_tracks_to_wav
from octobeat.core.analyser import (
    detect_count_in_clicks,
    detect_music_lead_in,
)
from octobeat.models.recording import Recording
from octobeat.models.songmap import Source
from octobeat.providers.base import SourceProvider
from octobeat.timing.sng import (
    extract_audio,
    extract_cover,
    extract_full_mix,
    extract_stems,
    parse_sng_container,
)
from octobeat.ui import console


class SngSourceProvider(SourceProvider):
    """
    Source provider for SNG containers.

    Extracts the audio track and the chart from an SNG, decoding the
    audio to a temporary WAV for analysis. The chart path is attached to
    the Recording so the pipeline uses it as the timing source.
    """

    @classmethod
    def supports(cls, source: str) -> bool:
        return str(source).lower().endswith(".sng")

    def load(self, source: str) -> Recording:
        path = Path(source).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(path)

        data = path.read_bytes()

        sng = parse_sng_container(data)
        metadata = sng.metadata

        artist = metadata.get("artist")
        title = metadata.get("name")
        album = metadata.get("album")
        year = _parse_year(metadata.get("year"))
        genre = metadata.get("genre")

        # Multitrack containers ship the instrument stems; mix them into
        # the full mix together with the `song.*` track, which carries
        # the stick-click count-in the chart grid is anchored to.
        # Otherwise fall back to the single audio track.
        stems = extract_stems(data)
        full_mix = extract_full_mix(data)

        cleanup = tempfile.TemporaryDirectory(
            prefix="octobeat-sng-",
        )

        audio_path = Path(cleanup.name) / "song.wav"

        try:
            if stems:
                tracks = list(stems)

                if full_mix is not None:
                    tracks.append(full_mix)

                mix_tracks_to_wav(
                    tracks,
                    audio_path,
                )

                label = (
                    "tracks"
                    if full_mix is not None
                    else "stems"
                )

                console.info(
                    "SNG is multitrack; mixed "
                    + f"{len(tracks)} {label} into the full mix.",
                )
            else:
                _name, audio_bytes = extract_audio(data)

                decode_to_wav_from_bytes(
                    audio_bytes,
                    audio_path,
                )

            count_in_start, song_start = (
                detect_music_lead_in(
                    audio_path,
                )
            )

            # The stick clicks are prominent on the full-mix track
            # (song.opus); in the mixed stems they are buried. Detect the
            # individual clicks from that track so the count-in counter
            # can stay in sync with each click.
            click_wav = audio_path

            if full_mix is not None and stems:
                _mix_name, mix_bytes = full_mix

                click_wav = (
                    Path(cleanup.name)
                    / "click.wav"
                )

                decode_to_wav_from_bytes(
                    mix_bytes,
                    click_wav,
                )

            clicks = detect_count_in_clicks(
                click_wav,
                limit=song_start,
            )

            if clicks and len(clicks) <= 8:
                count_in_start = clicks[0]
            else:
                clicks = []
        except Exception:
            cleanup.cleanup()
            raise

        return Recording(
            path=audio_path,
            artist=artist,
            title=title,
            source=Source(
                type="file",
                id=str(path),
            ),
            cleanup_dir=cleanup,
            chart_path=path,
            album=album,
            year=year,
            genres=(
                [genre]
                if genre
                else None
            ),
            cover_bytes=extract_cover(data),
            count_in_start=count_in_start,
            song_start=song_start,
            count_in_clicks=(
                clicks
                if clicks
                else None
            ),
        )


def _parse_year(value: str | None) -> int | None:
    if not value:
        return None

    try:
        return int(value)
    except ValueError:
        return None
