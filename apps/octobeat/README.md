# OctoBeat Web App

> **The web interface for practicing musical technique with real songs.**

OctoBeat is a Next.js application that consumes SongMaps to keep
technical exercises synchronized with real recordings.

It plays the recording with a full-screen waveform, renders a
synchronized exercise overlay and provides a browsable catalog of
datasets.

---

# Getting Started

## Prerequisites

- Node.js 20+
- [pnpm](https://pnpm.io/)

## Install

From the repository root:

```bash
pnpm install
```

## Configure the catalog

The app serves dataset resources from `public/resources/`. Point a
catalog there by configuring the catalog URL in the settings dialog
(`⌘,`) — the default is `/resources`.

Copy your datasets into the public directory, or symlink them:

```bash
ln -s ~/Music/OctoBeat apps/octobeat/public/resources
```

Each dataset must contain `catalog.json`, plus per-song directories
with `metadata.json`, `songmap.json`, `recording.webm` and
`cover.jpg`.

## Run the dev server

```bash
cd apps/octobeat
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000).

> The dev server uses port `3001` when `3000` is already in use.

## Build the static site

The app is fully static: it builds to a plain folder (`out/`) that any
web server can serve — no Node app server required. The catalog and
datasets are static files fetched at runtime.

Make sure the resources symlink is in place before building:

```bash
ln -s ~/Music/OctoBeat apps/octobeat/public/resources
```

```bash
cd apps/octobeat
pnpm build
```

This generates `out/` with `index.html`, the JS/CSS bundle and a
symlink at `out/resources/` pointing at your datasets — the datasets are
**not** copied, so the build stays fast even with hundreds of gigabytes
of resources. Serve it with any static server, for example:

```bash
python3 -m http.server 3000 -d out
```

or point nginx/Apache at the `out/` directory.

---

# Features

## Catalog

- browse the catalog, randomized each session;
- filter by genre and preferred genres;
- search songs with a command palette (`⌘K`);
- open any song directly from the search results.

## Player

- plays local recordings with a full-screen waveform;
- transport controls with keyboard shortcuts;
- seek bar with elapsed time and percentage;
- volume control (`↑`/`↓`) with a slider and percentage readout;
- fullscreen toggle (`F`);
- auto-advances to the next song when playback ends.

### Song timeline

The full-screen waveform shows the song structure (sections as colored
regions) with a live progress playhead, always visible during playback.
The transport overlay keeps a seek bar with elapsed time and percentage.

## Exercises

- Stick Control exercises synchronized with the beat grid;
- speed selector (1x / 2x / 4x) with shortcuts `1`/`2`/`4`;
- countdown before the music starts;
- a now-playing summary with title, artist, album, genre, year and BPM.

## Shortcuts

Hold `Ctrl`/`Cmd` to reveal the keyboard shortcut badges on the
interface.

| Key                        | Action                    |
| -------------------------- | ------------------------- |
| `Space`                    | Play / pause              |
| `←` / `→`                  | Seek ±5s                  |
| `P` / `N`                  | Previous / next song      |
| `Home` / `End`             | Start / end of recording  |
| `↑` / `↓`                  | Volume up / down          |
| `F`                        | Toggle fullscreen         |
| `Ctrl`+`F`                 | Toggle genre filter       |
| `Ctrl`+`K`                 | Search the catalog        |
| `1` / `2` / `4`            | Speed 1x/2x/4x          |

---

# Project Structure

```text
apps/octobeat/

├── app/                    # Next.js app router
├── features/
│   ├── exercises/          # exercise overlay + speed
│   ├── library/            # catalog, search, filter
│   ├── overlay/            # logo
│   ├── player/             # player, controls, now playing
│   ├── settings/           # settings dialog + toast
│   └── ui/                 # UI visibility levels
├── lib/                    # library wiring, shortcuts
└── public/resources/       # dataset resources (catalog + songs)
```

The UI is organized in three visibility levels:

1. always visible — logo, speed, headers, exercises;
2. on pointer or shortcut activity — transport controls;
3. while holding `Ctrl`/`Cmd` — shortcut badges.

---

# Packages

The app depends on the workspace packages:

- `@octobeat/songmap` — SongMap schema, model and beat/bar helpers;
- `@octobeat/library` — catalog loading and dataset resolution;
- `@octobeat/player` — media abstraction and keyboard shortcuts;
- `@octobeat/exercises` — exercise definitions;
- `@octobeat/ui` — shared UI components (exercise renderer, seek bar, etc.).
