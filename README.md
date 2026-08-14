# OctoBeat

> **Practice musical technique synchronized with real songs.**

OctoBeat is an open ecosystem for practicing technical exercises in
time with real recordings. It consists of:

- **SongMap** — an open specification describing the temporal structure
  of an audio recording (beats, bars, tempo map, confidence);
- **BeatEngine** — a CLI (`octobeat`) that downloads, analyses and
  builds complete datasets from YouTube or local files;
- **OctoBeat app** — a web interface that plays recordings and keeps
  exercises synchronized with the music.

```
YouTube / Local file
        │
        ▼
  OctoBeat CLI  ──►  Dataset + catalog.json
        │
        ▼
   OctoBeat app
```

The core idea: **the detector provides evidence; the musical grid
governs the SongMap.**

---

# Repository Layout

This is a pnpm monorepo.

```text
octobeat/

├── apps/
│   └── octobeat/          # Next.js web application
│
├── packages/
│   ├── exercises/         # exercise definitions (Stick Control)
│   ├── library/           # catalog + dataset loading
│   ├── player/            # media abstraction + shortcuts
│   ├── songmap/           # SongMap schema, model, beat/bar helpers
│   └── ui/                # shared UI components (incl. SongTimeline)
│
├── tools/
│   └── octobeat/          # BeatEngine CLI (Python)
│
└── docs/
    ├── prd/               # Product Requirements Document
    ├── adr/               # Architecture Decision Records
    ├── specs/             # SongMap specification
    └── dataset/           # dataset-related notes
```

---

# Getting Started

## 1. Prerequisites

- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- Node.js 20+ and [pnpm](https://pnpm.io/)

## 2. Install dependencies

```bash
git clone git@github.com:tombatossals/octobeat.git
cd octobeat

# Python CLI
cd tools/octobeat
uv sync
cd ../..

# Web app
pnpm install
```

Verify the CLI works:

```bash
cd tools/octobeat
uv run octobeat --version
```

> Tip: with [direnv](https://direnv.net/) installed, entering the repo
> sets everything up automatically:
>
> ```bash
> cd octobeat
> direnv allow
> ```
>
> The root `.envrc` runs `pnpm install`, `tools/octobeat/.envrc` syncs
> and activates the uv environment, and `apps/octobeat/.envrc` puts the
> Next.js binaries (`next`, `tsc`, `eslint`) on your `PATH`.

## 3. Initialize the workspace

```bash
cd tools/octobeat
uv run octobeat init
```

This creates the default configuration at
`~/.config/octobeat/config.toml` with `~/Music/OctoBeat` as the
datasets directory.

## 4. Download and analyze a song

Add a song from YouTube with a single command:

```bash
uv run octobeat add https://youtu.be/KJamzD0KntE
```

The command downloads metadata, artwork and audio, analyzes the
recording, generates the SongMap, builds the dataset and updates the
catalog.

To analyze a local audio file instead:

```bash
uv run octobeat analyse /path/to/song.mp3 -o /tmp/song.songmap.json
```

Inspect the analysis with `--debug`:

```bash
uv run octobeat analyse /path/to/song.mp3 --debug
```

The result is a dataset directory like:

```text
~/Music/OctoBeat/mxpx-responsibility-kjamzd0knte/
├── metadata.json
├── cover.jpg
├── recording.mp3
└── songmap.json
```

## 5. Use it with the web interface

Serve the datasets from the app's public directory:

```bash
ln -s ~/Music/OctoBeat apps/octobeat/public/resources
```

Start the dev server:

```bash
cd apps/octobeat
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000).

The app defaults to the `/resources` catalog. If your datasets live
elsewhere, change the catalog URL in the settings dialog (`⌘,`).

Select a song, choose a difficulty, and practice Stick Control in sync
with the music. Hold `Ctrl`/`Cmd` to reveal the keyboard shortcuts.

---

# CLI Overview

```bash
octobeat init                    # initialize the workspace
octobeat add <youtube-or-file>   # build a complete dataset
octobeat analyse <file> [--debug]
octobeat analyse <file> --chart song.sng   # use a community chart for timing
octobeat inspect <song.sng>      # show a chart's timing without building
octobeat dataset reanalyse       # re-analyse every dataset
octobeat dataset verify
octobeat catalog build           # rebuild catalog.json
octobeat validate <songmap.json>
octobeat info <songmap.json>
```

See `tools/octobeat/README.md` for the full reference.

---

# What Is a SongMap?

A SongMap is a deterministic, versioned JSON document describing the
temporal structure of one specific recording.

```json
{
  "version": 1,
  "schema": "songmap/v1",
  "timing": {
    "bpm": 162,
    "offset": 0.314,
    "timeSignature": "4/4",
    "confidence": 0.96,
    "tempoMap": [
      { "time": 0.0, "bpm": 162 },
      { "time": 135.2, "bpm": 175 }
    ]
  },
  "beats": [ { "index": 1, "time": 0.314 }, "..." ],
  "bars": [ { "index": 1, "firstBeat": 1 }, "..." ]
}
```

The tempo map supports constant tempo, discrete changes and gradual
ramps (accelerando/ritardando). Bars are aligned to detected downbeats.
Confidence combines independent tempo, beat and grid metrics.

See `docs/specs/songmap/SPEC.md` for the full specification.

---

# Documentation

- `docs/prd/PRD.md` — product requirements and vision;
- `docs/adr/` — architecture decision records;
- `docs/specs/songmap/` — SongMap specification, glossary, changelog;
- `tools/octobeat/README.md` — CLI reference;
- `apps/octobeat/README.md` — web app reference.

---

# Development

## Python CLI

```bash
cd tools/octobeat
uv run pytest       # run the test suite
uv run ruff check octobeat tests
uv run mypy octobeat
```

## Web app

```bash
cd apps/octobeat
pnpm lint
pnpm build
```

---

# Roadmap

- BeatEngine alternative detection backends;
- SongMap editor;
- additional metadata providers;
- sections, markers and deeper musical analysis;
- AI-assisted practice workflows.

See `docs/prd/PRD.md` for the full roadmap.
