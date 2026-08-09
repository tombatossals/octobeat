# ADR-0006 — BeatEngine as an Independent CLI

**Status:** Accepted
**Date:** 2026-08-02

---

# Context

BeatEngine is responsible for generating SongMaps from audio recordings.

During the initial design phase, several implementation approaches were considered:

* an internal library used directly by OctoBeat;
* a REST service;
* an independent command-line application (CLI).

The project aims to keep BeatEngine independent from any specific application while making it easy to integrate into development workflows, automation pipelines and third-party tools.

---

# Decision

BeatEngine will initially be implemented as an **independent command-line application (CLI)**.

Its responsibility is limited to reading an audio source, analyzing it and producing a valid SongMap.

BeatEngine does not know how SongMaps will be consumed.

It has no dependency on OctoBeat or any other application.

---

# Responsibilities

BeatEngine is responsible for:

* loading supported recording sources;
* analyzing temporal musical information;
* generating SongMaps;
* validating generated SongMaps;
* exposing analysis through a command-line interface.

BeatEngine is **not** responsible for:

* playback;
* visualization;
* synchronization overlays;
* user interfaces;
* practice sessions;
* educational content.

---

# Consequences

## Positive

### Application Independence

BeatEngine can be used by any application capable of reading SongMaps.

Examples include:

* OctoBeat;
* SongMap Editor;
* batch processing tools;
* CI pipelines;
* third-party applications.

---

### Automation

The CLI integrates naturally with automation workflows.

Examples include:

```bash
octobeat analyse get-lucky.mp3

octobeat validate get-lucky.songmap.json

octobeat info get-lucky.songmap.json
```

This makes BeatEngine suitable for scripting and continuous integration.

---

### Testability

The command-line interface provides a stable contract for automated testing.

Given the same input recording, BeatEngine should always produce the same SongMap.

---

### Future Integrations

Other applications may invoke BeatEngine without linking directly to its implementation.

Future wrappers may include:

* desktop applications;
* web services;
* graphical frontends;
* editor integrations.

---

# Negative Consequences

Applications that require direct in-process access to analysis results must invoke the CLI or rely on future integration layers.

The command-line interface may introduce a small amount of overhead compared to a native library.

---

# Alternatives Considered

## Internal Library

BeatEngine could have been implemented as a library imported directly by OctoBeat.

This option was rejected because it tightly couples the analysis engine to a specific application and makes reuse more difficult.

---

## REST API

BeatEngine could expose its functionality through an HTTP service.

This option was rejected because it introduces deployment complexity and network dependencies during the proof-of-concept phase.

A service layer can always be added later if required.

---

## Embedded Analysis

OctoBeat could perform audio analysis internally.

This option was rejected because it violates the architectural principle that applications consume SongMaps rather than generating them.

---

# Architectural Principles Established

This decision establishes the following principles:

* BeatEngine is an independent component.
* SongMap is the only output contract.
* Applications consume SongMaps rather than analysis algorithms.
* The command-line interface is the primary public interface of BeatEngine.
* Additional interfaces may be added without changing the core engine.

---

# Future Evolution

Although the CLI is the primary interface, the analysis engine should remain independent from it.

Future interfaces may include:

* a reusable library;
* a REST API;
* a desktop application;
* cloud-based analysis services.

These interfaces should reuse the same analysis engine rather than implementing independent analysis pipelines.

The CLI remains the reference implementation.

---

# Scope

This decision applies to BeatEngine and every component that interacts with it.

It does not prevent future interfaces, provided they preserve the same architectural boundaries.

---

# Related Documents

* `docs/prd/PRD.md`
* `docs/specs/songmap/SPEC.md`
* `docs/adr/ADR-0001-songmap-as-contract.md`
* `docs/adr/ADR-0002-monorepo-during-the-early-development-phase.md`

---

# Notes

Choosing a CLI is an architectural decision rather than an implementation detail.

The command-line interface provides a simple, portable and language-independent way of exposing BeatEngine while keeping the analysis engine isolated from the applications that consume its output.

This separation ensures that BeatEngine remains reusable, testable and suitable for future integrations without compromising the independence of the SongMap specification.
