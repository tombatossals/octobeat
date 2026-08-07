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

* VideoStick
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

├── recording

├── timing

├── beats

└── bars
```

---

# 6. Recording

The recording block identifies the analysed recording.

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

Applications should use this information only as a global reference.

Precise synchronization should always rely on the beat list.

---

# 8. Beats

The beat collection defines every beat of the recording.

Each beat contains only:

* index
* time

No additional musical information should be duplicated.

Applications reconstruct higher level concepts using other collections.

---

# 9. Bars

Bars reference the beat collection.

Each bar identifies the first beat that belongs to it.

This avoids duplicating information while allowing efficient reconstruction of the musical timeline.

---

# 10. Versioning

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

# 11. Compatibility

SongMap follows a forward-compatible design whenever possible.

Allowed changes within the same schema include:

* adding optional blocks;
* adding optional fields;
* extending metadata.

Breaking changes require a new major schema.

Applications must ignore unknown optional fields.

---

# 12. Future evolution

Version 1 intentionally keeps the model minimal.

Future versions may introduce optional blocks such as:

* sections
* tempoChanges
* markers
* cues
* chords
* key
* groove
* energy

without modifying the existing contract.

---

# 13. Future timeline model

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

# 14. Design goals

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

BeatEngine and VideoStick are consumers of SongMap, not its definition.

---

# 15. Non-goals

SongMap is not:

* a music catalogue;
* a notation format;
* a MIDI replacement;
* a DAW project;
* a practice session format;
* a user profile.

Those concerns belong to independent specifications.

---

# 16. Ecosystem

SongMap is intended to become the common contract of the VideoStick ecosystem.

Typical architecture:

```
                BeatEngine
                     │
                     ▼

                SongMap (.json)

         ┌───────────┼────────────┐
         ▼           ▼            ▼

    VideoStick   SongMap Editor   Viewer
```

Every component communicates exclusively through SongMap.

---

# 17. Guiding principle

> **A SongMap is a deterministic temporal description of a specific audio recording.**

Every future design decision should remain consistent with this statement.
