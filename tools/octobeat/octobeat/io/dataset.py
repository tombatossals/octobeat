from __future__ import annotations

import tempfile
from pathlib import Path

from octobeat.audio import (
    decode_to_wav_from_bytes,
    encode_to_mp3,
    mix_click_track,
    mix_tracks_to_wav,
)
from octobeat.cache import cache
from octobeat.io.songmap import write_songmap
from octobeat.models.songmap import SongMap
from octobeat.naming import export_stem
from octobeat.timing.sng import (
    extract_audio,
    extract_full_mix,
    extract_stems_without_drums,
)


def write_dataset(
    songmap: SongMap,
    destination: Path,
    *,
    metronome: bool = False,
    no_drums: bool = False,
    click_volume: float = 1.0,
    audio_path: Path | None = None,
) -> Path:
    """
    Write a SongMap dataset to disk.

    The exported files are named ``"<bpm> - <group> - <title>.mp3"``
    (and the matching ``.songmap.json``), so a batch of exports placed
    in the same directory sorts by song speed. The group is omitted
    when the SongMap carries no artist.

    When ``metronome`` is true the exported MP3 gets a metronome click
    track overlaid, marking every beat with a click and accenting the
    downbeat of each bar so the timing can be practiced by ear.
    ``click_volume`` scales the click level (``1.0`` default).

    When ``no_drums`` is true the exported audio is mixed from the
    original SNG multitracks with the drum stems removed, so the drums
    can be practiced along with the rest of the instruments. The SNG is
    resolved from ``audio_path`` when it points to a ``.sng`` file, or
    from the SongMap source otherwise.

    ``audio_path`` overrides the source recording; by default the
    recording is resolved from the cache via ``songmap.metadata.source``.
    An ``.sng`` container is accepted: its full-mix audio track is
    extracted and used as the recording.
    """

    destination = destination.expanduser().resolve()

    destination.mkdir(
        parents=True,
        exist_ok=True,
    )

    stem = export_stem(songmap)

    # Write SongMap
    write_songmap(
        songmap,
        destination / f"{stem}.songmap.json",
    )

    exported = destination / f"{stem}.mp3"

    if no_drums:
        _write_without_drums(
            songmap,
            exported,
            metronome=metronome,
            click_volume=click_volume,
            audio_path=audio_path,
        )
    else:
        with tempfile.TemporaryDirectory(
            prefix="octobeat-export-",
        ) as tmp:
            recording = _resolve_recording(
                songmap,
                audio_path,
                tmp_dir=Path(tmp),
            )

            if metronome:
                mix_click_track(
                    recording,
                    exported,
                    songmap,
                    volume=click_volume,
                )
            else:
                encode_to_mp3(
                    recording,
                    exported,
                )

    return destination


def _resolve_recording(
    songmap: SongMap,
    audio_path: Path | None,
    *,
    tmp_dir: Path,
) -> Path:
    """
    Resolve the source recording for a plain export.

    ``audio_path`` may be an audio file or an SNG container (its
    full-mix audio track is extracted and decoded into ``tmp_dir``).
    When omitted, the recording is looked up in the cache, falling back
    to the SongMap source when it points to an SNG container.
    """

    if audio_path is not None:
        path = audio_path.expanduser().resolve()

        if path.suffix.lower() == ".sng":
            return _sng_audio_to_wav(
                path,
                tmp_dir,
            )

        if path.exists():
            return path

        raise FileNotFoundError(
            f"Recording not found: {audio_path}",
        )

    recording = cache.lookup(songmap.metadata.source)

    if recording is not None:
        return recording

    source = songmap.metadata.source

    if source.type == "file":
        path = Path(source.id).expanduser().resolve()

        if path.suffix.lower() == ".sng" and path.exists():
            return _sng_audio_to_wav(
                path,
                tmp_dir,
            )

    raise FileNotFoundError(
        f"Recording not found in cache: "
        f"{songmap.metadata.source.type}:{songmap.metadata.source.id}"
    )


def _sng_audio_to_wav(
    sng_path: Path,
    tmp_dir: Path,
) -> Path:
    """
    Extract the full-mix (or single) audio track from an SNG container
    and decode it to a PCM WAV inside ``tmp_dir``.
    """

    data = sng_path.read_bytes()

    track = extract_full_mix(data)

    if track is None:
        _name, audio_bytes = extract_audio(data)
    else:
        _name, audio_bytes = track

    destination = tmp_dir / "sng-audio.wav"

    decode_to_wav_from_bytes(
        audio_bytes,
        destination,
    )

    return destination


def _write_without_drums(
    songmap: SongMap,
    exported: Path,
    *,
    metronome: bool,
    click_volume: float,
    audio_path: Path | None,
) -> None:
    """
    Mix the SNG multitracks without the drums and encode the result.
    """

    sng_path = _resolve_sng(
        songmap,
        audio_path,
    )

    tracks = extract_stems_without_drums(
        sng_path.read_bytes(),
    )

    if not tracks:
        raise ValueError(
            f"SNG has no instrument stems to mix: {sng_path}",
        )

    with tempfile.TemporaryDirectory(
        prefix="octobeat-nodrums-",
    ) as tmp:
        mix_wav = Path(tmp) / "mix.wav"

        mix_tracks_to_wav(
            tracks,
            mix_wav,
        )

        if metronome:
            mix_click_track(
                mix_wav,
                exported,
                songmap,
                volume=click_volume,
            )
        else:
            encode_to_mp3(
                mix_wav,
                exported,
            )


def _resolve_sng(
    songmap: SongMap,
    audio_path: Path | None,
) -> Path:
    """
    Resolve the original SNG container for a no-drums export.
    """

    if audio_path is not None:
        path = audio_path.expanduser().resolve()

        if path.suffix.lower() == ".sng" and path.exists():
            return path

        raise FileNotFoundError(
            f"--no-drums requires the original SNG multitracks, but "
            f"--audio points to: {audio_path}",
        )

    source = songmap.metadata.source

    if source.type == "file":
        path = Path(source.id).expanduser().resolve()

        if path.suffix.lower() == ".sng" and path.exists():
            return path

    raise FileNotFoundError(
        "The SongMap is not based on an SNG container; --no-drums "
        "requires the original SNG multitracks "
        "(use --audio <song.sng>).",
    )
