# OctoBeat CLI

> **The official command-line tool for building and maintaining the OctoBeat music library.**

OctoBeat CLI is responsible for creating, analysing and maintaining the datasets used by the OctoBeat ecosystem.

A dataset contains everything required to reproduce and analyse a song:

- metadata
- cover artwork
- audio recording
- video recording
- SongMap

The CLI automates the complete pipeline from a source (such as YouTube or a local file) to a fully reproducible dataset.

---

# Installation

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone git@github.com:tombatossals/octobeat.git
cd octobeat/tools/octobeat
uv sync
uv run octobeat --version
```

To install the command globally:

```bash
cd octobeat/tools/octobeat
uv tool install .
```

---

# Quick Start

## 1. Initialize the workspace

```bash
octobeat init
```

Creates the default configuration:

```text
~/.config/octobeat/config.toml
```

The default datasets directory is `~/Music/OctoBeat`.

## 2. Add a song from YouTube

```bash
octobeat add https://youtu.be/KJamzD0KntE
```

This single command:

- retrieves metadata (from Deezer);
- downloads the cover artwork;
- downloads the audio recording;
- downloads the video;
- decodes the audio when necessary;
- analyses the recording;
- generates the SongMap;
- builds the dataset;
- updates the catalog.

## 3. Analyse a local file

```bash
octobeat analyse /path/to/song.mp3 -o song.songmap.json
```

Add `--debug` to inspect the analysis:

```bash
octobeat analyse song.mp3 --debug
```

---

# Commands

## `init`

Initialize the OctoBeat workspace and default configuration.

```bash
octobeat init
```

## `config`

Manage configuration.

```bash
octobeat config show     # show the current configuration
octobeat config edit     # edit the configuration file
octobeat config set k v  # update a configuration value
```

## `add`

Create a complete dataset from a source (YouTube URL or local file).

```bash
octobeat add <input> [--no-video] [--no-cover] [--offset SECONDS]
```

Options:

- `-o, --output` — datasets directory (defaults to `paths.datasets`);
- `--catalog` — catalog file (defaults to `<output>/catalog.json`);
- `--id` — override the dataset identifier;
- `--no-video` — skip downloading the video track;
- `--no-cover` — skip downloading the cover artwork;
- `--offset` — seconds into the media where the song begins.

## `dataset`

Manage datasets.

```bash
octobeat dataset create   # create a dataset interactively
octobeat dataset update   # update an existing dataset
octobeat dataset rebuild  # rebuild a dataset
octobeat dataset verify   # verify datasets
octobeat dataset clean    # remove temporary artefacts
```

## `analyse`

Generate a SongMap from a recording.

```bash
octobeat analyse <input> [-o OUTPUT] [--offset SECONDS] [--debug]
```

The analyser (BeatEngine v2) detects:

- tempo (resolving half-time/double-time);
- a tempo map (constant tempo, discrete changes, accelerando/ritardando);
- phase and a stable beat grid;
- downbeats and bars;
- overall, tempo, beat and grid confidence;
- optional synced lyrics (from LRCLIB).

## `metadata`

Generate metadata.

```bash
octobeat metadata youtube <url>
```

## `extract`

Extract media from a source.

```bash
octobeat extract audio <url>
octobeat extract video <url>
```

## `cover`

Download cover artwork.

```bash
octobeat cover <url>
```

## `catalog`

Manage the catalog.

```bash
octobeat catalog build   # build catalog.json
octobeat catalog verify  # verify the catalog
octobeat catalog stats   # display catalog statistics
```

## `validate`

Validate a SongMap.

```bash
octobeat validate <songmap.json>
```

## `info`

Display information about a SongMap.

```bash
octobeat info <songmap.json>
```

## `export`

Export a SongMap.

```bash
octobeat export <songmap.json> <destination>
```

---

# Configuration

The CLI maintains a workspace configuration at
`~/.config/octobeat/config.toml`.

```toml
[paths]
datasets = "~/Music/OctoBeat"

[download]
audio_format = "bestaudio"
video_format = "bestvideo"

[catalog]
auto_rebuild = true
```

---

# Dataset Layout

Every dataset follows the same structure:

```text
dataset/

├── metadata.json
├── cover.jpg
├── recording.webm
├── recording.wav
├── video.mp4
└── songmap.json
```

The catalog (`catalog.json`) lists every dataset and is consumed by the
OctoBeat web application.

---

# Caching

Temporary artefacts are stored in the local cache
(`~/.cache/octobeat/`):

```text
cache/
    sources/
    decoded/
```

Cached data includes:

- downloaded recordings;
- decoded PCM audio;
- metadata.

The cache regenerates artefacts automatically whenever the source
changes.

---

# Development

```bash
# run the test suite
uv run pytest

# lint
uv run ruff check octobeat tests

# type-check
uv run mypy octobeat
```

The repository includes a set of synthetic fixtures
(`octobeat/fixtures/`) covering constant tempo, half/double-time,
tempo changes, accelerando, ritardando, syncopation, intros and
silence. Each fixture has an expected ground truth recorded in its
`manifest.json`.

---

# Architecture

The analysis engine (BeatEngine) is organised into independent
modules:

```text
core/
├── onset.py       onset envelope extraction
├── tempo.py       tempo candidates, tempo map, half/double resolution
├── phase.py       beat grid phase estimation
├── grid.py        stable beat grid with snapping
├── bars.py        downbeat detection and bars
└── confidence.py  independent quality metrics
```

The detection provides evidence; the musical grid governs the SongMap.

---

# Roadmap

The CLI is the reference implementation of BeatEngine. Planned work
includes:

- alternative detection backends (e.g. madmom);
- a graphical SongMap editor;
- additional metadata providers;
- dataset export/import.
