# Product Requirements Document (PRD)

**Project:** VideoStick
**Version:** 1.0 (Draft)
**Status:** Draft

---

# 1. Vision

VideoStick is an application for practicing musical technique using real music.

Rather than practicing with a metronome alone, musicians practice technical exercises while remaining synchronized with the temporal structure of real recordings.

VideoStick is the first application built on top of the SongMap specification.

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

VideoStick aims to bridge that gap.

---

# 3. Product Vision

The project consists of two complementary ideas.

## SongMap

SongMap is an open specification describing the temporal structure of an audio recording.

It is independent of VideoStick and acts as the common contract between all tools.

## VideoStick

VideoStick consumes SongMaps to synchronize educational content with music.

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

## VideoStick

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

## Phase 1

Define the SongMap specification.

---

## Phase 2

Develop BeatEngine.

---

## Phase 3

Build a SongMap Viewer.

---

## Phase 4

Develop the synchronized overlay.

---

## Phase 5

Implement exercises and practice sessions.

---

## Phase 6

Build the Music Catalog.

---

## Phase 7

Develop the SongMap Editor.

---

## Phase 8

Add advanced music analysis.

Examples:

* sections;
* tempo changes;
* harmonic analysis;
* musical descriptors.

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

VideoStick is not the final product.

It is the first application built on top of SongMap.

The long-term objective is to create an ecosystem of interoperable tools capable of sharing temporal musical information through an open specification.

Potential ecosystem components include:

* BeatEngine
* VideoStick
* SongMap Editor
* Music Catalog
* SongMap Viewer
* AI-assisted analysis tools
* DAW integrations
* Educational applications

The long-term value of the project lies not only in VideoStick itself, but in establishing SongMap as a reusable and implementation-independent standard for temporal music synchronization.
