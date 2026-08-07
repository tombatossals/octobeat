# ADR-0004 — "Get Lucky" as the Reference Recording

**Status:** Accepted
**Date:** 2026-08-02

---

# Context

The primary objective of the proof of concept is to validate the synchronization capabilities of the VideoStick ecosystem.

At this stage, the project is not attempting to evaluate BeatEngine against arbitrary recordings or to support every musical style.

Instead, the goal is to verify that a SongMap can drive a synchronized educational overlay throughout an entire recording.

Choosing an appropriate reference recording is therefore an engineering decision rather than a musical one.

---

# Decision

**"Get Lucky" by Daft Punk** is selected as the reference recording for the proof of concept.

All initial development, testing and demonstrations should use this recording whenever possible.

The reference recording serves as the baseline against which synchronization quality and application behaviour are evaluated.

---

# Rationale

The recording was selected because it exhibits several characteristics that simplify validation.

### Stable Tempo

The recording maintains a highly consistent tempo throughout its duration.

This minimizes synchronization drift and allows the project to focus on validating the architecture rather than compensating for tempo variations.

---

### Simple Time Signature

The recording uses a standard 4/4 time signature, making it suitable for the first implementation of SongMap and BeatEngine.

---

### Predictable Groove

The rhythmic structure remains consistent for most of the recording.

This makes synchronization errors immediately noticeable.

---

### Suitable for Practice

Its moderate tempo makes it appropriate for practicing Stick Control and other basic technical exercises.

---

### Well Known

The recording is widely recognized, making demonstrations easier to understand and evaluate.

---

# Consequences

## Positive

### Consistent Testing

Every component of the ecosystem can be validated against the same reference recording.

Examples include:

* BeatEngine
* SongMap validation
* SongMap Viewer
* VideoStick
* Overlay synchronization

---

### Reproducibility

Developers working on different components can reproduce identical results using the same recording.

---

### Reduced Variables

By using a recording with a stable tempo, synchronization issues are easier to diagnose.

Problems are more likely to originate in the implementation rather than in the recording itself.

---

# Negative Consequences

The proof of concept is initially validated against a single recording.

This does not guarantee correct behaviour with recordings that contain:

* tempo fluctuations;
* unusual time signatures;
* live performances;
* expressive timing.

Additional recordings will be required before considering the architecture production-ready.

---

# Alternatives Considered

## "Say It Ain't So" — Weezer

Originally considered during the early design phase.

This option was rejected because natural tempo fluctuations make it less suitable for validating the synchronization engine.

It remains a valuable future test case once the proof of concept has been completed.

---

## Multiple Reference Recordings

Using several recordings from the beginning would increase test coverage.

This option was rejected because it introduces additional variables before the core synchronization model has been validated.

---

## Synthetic Metronome Tracks

Artificial recordings with a perfectly constant tempo would simplify synchronization.

This option was rejected because the objective of the project is to synchronize with real commercial recordings rather than synthetic examples.

---

# Architectural Principles Established

This decision establishes the following principles:

* Reference recordings are engineering tools.
* The proof of concept should minimize unnecessary variables.
* Validation should begin with predictable recordings before expanding to more complex material.
* The reference recording does not influence the SongMap specification.

---

# Future Evolution

Once the proof of concept has been validated, the ecosystem should progressively incorporate recordings with increasing complexity.

Examples include:

* recordings with expressive tempo changes;
* live performances;
* different musical genres;
* uncommon time signatures;
* recordings with multiple tempo sections.

The reference recording should remain available as a regression test throughout the lifetime of the project.

---

# Scope

This decision applies only to the proof-of-concept and early development phases.

Future versions of the project should maintain a growing library of reference recordings covering a broad range of musical characteristics.

---

# Related Documents

* `docs/prd/PRD.md`
* `docs/specs/songmap/SPEC.md`
* `docs/adr/ADR-0001-songmap-as-contract.md`
* `docs/adr/ADR-0003-youtube-as-first-source.md`

---

# Notes

The reference recording is selected for its technical characteristics rather than personal preference.

Its purpose is to provide a stable and reproducible baseline for validating synchronization across the entire VideoStick ecosystem.

As the project evolves, additional reference recordings should be incorporated to increase coverage while preserving **"Get Lucky"** as the canonical regression test.
