# OctoBeat CLI

> **The official command-line tool for building and maintaining the OctoBeat music library.**

OctoBeat CLI is responsible for creating, analysing and maintaining the datasets used by the OctoBeat ecosystem.

A dataset contains everything required to reproduce and analyse a song:

- metadata
- cover artwork
- audio recording
- video recording
- SongMap

The CLI automates the complete pipeline from a source (such as YouTube) to a fully reproducible dataset.

---

# Vision

The command line should make adding a new song as simple as:

```bash
octobeat add https://youtu.be/KJamzD0KntE
```

From that single command the CLI should:

- retrieve metadata;
- download the cover artwork;
- download the audio recording;
- download the video;
- decode the audio when necessary;
- analyse the recording;
- generate the SongMap;
- build the dataset;
- update the catalog.

The user should never need to perform these steps manually.

---

# Responsibilities

The CLI is responsible for:

- building datasets;
- analysing recordings;
- generating SongMaps;
- validating SongMaps;
- downloading media;
- generating metadata;
- maintaining the catalog;
- validating datasets.

It is **not** responsible for:

- media playback;
- exercise rendering;
- user interface;
- educational features.

Those belong to the OctoBeat application.

---

# Dataset

Every dataset follows the same structure.

```text
dataset/

├── metadata.json
├── cover.jpg
├── recording.webm
├── video.webm
└── recording.songmap.json
```

Future optional files may include:

```text
lyrics.txt
notes.md
thumbnail.jpg
```

---

# Architecture

The project is organised into independent layers.

```text
CLI
 │
 ▼
Commands
 │
 ▼
Pipeline
 │
 ├── Metadata
 ├── Download
 ├── Decode
 ├── Analysis
 ├── Catalog
 │
 ▼
Core
 │
 ▼
IO
```

---

# Pipeline

The analysis pipeline is intentionally modular.

```text
Source
   │
   ▼
Metadata
   │
   ▼
Download
   │
   ├── Audio
   └── Video
         │
         ▼
   Decode PCM
         │
         ▼
 Beat Detection
         │
         ▼
 SongMap
         │
         ▼
 Dataset
         │
         ▼
 Catalog
```

Each stage should be reusable independently.

---

# Supported Sources

Initially supported sources:

- YouTube
- Local audio files

Future providers:

- Spotify
- Discogs
- MusicBrainz
- Local video files

---

# Configuration

The CLI maintains a workspace configuration.

```bash
octobeat init
```

Creates:

```text
~/.config/octobeat/config.toml
```

Example:

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

# Planned Commands

## Configuration

```bash
octobeat init

octobeat config show

octobeat config edit

octobeat config set
```

---

## Dataset

```bash
octobeat add <youtube-url>

octobeat dataset create

octobeat dataset update

octobeat dataset rebuild

octobeat dataset verify

octobeat dataset clean
```

---

## Analysis

```bash
octobeat analyse <recording>
```

Generates:

```
recording.songmap.json
```

---

## Metadata

```bash
octobeat metadata youtube <url>
```

---

## Media

```bash
octobeat extract audio <url>

octobeat extract video <url>

octobeat cover <url>
```

---

## Catalog

```bash
octobeat catalog build

octobeat catalog verify

octobeat catalog stats
```

---

# Caching

Temporary artefacts are stored in the local cache.

```text
cache/

    sources/

    decoded/
```

Cached data includes:

- downloaded recordings;
- decoded PCM audio;
- metadata.

The cache should regenerate artefacts automatically whenever the source changes.

---

# Reporting

Every command should produce a concise execution report.

Example:

```text
Dataset
-------

Artist............. MxPx
Title.............. Responsibility

Resources
---------

Audio.............. recording.webm
Video.............. video.webm
Cover.............. cover.jpg

Analysis
--------

Duration........... 159.2 s
Tempo.............. 162 BPM
Beats.............. 430
Confidence......... 0.96

Output
------

Dataset............ ~/Music/OctoBeat/mxpx-responsibility
```

---

# Guiding Principles

The CLI follows a few simple principles:

- one command should build a complete dataset;
- deterministic output;
- reproducible builds;
- incremental updates whenever possible;
- no manual editing of generated files;
- modular pipeline;
- provider-based architecture;
- human-readable console output.

---

# Repository Layout

```text
octobeat/

├── octobeat/
│   ├── cli.py
│   ├── commands/
│   ├── config/
│   ├── providers/
│   ├── pipeline/
│   ├── cache/
│   ├── core/
│   ├── io/
│   └── ui/
│
├── tests/
├── fixtures/
└── pyproject.toml
```

---

# Relationship with the Ecosystem

```text
YouTube / Local Files
          │
          ▼
     OctoBeat CLI
          │
          ▼
      Datasets
          │
          ▼
     catalog.json
          │
          ▼
     OctoBeat App
```

The CLI is responsible for producing datasets.

The application is responsible for consuming them.

---

# Roadmap

## Phase 1

- Configuration
- Workspace
- Dataset Builder

## Phase 2

- Metadata providers
- Media extraction
- Cover download

## Phase 3

- Beat analysis
- SongMap generation
- Validation

## Phase 4

- Automatic catalog generation
- Dataset verification
- Statistics

## Phase 5

- Advanced tempo analysis
- Downbeat detection
- Time signature detection
- Section analysis

## Phase 6

- Additional metadata providers
- Plugin system
- Dataset export/import

---

# Current Status

Current implementation includes:

- Local file support
- YouTube support
- Audio decoding
- SongMap generation
- Dataset loading
- Audio caching

The next milestone is to transform the CLI into a complete dataset builder capable of constructing and maintaining the entire OctoBeat library from a single command.