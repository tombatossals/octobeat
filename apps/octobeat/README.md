# OctoBeat Web App

> **The web interface for practicing musical technique with real songs.**

OctoBeat is a Next.js application that consumes SongMaps to keep
technical exercises synchronized with real recordings.

It plays the recording (local audio/video or YouTube), renders a
synchronized exercise overlay, shows synced lyrics and provides a
browsable catalog of datasets.

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
with `metadata.json`, `songmap.json`, `recording.webm`, `video.mp4`
and `cover.jpg`.

## Run the dev server

```bash
cd apps/octobeat
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000).

> The dev server uses port `3001` when `3000` is already in use.

## Build for production

```bash
pnpm build
pnpm start
```

---

# Features

## Catalog

- browse the catalog, randomized each session;
- filter by genre and preferred genres;
- search songs with a command palette (`⌘K`);
- open any song directly from the search results.

## Player

- plays local audio + video, or YouTube;
- transport controls with keyboard shortcuts;
- seek bar with elapsed time and percentage;
- volume control (`↑`/`↓`) with a slider and percentage readout;
- fullscreen toggle (`F`);
- auto-advances to the next song when playback ends.

### Song timeline

- section bars proportional to each section's duration, always in
  **song time** (unaffected by the video offset);
- active section highlighted with a live position marker and current
  time;
- click a section to seek to its start.

### Video synchronization

When a dataset has a synced video (`SongMap.media.video`), the video is
muted and follows the audio in `videoTime = songTime + videoOffset`. A
**Video offset** control (shown in the transport overlay) lets you fine
tune the offset in ±10 ms steps and save the correction; the correction
persists in `localStorage` for that dataset and is marked as "manual".

## Exercises

- Stick Control exercises synchronized with the beat grid;
- difficulty selector (Easy / Medium / Hard) with shortcuts `1`/`2`/`3`;
- countdown before the music starts;
- a now-playing summary with title, artist, album, genre, year and BPM.

## Lyrics

- synchronized lyrics rendered over the video;
- embedded in the SongMap when available, with an LRCLIB fallback.

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
| `1` / `2` / `3`            | Difficulty Easy/Med/Hard  |

---

# Project Structure

```text
apps/octobeat/

├── app/                    # Next.js app router
├── features/
│   ├── exercises/          # exercise overlay + difficulty
│   ├── library/            # catalog, search, filter
│   ├── lyrics/             # synced lyrics
│   ├── overlay/            # logo, debug HUD
│   ├── player/             # player, controls, now playing
│   ├── settings/           # settings dialog + toast
│   └── ui/                 # UI visibility levels
├── lib/                    # library wiring, shortcuts
└── public/resources/       # dataset resources (catalog + songs)
```

The UI is organized in three visibility levels:

1. always visible — logo, difficulty, headers, exercises, lyrics;
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
