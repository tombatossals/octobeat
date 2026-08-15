# SongMap Specification

**Version:** 1
**Schema:** `songmap/v1`
**Status:** Draft

---

# 1. Introduction

SongMap is an open, deterministic and versioned specification for describing the **temporal structure of a specific audio recording**.

Its purpose is to provide a common language that allows independent applications to exchange temporal musical information without sharing implementation details.

SongMap is designed to be:

* deterministic;
* portable;
* extensible;
* application independent;
* instrument agnostic.

A SongMap represents **when musical events occur**, not how they should be interpreted by a particular application.

---

# 2. Scope

SongMap describes objective temporal information extracted from an audio recording.

Examples include:

* beats;
* bars;
* tempo;
* time signature;
* sections;
* tempo changes;
* markers.

SongMap deliberately excludes concepts that belong to higher application layers.

It does **not** describe:

* exercises;
* practice sessions;
* educational content;
* overlays;
* user preferences;
* statistics;
* application state.

Those concepts belong to the applications that consume SongMaps.

---

# 3. Philosophy

SongMap is based on a small number of fundamental principles.

## 3.1 A SongMap describes a recording

A SongMap always represents one specific recording.

Different recordings of the same musical work produce different SongMaps.

Examples:

* album version
* live version
* acoustic version
* remaster
* radio edit

Each recording has its own independent SongMap.

---

## 3.2 SongMap is deterministic

Running the same analysis over the same recording should always produce the same SongMap.

The only non-deterministic fields are informational metadata such as:

* generation timestamp
* generator version

Musical information must always be reproducible.

---

## 3.3 SongMap is independent

SongMap does not depend on:

* OctoBeat
* BeatEngine
* any DAW
* any player
* any programming language

Applications depend on SongMap.

SongMap never depends on applications.

---

## 3.4 SongMap is objective

SongMap contains measurable facts.

It never stores opinions or interpretations.

Examples of objective information:

* beat at 32.512 seconds
* tempo 117.2 BPM
* first beat of bar 42

Examples of subjective information:

* difficult groove
* beginner song
* energetic chorus

Those belong to other systems.

---

## 3.5 SongMap is extensible

New information may be added without breaking compatibility whenever possible.

Consumers should ignore unknown optional blocks.

---

# 4. Conceptual model

Conceptually, a SongMap is a temporal description of a recording.

```
Recording

↓

Timeline

↓

Events
```

Version 1 represents the timeline using dedicated collections.

Future versions may evolve towards a unified event model while preserving compatibility.

---

# 5. Data model

A SongMap consists of:

```
SongMap

├── version

├── schema

├── generatedBy

├── createdAt

├── metadata

├── timing

├── beats

├── bars

├── sections (optional)
```

---

# 6. Metadata

The metadata block identifies the analysed recording.

It intentionally contains only the minimum information required to identify the analysed source.

It is **not** a music catalogue.

Typical information includes:

* title
* duration
* source

Information such as:

* artist
* album
* genre
* release year

belongs to an external Music Catalog.

---

# 7. Timing

The timing block defines the global temporal reference of the recording.

It contains:

* tempo
* time signature
* beat offset
* analysis confidence
* optional tempo map
* optional source

Applications should use this information only as a global reference.

Precise synchronization should always rely on the beat list.

## 7.0 Source

The optional `source` field records where the timing information came
from, so consumers know why a SongMap has a given quality:

```json
{ "source": "sng" }
{ "source": "audio-analysis" }
```

Known values:

* `sng` — community chart (Clone Hero / YARG)
* `midi` — MIDI chart
* `chart` — `.chart` text format
* `audio-analysis` — BeatEngine audio detection
* `manual` — manually authored/edited

The `confidence` field reflects how reliable the timing is. A chart
whose timing matches the audio closely receives a high confidence; an
offset-corrected chart or a pure audio analysis receives a lower one.

## 7.1 Tempo map

The `tempoMap` block is optional. When present, it describes how the
tempo changes over time as a list of segments, each with a start time
and a tempo:

```json
{
  "tempoMap": [
    { "time": 0.0, "bpm": 162 },
    { "time": 135.2, "bpm": 175 }
  ]
}
```

Between two consecutive segments the tempo is interpolated linearly,
which supports both abrupt changes (two segments at the same time) and
gradual ramps such as accelerando and ritardando.

When the `tempoMap` block is absent, the tempo is assumed to be
constant at the global `bpm` value.

## 7.2 Confidence

The `confidence` field is a value in `[0, 1]` describing the overall
reliability of the analysis.

