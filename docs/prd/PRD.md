# Product Requirements Document (PRD)

**Project:** OctoBeat
**Version:** 1.0 (Draft)
**Status:** Draft

---

# 1. Vision

OctoBeat is an application for practicing musical technique using real music.

Rather than practicing with a metronome alone, musicians practice technical exercises while remaining synchronized with the temporal structure of real recordings.

OctoBeat is the first application built on top of the SongMap specification.

The long-term vision is to create an ecosystem of interoperable tools centered around an open standard for describing the temporal structure of audio recordings.

---

# 2. Problem Statement

Technical practice is traditionally performed with a metronome.

While effective for developing timing, this approach has several limitations:

* it is repetitive;
* it lacks musical context;
* it reduces long-term motivation;
* it separates technical practice from real music.

Existing play-alongs and backing tracks provide musical accompaniment but do not synchronize exercises with the internal structure of a recording.

OctoBeat aims to bridge that gap.

---

# 3. Product Vision

The project consists of two complementary ideas.

## SongMap

SongMap is an open specification describing the temporal structure of an audio recording.

It is independent of OctoBeat and acts as the common contract between all tools.

## OctoBeat

OctoBeat consumes SongMaps to synchronize educational content with music.

It never analyzes audio directly.

---

# 4. Product Goals

## Primary Goals

* Make technical practice more engaging.
* Synchronize exercises with real music.
* Eliminate dependence on the traditional metronome.
* Build a reusable platform rather than a single application.

---

## Technical Goals

* Build an open specification (SongMap).
* Build an independent analysis engine (BeatEngine).
* Maintain a modular architecture.
* Support future AI-assisted workflows.
* Keep all components loosely coupled.

---

# 5. Target Users

Initial audience:

* drummers;
* drum teachers;
* self-taught musicians.

Future audience:

* guitarists;
* pianists;
* music schools;
* conservatories;
* educational platforms.

---

# 6. Product Scope

The ecosystem is composed of independent components with clearly defined responsibilities.

## SongMap

Open specification describing the temporal structure of recordings.

## BeatEngine

Generates SongMaps from audio recordings.

## OctoBeat

Synchronizes exercises using SongMaps.

## SongMap Editor

Allows manual editing and validation of SongMaps.

## Music Catalog

Stores musical metadata and references SongMaps.

---

# 7. MVP

The initial proof of concept is intentionally small.

It must demonstrate that the core idea works before adding complexity.

The MVP should:

* analyze one recording;
* generate a SongMap;
* display a synchronized overlay;
* allow practicing Stick Control during the entire recording.

Reference recording:

**Daft Punk – Get Lucky**

> **Status:** The MVP is implemented and has evolved into a working
> product. The current implementation supports a full CLI pipeline
> (`octobeat add`, `octobeat analyse`), a growing catalog of recordings,
> synchronized exercises and lyrics, and a web interface. See the
> repository `README.md` for the current state.

---

# 8. Out of Scope

The first version does not attempt to:

* teach musical technique;
* evaluate user performance;
* detect MIDI events;
* edit audio;
* replace a DAW;
* provide advanced music analysis;
* generate exercises automatically.

These capabilities may be considered in future versions.

---

# 9. Success Criteria

The proof of concept will be considered successful if:

* synchronization remains stable throughout the recording;
* exercises can be followed without using a metronome;
* the generated SongMap can be reused without reanalysis;
* additional recordings can be added by creating new SongMaps only.

---

# 10. Roadmap

> Phases 1–6 are implemented. The roadmap below marks the current
> status of each phase.

## Phase 1

Define the SongMap specification. ✅ Done

---

## Phase 2

Develop BeatEngine. ✅ Done

The CLI is available as `octobeat` and supports `analyse`, `add`,
`validate`, `info` and `export` commands. The analysis engine
(BeatEngine v2) detects tempo, tempo maps (including accelerando and
ritardando), downbeats, bars and confidence metrics.

---

## Phase 3

Build a SongMap Viewer. ✅ Done

The web interface (`apps/octobeat`) renders the catalog, plays
recordings (local audio/video and YouTube) and displays synchronized
exercises, lyrics and a debugging HUD.

---

## Phase 4

Develop the synchronized overlay. ✅ Done

Exercises (Stick Control) advance in sync with the detected beat grid
and support difficulty levels 1–3.

---

## Phase 5

Implement exercises and practice sessions. ✅ Done

The exercise engine is exposed through the `@octobeat/exercises`
package and rendered by the `@octobeat/ui` package.

---

## Phase 6

Build the Music Catalog. ✅ Done

The catalog is generated by the CLI (`octobeat catalog build`) and
consumed by the app through the `@octobeat/library` package.

---

## Phase 7

Develop the SongMap Editor.

A graphical editor for manually correcting SongMaps remains future
work. The CLI provides `validate` and `info` as an interim toolset.

---

## Phase 8

Add advanced music analysis.

Examples:

* sections;
* harmonic analysis;
* musical descriptors.

> Tempo changes (including accelerando and ritardando) and downbeat
> detection are already implemented in BeatEngine v2.

---

## Phase 9

Introduce AI-assisted workflows.

Examples:

* automatic practice sessions;
* adaptive difficulty;
* personalized recommendations.

---

# 11. Guiding Principles

The project follows these principles.

* SongMap is the central contract.
* Components have a single responsibility.
* Applications communicate through SongMaps.
* Manual editing is always possible.
* Components evolve independently.
* The architecture remains instrument agnostic.
* Extensibility is preferred over specialization.

---

# 12. Long-Term Vision

OctoBeat is not the final product.

It is the first application built on top of SongMap.

The long-term objective is to create an ecosystem of interoperable tools capable of sharing temporal musical information through an open specification.

Potential ecosystem components include:

* BeatEngine
* OctoBeat
* SongMap Editor
* Music Catalog
* SongMap Viewer
* AI-assisted analysis tools
* DAW integrations
* Educational applications

The long-term value of the project lies not only in OctoBeat itself, but in establishing SongMap as a reusable and implementation-independent standard for temporal music synchronization.
