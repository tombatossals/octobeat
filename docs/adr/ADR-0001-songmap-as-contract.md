# ADR-0001 — SongMap as the Ecosystem Contract

**Status:** Accepted
**Date:** 2026-08-02

---

# Context

OctoBeat was originally conceived as an application for practicing musical technique using real songs.

During the initial design phase, it became clear that the true value of the project is not the application itself, but the ability to represent the temporal structure of an audio recording in an objective and reusable way.

Multiple tools within the ecosystem need to exchange this information:

* BeatEngine analyzes an audio recording.
* SongMap Editor allows manual corrections.
* OctoBeat synchronizes practice exercises.
* A viewer can visualize the musical timeline.
* Future AI-based tools may generate or enrich the analysis.

If each tool defines its own internal format, the ecosystem becomes tightly coupled, making interoperability and long-term evolution significantly more difficult.

---

# Decision

SongMap is defined as the **single exchange contract** for every tool in the ecosystem.

No component should share internal data structures or depend on another component's implementation.

All communication between tools must take place through SongMap documents that conform to the official SongMap specification.

---

# Consequences

## Positive

### Decoupling

Each component can evolve independently.

For example, BeatEngine may completely change its analysis algorithms without requiring any changes to OctoBeat.

---

### Interoperability

Third-party applications can generate or consume SongMaps by implementing the public specification alone.

No dependency on the original implementation is required.

---

### Reusability

The same SongMap can be reused by multiple applications simultaneously.

Examples include:

* OctoBeat
* SongMap Editor
* SongMap Viewer
* Analysis tools
* AI systems

---

### Testability

Each component can be developed and tested independently using SongMap documents as input and output.

---

### Evolvability

New tools can be introduced without modifying existing ones.

As long as they conform to the SongMap specification, they become immediately compatible with the ecosystem.

---

# Negative Consequences

SongMap becomes a critical dependency for the entire ecosystem.

Breaking changes must be managed carefully through versioning and migration guides.

The specification requires greater design discipline than an internal application-specific format.

---

# Alternatives Considered

## Shared Internal Models

Each component could directly share internal data structures implemented in code.

This approach was rejected because it creates strong coupling between projects and makes independent evolution difficult.

---

## Shared API

BeatEngine could expose an API consumed directly by the remaining tools.

This approach was rejected because it introduces a single point of dependency, complicates offline workflows and makes manual editing significantly harder.

---

## Tool-Specific Formats

Each application could define its own exchange format.

This approach was rejected because it requires multiple conversion layers and greatly reduces interoperability.

---

# Architectural Principles Established

This decision establishes the following architectural principles:

* SongMap is the single shared contract of the ecosystem.
* Tools exchange SongMaps, never internal data structures.
* SongMap is independent of any specific application.
* The SongMap specification evolves independently from the applications that consume it.
* Applications depend on SongMap; SongMap depends on no application.

---

# Scope

This decision applies to the entire OctoBeat ecosystem, including both current and future components.

Examples include:

* BeatEngine
* SongMap Editor
* OctoBeat
* SongMap Viewer
* Music Catalog
* Future analysis and AI-based tools

---

# Related Documents

* `docs/specs/songmap/SPEC.md`
* `docs/prd/PRD.md`

---

# Notes

This ADR defines the fundamental architectural decision of the project.

OctoBeat is considered a consumer of SongMap rather than its owner.

SongMap is not an internal format used by OctoBeat; it is an independent specification intended to support an entire ecosystem of interoperable tools.