It is a combination of independent metrics:

* tempo confidence — how unambiguous the detected tempo is;
* beat confidence — how well the beats align with the onsets;
* grid stability — how regular the beat intervals are.

Applications should treat low-confidence SongMaps with caution.

---

# 8. Beats

The beat collection defines every beat of the recording.

Each beat contains only:

* index
* time

Beat indices are absolute and continuous: when the tempo changes, the
index keeps counting and only the spacing between beats changes.

No additional musical information should be duplicated.

Applications reconstruct higher level concepts using other collections.

---

# 9. Bars

Bars reference the beat collection.

Each bar identifies the first beat that belongs to it.

This avoids duplicating information while allowing efficient reconstruction of the musical timeline.

The first beat of a bar (its downbeat) is detected from the onset
evidence rather than assumed to be beat 1, so a recording that begins
on a pickup or an off-beat is represented correctly.

---

# 10. Sections

The optional `sections` collection describes the musical form of the
recording (intro, verse, chorus, bridge, solo, outro, ...).

Each section references the beat collection preferentially:

```json
{
  "sections": [
    { "index": 1, "name": "Intro",  "startBeat": 1,  "startTime": 0.0 },
    { "index": 2, "name": "Verse",  "startBeat": 33, "startTime": 11.8 },
    { "index": 3, "name": "Chorus", "startBeat": 65, "startTime": 23.6 }
  ]
}
```

Fields:

* `index` — 1-based, continuous section number;
* `name` — normalized section name (see normalization below);
* `startBeat` — index of the first beat of the section (preferred);
* `startTime` — seconds into the recording (convenience);
* `sourceName` (optional) — the original label from the chart.

Sections reference **beats preferentially** and keep `startTime` for
convenience (`Section → startBeat → SongMap → timestamp`), so the UI
timeline, navigation and practice-by-section features can rely on the
same structure.

## 10.1 Name normalization

Chart labels vary widely (`"section Chorus"`, `"verse 1"`, `"hook"`,
`"Solo 2"`). The `name` field uses normalized, predictable names:

```
intro   → Intro
verse   → Verse
verse 1 → Verse
chorus  → Chorus
hook    → Chorus
bridge  → Bridge
solo    → Solo
outro   → Outro
```

Unrecognized labels are kept, normalized to Title Case. The original
chart label is preserved in `sourceName` when it differs from `name`.

---

# 11. Versioning

Every SongMap declares:

* format version
* schema identifier

Example:

```json
{
    "version":1,
    "schema":"songmap/v1"
}
```

Breaking compatibility requires a new schema identifier.

---

# 12. Compatibility

SongMap follows a forward-compatible design whenever possible.

Allowed changes within the same schema include:

* adding optional blocks;
* adding optional fields;
* extending metadata.

Breaking changes require a new major schema.

Applications must ignore unknown optional fields.

---

# 13. Future evolution

Version 1 intentionally keeps the model minimal.

Future versions may introduce optional blocks such as:

* markers
* cues
* chords
* key
* groove
* energy

without modifying the existing contract.

---

# 14. Future timeline model

Although version 1 uses dedicated collections, the long-term conceptual model is an event timeline.

```
Timeline

↓

Beat

↓

Bar

↓

Section

↓

Marker

↓

Tempo Change

↓

Cue
```

Applications should not assume that future SongMaps will always be organised using the same internal collections.

---

# 15. Design goals

SongMap has four primary goals.

## Simplicity

The format should remain easy to understand and implement.

---

## Stability

Applications should continue working across future versions whenever possible.

---

## Reusability

The same SongMap should be consumable by completely different applications.

Examples:

* educational software
* visualisers
* DAWs
* analysis tools
* AI systems

---

## Longevity

SongMap should outlive any particular implementation.

BeatEngine and OctoBeat are consumers of SongMap, not its definition.

---

# 16. Non-goals

SongMap is not:

* a music catalogue;
* a notation format;
* a MIDI replacement;
* a DAW project;
* a practice session format;
* a user profile.

Those concerns belong to independent specifications.

---

# 17. Ecosystem

SongMap is intended to become the common contract of the OctoBeat ecosystem.

Typical architecture:

```
                BeatEngine
                     │
                     ▼

                SongMap (.json)

         ┌───────────┼────────────┐
         ▼           ▼            ▼

    OctoBeat   SongMap Editor   Viewer
```

Every component communicates exclusively through SongMap.

---

# 20. Guiding principle

> **A SongMap is a deterministic temporal description of a specific audio recording.**

Every future design decision should remain consistent with this statement.
