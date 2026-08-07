# ADR-0007 — SongMap Describes a Recording, Not a Song

**Status:** Accepted
**Date:** 2026-08-02

---

# Context

One of the earliest design questions was to determine exactly what a SongMap represents.

Several possibilities were considered:

* a musical work ("song");
* a score;
* a recording;
* a video;
* a practice session.

Although these concepts are closely related, they represent different layers of information.

For example, a single musical work may exist in multiple recordings:

* studio version;
* live performance;
* acoustic version;
* remastered edition;
* radio edit.

Each recording has its own temporal characteristics.

Even when the musical composition remains unchanged, timing, tempo, structure and duration may differ significantly.

---

# Decision

A **SongMap always describes one specific audio recording**.

It does not describe the abstract musical work.

It does not describe a video.

It does not describe a performance by the user.

It does not describe a practice session.

Each recording has its own independent SongMap.

---

# Consequences

## Positive

### Clear Semantics

The meaning of a SongMap becomes unambiguous.

Every timestamp, beat and bar refers to one specific recording.

---

### Accurate Synchronization

Applications synchronize against a concrete recording rather than an abstract musical composition.

This guarantees that temporal information always matches the analysed source.

---

### Multiple Versions

Different recordings of the same musical work naturally produce different SongMaps.

Examples include:

* album version;
* live version;
* acoustic version;
* remastered edition.

No special handling is required.

---

### Independence from Media

A SongMap represents the temporal structure of the recording itself.

The same SongMap may be associated with:

* a local audio file;
* a YouTube video;
* another playback source.

The playback medium does not change the temporal model.

---

# Negative Consequences

Applications must distinguish between a musical work and a recording.

The Music Catalog is therefore responsible for modelling relationships such as:

* one song;
* many recordings;
* one SongMap per recording.

This introduces an additional conceptual layer but results in a clearer architecture.

---

# Alternatives Considered

## SongMap Describes a Song

One option was to define SongMap as describing the musical work itself.

This option was rejected because a musical work has no unique temporal structure.

Different recordings of the same composition frequently differ in duration, tempo and arrangement.

---

## SongMap Describes a Video

Another option was to associate SongMap directly with a YouTube video or another media source.

This option was rejected because playback sources are implementation details.

A recording may exist in multiple media formats without changing its temporal structure.

---

## SongMap Describes a Practice Session

Another possibility was to include educational information together with temporal analysis.

This option was rejected because practice sessions belong to the application layer rather than the temporal description of the recording.

---

# Architectural Principles Established

This decision establishes the following principles:

* SongMap always represents one recording.
* Every recording has its own SongMap.
* A musical work may have multiple recordings.
* Playback providers are independent of SongMap.
* Educational content is independent of SongMap.

---

# Future Evolution

Future ecosystem components should model these concepts independently.

```text id="concept-model"
Song
 │
 ├── Recording
 │      │
 │      └── SongMap
 │
 ├── Recording
 │      │
 │      └── SongMap
 │
 └── Recording
        │
        └── SongMap
```

This model naturally supports multiple recordings while preserving a deterministic temporal description for each one.

---

# Scope

This decision applies to the SongMap specification and every application that consumes SongMaps.

It also establishes the conceptual relationship between SongMap and the future Music Catalog.

---

# Related Documents

* `docs/specs/songmap/SPEC.md`
* `docs/prd/PRD.md`
* `docs/adr/ADR-0001-songmap-as-contract.md`
* `docs/adr/ADR-0005-separate-music-catalog-from-songmap.md`

---

# Notes

This ADR defines one of the core concepts of the SongMap specification.

The distinction between **Song** (the musical work) and **Recording** (a specific performance or production of that work) ensures that SongMap remains deterministic, unambiguous and independent of playback technology.

This decision is summarized by the project's guiding principle:

> **A SongMap is a deterministic temporal description of a specific audio recording.**
