# SNG Format Research

> **Investigation of the `.sng` container used by Clone Hero / YARG.**

Status: **Research + fixtures + parser** (Phase 1 — SNG)

This document records what we found by inspecting real `.sng` files. It is the
reference for the `SNGProvider` implementation. Synthetic fixtures are built by
`octobeat/fixtures/sng.py` (see section 8) and consumed by the parser.

---

# 1. What a `.sng` Is

A `.sng` is a **binary container** that groups a set of files (chart, audio,
cover art) plus song metadata into a single file. It is the distribution format
used by Clone Hero (and read by YARG) for community charts.

The container itself carries **no music timing**; the timing lives inside a
`notes.mid` (or `notes.chart`) file stored in the container. The metadata section
is the equivalent of a `song.ini`.

## 1.1 Reference implementations

- **Format specification (authoritative):**
  <https://github.com/mdsitton/SngFileFormat>
  - Spec + rationale: `README.md`
  - **Reference parser/serializer: `SngTool/SngLib/SngSerializer.cs`**
  - **Metadata key registry: `SngTool/SngCli/KnownKeys.cs`**
  - CLI tool (`SngCli`) for encoding/decoding (transcodes audio to Opus, images to JPEG)
- **YARG parser:** `YARC-Official/YARG.Core` → `YARG.Core/IO/SngHandler/SngFile.cs`
- **Clone Hero parser:** `CloneHero/CloneHero` (unpacking the container)

> Note: YARG also supports a separate, encrypted `.yarg` container
> (`YARGSongFileStream`, magic `YARGSONG`). That is **not** the `.sng` format.

> Our `SNGProvider` was checked against the reference serializer: header,
> metadata pairs (`int32` length + UTF-8 bytes), file index with **absolute**
> `contentsIndex`, and the XOR mask formula all match
> (`data[i] ^= (i & 0xFF) ^ seed[i & 0xF]`; the reference's `Vector<byte>`
> version is a pure performance optimization).

---

# 2. Container Structure

A `.sng` is built from four sections in fixed order. All integers are
**little-endian**.

| Section     | Purpose                                          |
| ----------- | ------------------------------------------------ |
| `Header`    | Magic + format version + XOR mask                |
| `Metadata`  | Key/value song metadata (like `song.ini`)        |
| `FileIndex` | Table of files: name, length, offset             |
| `FileData`  | The actual file bytes, XOR-masked                 |

## 2.1 Header

| Field            | Type   | Size | Notes                                          |
| ---------------- | ------ | ---- | ---------------------------------------------- |
| `fileIdentifier` | bytes  | 6    | ASCII magic `SNGPKG`                           |
| `version`        | uint32 | 4    | Format version (samples seen: `1`)             |
| `xorMask`        | bytes  | 16   | Random bytes used to mask `FileData`           |

Observed on the Weezer sample:

```
offset 0x00: 53 4e 47 50 4b 47   "SNGPKG"
offset 0x06: 01 00 00 00         version = 1
offset 0x0a: 5d f5 3c 5f d7 12 f1 92 cb 4f dd e7 09 59 e3 5d   xorMask
```

## 2.2 Metadata section

| Field           | Type     | Size              |
| --------------- | -------- | ----------------- |
| `metadataLen`   | uint64   | 8                 |
| `metadataCount` | uint64   | 8                 |
| pairs           | repeated | until metadataLen |

Each `MetadataPair` (a key/value string pair):

| Field     | Type   | Size   |
| --------- | ------ | ------ |
| `keyLen`  | int32  | 4      |
| `key`     | string | keyLen |
| `valueLen`| int32  | 4      |
| `value`   | string | valueLen|

Keys seen in the Weezer sample:

```
name, artist, album, genre, year, charter, song_length,
diff_band, diff_guitar, diff_bass, diff_drums, diff_drums_real,
diff_vocals, preview_start_time, icon, loading_phrase,
album_track, hopo_frequency, pro_drums, diff_* (several),
banner_link_a, link_name_a
```

Most values are **strings**; consumers decide how to parse them (bool/int/float).
`preview_start_time` is in **milliseconds**. `song_length` is in **milliseconds**.

The full set of known keys (and their value types) is the metadata key
registry in the reference repo (`SngTool/SngCli/KnownKeys.cs`). Keys relevant to
OctoBeat timing:

