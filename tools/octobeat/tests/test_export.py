from __future__ import annotations

import argparse
import wave
from io import BytesIO
from pathlib import Path

import librosa
import numpy as np
import pytest

from octobeat.audio import mix_click_track
from octobeat.io.dataset import write_dataset
from octobeat.io.songmap import write_songmap
from octobeat.models.songmap import (
    Bar,
    Beat,
    SongMap,
    SongMetadata,
    Source,
    Timing,
)
from octobeat.naming import export_stem, format_bpm

BPM = 120.0
SECONDS = 8.0
INTERVAL = 60.0 / BPM


def _silence_wav(path: Path, *, sr: int = 48000) -> Path:
    samples = int(sr * SECONDS)
    pcm = np.zeros(samples, dtype=np.int16)

    with wave.open(str(path), "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(sr)
        file.writeframes(pcm.tobytes())

    return path


def _songmap(*, source: Source | None = None) -> SongMap:
    beats = []

    t = 0.0
    index = 1

    while t < SECONDS:
        beats.append(
            Beat(
                index=index,
                time=t,
            )
        )
        index += 1
        t += INTERVAL

    bars = [
        Bar(
            index=i,
            firstBeat=first,
        )
        for i, first in enumerate(
            range(1, index, 4),
            start=1,
        )
    ]

    return SongMap(
        version=1,
        schema="songmap/v1",
        generatedBy="test",
        createdAt="2026-01-01T00:00:00Z",
        metadata=SongMetadata(
            title="Test",
            duration=SECONDS,
            source=(
                source
                or Source(
                    type="file",
                    id="test",
                )
            ),
        ),
        timing=Timing(
            bpm=BPM,
            offset=0.0,
            timeSignature="4/4",
            confidence=1.0,
        ),
        beats=beats,
        bars=bars,
    )


def _load(path: Path) -> np.ndarray:
    audio, _ = librosa.load(
        str(path),
        sr=48000,
        mono=True,
    )

    return audio


def _window_peak(
    audio: np.ndarray,
    time: float,
    *,
    sr: int = 48000,
    radius: float = 0.02,
) -> float:
    sample = int(time * sr)
    low = max(0, sample - int(radius * sr))
    high = sample + int(radius * sr)

    return float(
        np.max(
            np.abs(
                audio[low:high],
            ),
        )
    )


def test_mix_click_track_places_a_click_on_every_beat(
    tmp_path,
) -> None:
    source = _silence_wav(
        tmp_path / "silence.wav",
    )
    songmap = _songmap()

    output = mix_click_track(
        source,
        tmp_path / "metronome.mp3",
        songmap,
    )

    assert output.exists()

    audio = _load(output)

    for beat in songmap.beats:
        assert (
            _window_peak(
                audio,
                beat.time,
            )
            > 0.05
        )

    # Between two consecutive beats the track is silent (no stray
    # energy), so every click is exactly on its beat.
    for beat in songmap.beats[:-1]:
        halfway = beat.time + INTERVAL / 2.0

        assert (
            _window_peak(
                audio,
                halfway,
            )
            < 0.02
        )


def test_mix_click_track_accents_the_downbeat(
    tmp_path,
) -> None:
    source = _silence_wav(
        tmp_path / "silence.wav",
    )
    songmap = _songmap()

    output = mix_click_track(
        source,
        tmp_path / "metronome.mp3",
        songmap,
    )

    audio = _load(output)

    downbeat = _window_peak(
        audio,
        songmap.beats[0].time,
    )
    regular = _window_peak(
        audio,
        songmap.beats[1].time,
    )

    assert downbeat > regular


def test_write_dataset_with_metronome(
    tmp_path,
) -> None:
    source = _silence_wav(
        tmp_path / "silence.wav",
    )
    songmap = _songmap()

    destination = write_dataset(
        songmap,
        tmp_path / "export",
        metronome=True,
        audio_path=source,
    )

    assert (destination / "120 - Test.mp3").exists()
    assert (destination / "120 - Test.songmap.json").exists()


def test_export_command_metronome(
    tmp_path,
) -> None:
    import octobeat.commands.export as export_cmd

    source = _silence_wav(
        tmp_path / "silence.wav",
    )
    songmap = _songmap()

    songmap_path = (
        tmp_path / "songmap.json"
    )

    write_songmap(
        songmap,
        songmap_path,
    )

    destination = tmp_path / "out"

    result = export_cmd.run(
        argparse.Namespace(
            songmap=str(songmap_path),
            destination=str(destination),
            metronome=True,
            no_drums=False,
            click_volume=1.0,
            audio=str(source),
        )
    )

    assert result == 0
    assert (destination / "120 - Test.mp3").exists()
    assert (destination / "120 - Test.songmap.json").exists()


def test_format_bpm() -> None:
    assert format_bpm(120.0) == "120"
    assert format_bpm(87.5) == "087.5"
    assert format_bpm(94.0) == "094"
    assert format_bpm(80.0) == "080"


def test_export_stem_prefixes_bpm() -> None:
    songmap = _songmap()

    assert export_stem(songmap) == "120 - Test"


def test_export_stem_sorts_by_bpm() -> None:
    slow = _songmap()
    fast = _songmap()
    faster = _songmap()

    slow = slow.model_copy(
        update={
            "timing": slow.timing.model_copy(
                update={"bpm": 80.0},
            ),
        }
    )
    fast = fast.model_copy(
        update={
            "timing": fast.timing.model_copy(
                update={"bpm": 120.0},
            ),
        }
    )
    faster = faster.model_copy(
        update={
            "timing": faster.timing.model_copy(
                update={"bpm": 180.0},
            ),
        }
    )

    stems = [
        export_stem(slow),
        export_stem(fast),
        export_stem(faster),
    ]

    assert stems == [
        "080 - Test",
        "120 - Test",
        "180 - Test",
    ]
    assert stems == sorted(stems)


# --------------------------------------------------------------------------
# No-drums export (from the SNG multitracks)
# --------------------------------------------------------------------------


def _pattern_wav(
    first_half: float,
    second_half: float,
    *,
    sr: int = 48000,
    duration: float = 0.1,
) -> bytes:
    """WAV with a constant amplitude in each half (48 kHz, int16)."""
    frames = int(sr * duration)
    half = frames // 2

    samples = np.concatenate(
        [
            np.full(
                half,
                first_half,
            ),
            np.full(
                frames - half,
                second_half,
            ),
        ]
    )

    buffer = BytesIO()

    with wave.open(buffer, "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(sr)
        file.writeframes(
            np.clip(
                samples * 32767,
                -32768,
                32767,
            ).astype(
                np.int16,
            ).tobytes()
        )

    return buffer.getvalue()


def _multitrack_sng_with_drums() -> bytes:
    from octobeat.fixtures.sng import (
        _build_notes_mid,
        _build_sng_container,
        _constant_tempo,
    )

    return _build_sng_container(
        {
            "name": "Multitrack",
            "artist": "Fixture Band",
            "song_length": "5000",
        },
        {
            "notes.mid": _build_notes_mid(_constant_tempo()),
            # Guitar fills the whole track; drums only the second half.
            # If drums were kept, the second half would be louder after
            # normalisation and the two halves would not match.
            "guitar.opus": _pattern_wav(0.5, 0.5),
            "drums.opus": _pattern_wav(0.0, 0.5),
        },
    )


def _multitrack_sng_path(tmp_path) -> Path:
    path = tmp_path / "multi.sng"
    path.write_bytes(_multitrack_sng_with_drums())
    return path


def test_write_dataset_no_drums_excludes_drums(
    tmp_path,
) -> None:
    sng_path = _multitrack_sng_path(tmp_path)

    songmap = _songmap(
        source=Source(
            type="file",
            id=str(sng_path),
        ),
    )

    destination = write_dataset(
        songmap,
        tmp_path / "export",
        no_drums=True,
    )

    mp3 = destination / "120 - Test.mp3"

    assert mp3.exists()

    audio = _load(mp3)
    half = audio.size // 2

    first = float(
        np.abs(
            audio[:half],
        ).mean()
    )
    second = float(
        np.abs(
            audio[half:],
        ).mean()
    )

    # Only the guitar (constant 0.5) is mixed, so both halves sit at
    # the same level. With the drums (0.5 in the second half) the first
    # half would drop to ~0.47 after normalisation.
    assert first > 0.7
    assert second > 0.7
    assert abs(first - second) < 0.1


def test_export_command_no_drums_with_metronome(
    tmp_path,
) -> None:
    import octobeat.commands.export as export_cmd

    sng_path = _multitrack_sng_path(tmp_path)

    songmap = _songmap(
        source=Source(
            type="file",
            id=str(sng_path),
        ),
    )

    songmap_path = (
        tmp_path / "songmap.json"
    )

    write_songmap(
        songmap,
        songmap_path,
    )

    destination = tmp_path / "out"

    result = export_cmd.run(
        argparse.Namespace(
            songmap=str(songmap_path),
            destination=str(destination),
            metronome=True,
            no_drums=True,
            click_volume=1.0,
            audio=str(sng_path),
        )
    )

    assert result == 0
    assert (destination / "120 - Test.mp3").exists()
    assert (destination / "120 - Test.songmap.json").exists()


def test_export_no_drums_resolves_sng_from_source(
    tmp_path,
) -> None:
    sng_path = _multitrack_sng_path(tmp_path)

    songmap = _songmap(
        source=Source(
            type="file",
            id=str(sng_path),
        ),
    )

    destination = write_dataset(
        songmap,
        tmp_path / "export",
        no_drums=True,
    )

    assert (destination / "120 - Test.mp3").exists()


def test_export_no_drums_requires_sng(
    tmp_path,
) -> None:
    songmap = _songmap()

    with pytest.raises(
        FileNotFoundError,
    ):
        write_dataset(
            songmap,
            tmp_path / "export",
            no_drums=True,
        )


def test_export_no_drums_rejects_non_sng_audio(
    tmp_path,
) -> None:
    sng_path = _multitrack_sng_path(tmp_path)
    audio = _silence_wav(
        tmp_path / "plain.wav",
    )

    songmap = _songmap(
        source=Source(
            type="file",
            id=str(sng_path),
        ),
    )

    with pytest.raises(
        FileNotFoundError,
    ):
        write_dataset(
            songmap,
            tmp_path / "export",
            no_drums=True,
            audio_path=audio,
        )


# --------------------------------------------------------------------------
# Exporting straight from an SNG container (full-mix audio)
# --------------------------------------------------------------------------


def _full_mix_sng_path(
    tmp_path,
    *,
    name: str = "Test",
) -> Path:
    from octobeat.fixtures.sng import (
        _build_notes_mid,
        _build_sng_container,
        _constant_tempo,
    )

    path = tmp_path / "song.sng"

    path.write_bytes(
        _build_sng_container(
            {
                "name": name,
                "artist": "Fixture Band",
                "song_length": "5000",
            },
            {
                "notes.mid": _build_notes_mid(_constant_tempo()),
                "song.wav": _pattern_wav(0.5, 0.5),
            },
        )
    )

    return path


def test_write_dataset_metronome_from_sng(
    tmp_path,
) -> None:
    sng_path = _full_mix_sng_path(tmp_path)

    songmap = _songmap(
        source=Source(
            type="file",
            id=str(sng_path),
        ),
    )

    destination = write_dataset(
        songmap,
        tmp_path / "export",
        metronome=True,
    )

    mp3 = destination / "120 - Test.mp3"

    assert mp3.exists()
    assert (destination / "120 - Test.songmap.json").exists()

    # The full-mix audio was extracted from the SNG and the metronome
    # overlaid a click on the first beat.
    audio = _load(mp3)

    assert (
        _window_peak(
            audio,
            0.0,
        )
        > 0.1
    )


def test_export_command_metronome_from_sng_audio_flag(
    tmp_path,
) -> None:
    import octobeat.commands.export as export_cmd

    sng_path = _full_mix_sng_path(tmp_path)

    songmap = _songmap(
        source=Source(
            type="file",
            id=str(sng_path),
        ),
    )

    songmap_path = (
        tmp_path / "songmap.json"
    )

    write_songmap(
        songmap,
        songmap_path,
    )

    destination = tmp_path / "out"

    result = export_cmd.run(
        argparse.Namespace(
            songmap=str(songmap_path),
            destination=str(destination),
            metronome=True,
            no_drums=False,
            click_volume=1.0,
            audio=str(sng_path),
        )
    )

    assert result == 0
    assert (destination / "120 - Test.mp3").exists()


# --------------------------------------------------------------------------
# Direct export: one command from an .sng
# --------------------------------------------------------------------------


def test_export_command_direct_from_sng(
    tmp_path,
) -> None:
    import octobeat.commands.export as export_cmd

    sng_path = _full_mix_sng_path(
        tmp_path,
        name="Direct Song",
    )

    destination = tmp_path / "out"

    result = export_cmd.run(
        argparse.Namespace(
            songmap=str(sng_path),
            destination=str(destination),
            metronome=True,
            no_drums=False,
            click_volume=1.0,
            audio=None,
        )
    )

    assert result == 0

    # The SongMap comes from the SNG metadata/chart: 120 BPM from the
    # constant-tempo chart, title from the container.
    mp3 = destination / "120 - Direct Song.mp3"

    assert mp3.exists()
    assert (destination / "120 - Direct Song.songmap.json").exists()

    # The full-mix audio was extracted and the metronome marks the
    # first beat.
    audio = _load(mp3)

    assert (
        _window_peak(
            audio,
            0.0,
        )
        > 0.1
    )


def test_export_command_direct_from_sng_no_drums(
    tmp_path,
) -> None:
    import octobeat.commands.export as export_cmd

    sng_path = _multitrack_sng_path(tmp_path)

    destination = tmp_path / "out"

    result = export_cmd.run(
        argparse.Namespace(
            songmap=str(sng_path),
            destination=str(destination),
            metronome=False,
            no_drums=True,
            click_volume=1.0,
            audio=None,
        )
    )

    assert result == 0

    mp3 = destination / "120 - Multitrack.mp3"

    assert mp3.exists()

    audio = _load(mp3)
    half = audio.size // 2

    first = float(
        np.abs(
            audio[:half],
        ).mean()
    )
    second = float(
        np.abs(
            audio[half:],
        ).mean()
    )

    # Only the guitar is mixed; the drums (second half only) are gone.
    assert first > 0.7
    assert second > 0.7
    assert abs(first - second) < 0.1


def test_export_direct_from_sng_without_full_mix_uses_single_track(
    tmp_path,
) -> None:
    """An SNG without a `song.*` full mix exports its single audio
    track as-is, instead of mixing the stems."""

    import octobeat.commands.export as export_cmd
    from octobeat.fixtures.sng import (
        _build_notes_mid,
        _build_sng_container,
        _constant_tempo,
    )

    sng_path = tmp_path / "stems-only.sng"

    sng_path.write_bytes(
        _build_sng_container(
            {
                "name": "Stems Only",
                "artist": "Fixture Band",
                "song_length": "5000",
            },
            {
                "notes.mid": _build_notes_mid(_constant_tempo()),
                # Two stems, no full mix: the export must use the single
                # guitar track (0.5) rather than summing both.
                "guitar.opus": _pattern_wav(0.5, 0.5),
                "vocals.opus": _pattern_wav(0.4, 0.4),
            },
        )
    )

    destination = tmp_path / "out"

    result = export_cmd.run(
        argparse.Namespace(
            songmap=str(sng_path),
            destination=str(destination),
            metronome=False,
            no_drums=False,
            click_volume=1.0,
            audio=None,
        )
    )

    assert result == 0

    audio = _load(
        destination / "120 - Stems Only.mp3",
    )

    level = float(
        np.abs(audio).mean()
    )

    # Guitar only (0.5): a stem mix would sit around 0.9.
    assert 0.3 < level < 0.7


# --------------------------------------------------------------------------
# Metronome click volume
# --------------------------------------------------------------------------


def test_click_volume_makes_clicks_louder(
    tmp_path,
) -> None:
    source = _silence_wav(
        tmp_path / "silence.wav",
    )
    songmap = _songmap()

    quiet = mix_click_track(
        source,
        tmp_path / "quiet.mp3",
        songmap,
    )

    loud = mix_click_track(
        source,
        tmp_path / "loud.mp3",
        songmap,
        volume=2.0,
    )

    quiet_audio = _load(quiet)
    loud_audio = _load(loud)

    quiet_beat = _window_peak(
        quiet_audio,
        songmap.beats[1].time,
    )
    loud_beat = _window_peak(
        loud_audio,
        songmap.beats[1].time,
    )

    assert loud_beat > quiet_beat


def test_export_command_click_volume(
    tmp_path,
) -> None:
    import octobeat.commands.export as export_cmd

    source = _silence_wav(
        tmp_path / "silence.wav",
    )
    songmap = _songmap()

    songmap_path = (
        tmp_path / "songmap.json"
    )

    write_songmap(
        songmap,
        songmap_path,
    )

    result = export_cmd.run(
        argparse.Namespace(
            songmap=str(songmap_path),
            destination=str(tmp_path / "out"),
            metronome=True,
            no_drums=False,
            click_volume=2.0,
            audio=str(source),
        )
    )

    assert result == 0
    assert (tmp_path / "out" / "120 - Test.mp3").exists()