| Key                  | Type     | Notes                                |
| -------------------- | -------- | ------------------------------------ |
| `song_length`        | integer  | total length, ms                     |
| `delay`              | integer  | audio delay offset, ms (used by games for sync) |
| `preview_start_time` | integer  | preview start, ms                    |
| `version`            | integer  | chart/format version                 |
| `name` / `artist`    | string   | song identity                        |

> `delay` is a sync offset used by Clone Hero to compensate for audio latency.
> It is a candidate input for the chart/audio validation milestone.

> The set of keys follows the `song.ini` conventions documented in
> [TheNathannator/GuitarGame_ChartFormats](https://github.com/TheNathannator/GuitarGame_ChartFormats).

## 2.3 FileIndex section

| Field         | Type     | Size              |
| ------------- | -------- | ----------------- |
| `fileMetaLen` | uint64   | 8                 |
| `fileCount`   | uint64   | 8                 |
| entries       | repeated | until fileMetaLen |

Each `FileMeta` entry:

| Field           | Type   | Size | Notes                                          |
| --------------- | ------ | ---- | ---------------------------------------------- |
| `filenameLen`   | byte   | 1    | Length of the file name (≤ 255)                |
| `filename`      | string | n    | Relative path, `/` separates folders           |
| `contentsLen`   | uint64 | 8    | Unmasked length in bytes                       |
| `contentsIndex` | uint64 | 8    | **Absolute** byte offset from start of the `.sng` file |

> Important: `contentsIndex` is **absolute**, not relative to the FileData
> section. Our first parse used a relative offset and produced garbage; using
> the absolute offset unmasked the files correctly.

Files seen in the Weezer sample:

```
drums_2.opus, guitar.opus, drums_3.opus, rhythm.opus,
vocals.opus, album.jpg, crowd.opus, song.opus, drums_1.opus,
notes.mid
```

The chart file is always `notes.mid` or `notes.chart`.

## 2.4 FileData section

| Field          | Type   | Size              |
| -------------- | ------ | ----------------- |
| `fileDataLen`  | uint64 | 8                 |
| `fileDataArray`| bytes  | fileDataLen       |

Each file's bytes are XOR-masked. To recover the real bytes:

```
for i in 0 .. len(masked)-1:
    xorKey = xorMask[i % 16] ^ (i & 0xFF)
    fileBytes[i] = masked[i] ^ xorKey
```

> The mask index `i` is the position **within the file**, not the absolute
> container position.

---

# 3. The `notes.mid` Chart

The chart file inside the container is a **standard MIDI file (SMF), format 1**.
Timing is encoded as MIDI events.

## 3.1 Header

```
MThd  length=6  format=1  ntrks=8  division=480
```

- `division = 480` → **480 ticks per quarter note (PPQ)**.
- One beat = 480 ticks. One bar (4/4) = 1920 ticks.

## 3.2 Tracks observed

| Track | Name          | Content                                  |
| ----- | ------------- | ---------------------------------------- |
| 0     | `sayitaintso` | **Tempo map + time signature**           |
| 1     | `PART DRUMS`  | Drum chart notes + `[mix]`/`[play]` texts |
| 2     | `PART BASS`   | Bass chart notes                         |
| 3     | `PART GUITAR` | Guitar chart notes + `[map ...]` texts    |
| 4     | `PART VOCALS` | Vocal notes + crowd/`[idle]` texts        |
| 5     | `EVENTS`      | **Sections + music start/end markers**   |
| 6     | `VENUE`       | Lighting/show events (not timing)        |
| 7     | `BEAT`        | **Explicit beat/downbeat markers**       |

Track names vary by charter; the **roles are identified by name**: `PART ...`
for instruments, `EVENTS`, `BEAT`.

## 3.3 Tempo map (track 0)

Tempo changes are MIDI **Set Tempo** meta events (`0x51`), value in
microseconds per quarter note:

```
tick        BPM
0           76.0
49920       76.1
65280       76.0
101760      77.0
103680      75.0
105600      76.1
119040      76.0
126720      76.1
134400      75.0
136320      76.8
138240      76.0
140160      77.0
142080      75.0
144000      76.0
149760      75.7
155520      73.95
```

> The Weezer sample is a **Rock Band (Harmonix) chart**: the tempo map captures
> the *recorded* micro-variations of the band performance (≈76 BPM with small
> ±1 BPM jitter). This is common for `charter = Harmonix` charts. Community
> charts authored in Moonscraper usually use a constant tempo.
>
> Consequence: we must **integrate the tempo map** to convert ticks → seconds;
> a single global BPM is not accurate enough for this class of chart.

## 3.4 Time signature (track 0)

MIDI **Time Signature** meta event (`0x58`): `4/4` at tick 0
(numerator=4, denominator=2², clocksPerClick=24, thirtySecondsPerQuarter=8).

Multiple time signatures are possible; the sample has one.

## 3.5 Beats and downbeats (track 7 `BEAT`)

The `BEAT` track stores explicit beat markers as note-on events (velocity > 0):

| Pitch | Meaning          |
| ----- | ---------------- |
| 12    | **Downbeat** (bar start) |
| 13    | Beat (regular)   |

Observed on the sample:

```
332 beats total
 83 downbeats (pitch 12)  → every 1920 ticks
249 regular   (pitch 13)  → every 480 ticks
```

The beat grid is perfectly uniform (`delta histogram: {480: 331}`). Beats start
at tick 0; the last beat is at tick 158880.

> The `BEAT` track gives us the beat grid directly. It is a superset of what we
> can derive from the tempo map. When a chart lacks a `BEAT` track (some
> community charts), beats must be derived from the tempo map + time signature.

## 3.6 Sections (track 5 `EVENTS`)

Sections are text meta events in the `EVENTS` track with the form
`[section <name>]`:

```
tick     name        time (s)  bar
3840     gtr_intro   6.32      3
19200    verse_1     31.58     11
30720    verse_1a    50.53     17
38400    verse_2     63.16     21
49920    chorus_1    82.11     27
65280    gtr_lick    107.34    35
72960    verse_3     119.97    39
88320    chorus_2    145.23    47
103680   bridge      170.45    55
122880   gtr_solo    202.04    65
134400   chorus_3    220.97    71
149760   outro       246.25    79
```

Additional marker texts in the same track:

| Text             | Meaning                       |
| ---------------- | ----------------------------- |
| `[music_start]`  | Where the music begins (offset) |
| `[music_end]`    | Where the music ends          |
| `[end]`          | End of chart                  |
| `[section <x>]`  | Section change                |
| `[crowd_*]`      | Crowd intensity (not timing)  |

`[music_start]` on the sample is at tick 5520 → 9.08 s. This is a candidate for
the SongMap **offset**.

> Section names from the community (e.g. `gtr_intro`, `verse_1a`, `gtr_lick`)
> are noisy and will need the **normalization** step from the plan
> (`intro → Intro`, `verse 1 → Verse`, `chorus → Chorus`, ...).

---

# 4. Units and conversions

| Unit     | Value                          |
| -------- | ------------------------------ |
| tick     | 1/480 quarter note             |
| beat     | 480 ticks                      |
| bar (4/4)| 1920 ticks (4 beats)           |
| time     | integrate `Set Tempo` events   |

Tick → seconds conversion:

```
tickToSec(t) = Σ over tempo segments: (Δticks * usecPerQuarter) / 1e6 / 480
```

## 4.1 Duration cross-check

| Source          | Value          |
| --------------- | -------------- |
| `song_length` metadata | 263.117 s |
| Audio `song.opus`      | 263.12 s   |
| Chart last beat        | 261.44 s   |
| Chart `[end]`          | 262.25 s   |

The chart and the audio agree within ~1 s, confirming the conversion math.

---

# 5. Dependencies for the parser

- **`.sng` container**: no external dependency required — ~150 lines of Python
  (magic check, header, metadata pairs, file index, XOR unmask).
- **`notes.mid`**: a MIDI parser is needed. Options:
  - `mido` (pure Python, easy, well tested);
  - or a small hand-rolled SMF parser (~100 lines) — the subset needed (meta
    events, note-on) is small.
  - Recommendation for the `SNGProvider`: use `mido` for the MIDI side; write
    the container reader by hand.

---

# 6. What OctoBeat should extract (scope)

From a `.sng` we will produce the canonical `TimingData`:

| Data               | Source in chart                      |
| ------------------ | ------------------------------------ |
| BPM / tempo map    | `Set Tempo` events (track 0)         |
| Time signatures    | `Time Signature` events (track 0)    |
| Beats              | `BEAT` track note-ons (fallback: derived from tempo map) |
| Downbeats/bars     | `BEAT` pitch 12 markers              |
| Sections           | `[section <name>]` texts (track `EVENTS`) |
| Music start/offset | `[music_start]` text (track `EVENTS`) |

Everything else (instrument notes, venue events) is out of scope for timing.
The container audio tracks (`.opus`) are *not* used by OctoBeat — OctoBeat
downloads its own audio; the chart is only a timing source.

---

# 7. Open questions

- [x] Version handling: samples only show version `1`. The parser rejects
      `version != 1` with `UnsupportedVersionError`.
- [x] Charts without a `BEAT` track: beats are derived from the tempo map +
      time signature, bounded by the `[end]` marker.
- [ ] `notes.chart` variant: some `.sng` containers ship `notes.chart` instead
      of `notes.mid`. The parser detects the file name but the `.chart` format
      is a later milestone.
- [x] Multiple time signatures and their tick positions: supported (the
      `multiple-timesig` fixture and `Mountain`/`Pixies` samples exercise them).

---

# 8. Synthetic fixtures

Real `.sng` files weigh 5–18 MB (audio dominates). For regression testing we
generate **small, deterministic synthetic fixtures** instead, following the same
pattern as the audio fixtures in `octobeat/fixtures/generate.py`.

## 8.1 Generator

`octobeat/fixtures/sng.py` builds `.sng` containers from scratch:

- a hand-rolled **SMF writer** (`_build_notes_mid`, format 1, 480 PPQ) producing
  the `notes.mid` chart with tempo map, time signatures, `[section ...]` events
  and the `BEAT` track (pitch 12 downbeat / 13 regular);
- a hand-rolled **SNG container writer** (`_build_sng_container`) emitting the
  SNGPKG header, metadata pairs, file index with absolute offsets, and
  XOR-masked file data.

No third-party dependency is required. `build_sng_fixtures(output)` writes every
case plus a `manifest.json` with the ground truth.

## 8.2 Cases

| Fixture             | Ground truth                                   |
| ------------------- | ---------------------------------------------- |
| `constant-tempo`    | 120 BPM, 4/4, 16 beats (4 downbeats), `intro`/`verse`, `[music_start]` |
| `tempo-change`      | 120 → 150 BPM at tick 3840, 4/4, 24 beats (6 downbeats) |
| `multiple-timesig`  | 100 BPM, 4/4 → 3/4 at tick 1920, 16 beats (5 downbeats) |
| `sections`          | 140 BPM, 4/4, 32 beats (8 downbeats), 8 sections (`intro`, `verse 1`, `chorus`, `verse 2`, `chorus`, `bridge`, `solo`, `outro`) |
| `no-beat-track`     | 90 BPM, 4/4, 12 beats — **no `BEAT` track** (beats must be derived) |
| `invalid-magic`     | Container bytes with a wrong magic (`NOTSNG...`) |
| `unsupported-version` | Valid container with `version = 99`          |
| `truncated`         | Container cut in half (dangling file index)   |
| `corrupt-chart`     | Valid container whose `notes.mid` header is destroyed |

The five "valid" cases encode their expected values into `manifest.json` and are
used by `tests/test_sng_fixtures.py` to assert the generator itself; the parser
tests (`tests/test_sng_provider.py`) consume the same fixtures.

> Note: `no-beat-track` intentionally has no `BEAT` track, so the manifest
> documents the beats that the parser should *derive* from the tempo map.

---

# 9. SNGProvider (implemented)

`octobeat/timing/sng.py` implements the parser.

## 9.1 Layout

```
octobeat/
├── models/timing.py     # canonical TimingData model
├── timing/
│   ├── base.py          # TimingProvider ABC + typed errors
│   ├── midi.py          # SMF parser (no external deps)
│   ├── sng.py           # SNG container + SNGProvider
│   └── factory.py       # provider registry/factory
```

`TimingProvider` is a distinct family from the media `SourceProvider`
(`providers/`). It lives in `octobeat/timing/` to avoid conflating the two.

## 9.2 Behavior

- Opens the container, validates magic (`SNGPKG`) and version (only `1`).
- Reads metadata pairs (exposed on `SngFile.metadata`).
- Reads the file index; **absolute** offsets are used to slice file bytes,
  then XOR-unmasked (`xorMask[i % 16] ^ (i & 0xFF)`).
- Extracts `notes.mid` (falls back to `notes.chart` name, though parsing the
  `.chart` format itself is a later milestone) and parses it with the
  hand-rolled SMF parser in `timing/midi.py`.
- Produces canonical `TimingData`:
  - `tempos` — `Set Tempo` segments with `start_beat`, `start_time`, `bpm`;
  - `beats` — from the `BEAT` track note-ons (pitch 12 downbeat, 13 regular),
    or **derived from the tempo map + time signatures** when the track is
    absent (bounded by the `[end]` marker);
  - `time_signatures` — `Time Signature` events mapped to start beats;
  - `sections` — `[section <name>]` texts mapped to `start_beat`/`start_time`
    (name normalization is a separate task).

Tick → seconds integrates the tempo map (microseconds per quarter ÷ PPQ), which
matters for Harmonix charts that carry recorded tempo micro-variations.

## 9.3 Error handling

| Error (`TimingError` subclasses) | When                              |
| -------------------------------- | --------------------------------- |
| `CorruptFileError`               | bad magic, truncated, bad chart   |
| `UnsupportedVersionError`        | `version != 1`                    |
| `MissingChartError`              | no `notes.mid`/`notes.chart`      |

All are catchable so the CLI can fall back to audio analysis. Missing sections /
`BEAT` track are not errors: they produce empty lists / derived beats.

## 9.4 Validation

- All 13 real Harmonix samples in `sng/` parse end-to-end (tempo, beats,
  sections, time signatures).
- `tests/test_sng_provider.py` (20 tests): fixtures valid + invalid cases,
  tick→second conversion, tempo changes, sections, derived beats, factory.
- `ruff` + `mypy` clean.

## 9.5 Open items

- `notes.chart` in containers is detected but not parsed (later milestone).

---

# 10. Chart/audio validation (implemented)

`octobeat/validation/timing.py` compares a chart-derived `TimingData`
against the audio and produces a per-check diagnostic.

## 10.1 Checks

| Check             | What it compares                       | Tolerance (configurable) |
| ----------------- | -------------------------------------- | ------------------------ |
| `bpm`             | chart tempo vs audio BPM/candidates    | 4 % (direct), 8 % (half/double); accepts any strong audio candidate; skips when audio not periodic |
| `duration`        | last chart beat vs audio duration      | 2.0 s |
| `offset`          | first chart beat vs audio start        | 500 ms (half a beat) |
| `tempo-changes`   | relative tempo **span** of chart vs audio | 15 % span difference |
| `drift`           | onset coverage of the chart beat grid  | ≥ 35 % coverage |

Each check is a `TimingCheck(name, ok, detail, warn)`. A mismatch is a
**warning, never a hard failure** — the dataset must still build from
audio when a chart is unusable.

### BPM robustness

The audio `estimate_tempo` often resolves to a sub-harmonic or double of
the true tempo with these game mix masters. The check therefore:

1. skips when the audio is not clearly periodic (`bpm_score` below the
   floor) — the audio cannot say the chart is wrong;
2. accepts half/double time with a looser tolerance;
3. accepts when the chart BPM matches **any strong autocorrelation
   candidate** of the audio.

### Tempo-changes as a span

Counting tempo *changes* is unreliable: Harmonix charts carry recorded
micro-variations and the audio tempo map carries estimator noise. The
check compares the **relative span** (max deviation from the mean) of
each tempo set, so a constant-tempo chart passes even when the audio
estimator wanders.

## 10.2 Corrected offset

`TimingValidation.corrected_offset` reports when the audio start differs
from the chart's first beat. It is **informational**: the SongMap keeps
the chart's own offset because the chart defines the beat grid, and
re-writing it from audio analysis would desynchronise the beats.

## 10.3 Confidence

`confidence_from_validation(checks)` derives a value in `[0, 1]`:

- 1.0 — perfect chart match;
- lowered per failed check (bpm −0.30, drift −0.30, duration −0.15,
  offset −0.15, tempo-changes −0.10);
- the result flows into `SongMap.timing.confidence` and dataset
  `metadata.json` `timing.confidence`, alongside `timing.source`.

## 10.4 Offset in TimingData

`TimingData.offset` is the time of the **first beat** of the chart (0.0
for these charts). The Rock Band `[music_start]` marker is a *section*
marker that may occur after the first beat; using it as the SongMap
offset would desynchronise the grid. The SongMap builder uses the
chart's first beat as the offset, keeping beats and offset consistent.
