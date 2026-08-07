# ADR-0005 — Separate Music Catalog from SongMap

**Status:** Accepted
**Date:** 2026-08-02

---

# Context

SongMap is designed to describe the temporal structure of a specific audio recording.

During the early design of the project, the question arose whether SongMap should also include musical metadata such as:

* artist;
* album;
* genre;
* release year;
* difficulty;
* practice tags.

Including this information directly inside SongMap would simplify some use cases, but it would also mix two fundamentally different concerns.

One describes **objective temporal information**.

The other describes **catalogue metadata**.

---

# Decision

SongMap will contain only the information required to describe the temporal structure of a recording.

All descriptive metadata will be stored in a separate component named **Music Catalog**.

SongMap may reference a recording source, but it will never become a music database.

---

# Consequences

## Positive

### Clear Separation of Responsibilities

SongMap focuses exclusively on temporal information.

The Music Catalog focuses exclusively on descriptive metadata.

Each component has a single responsibility.

---

### Reusability

The same SongMap can be reused by multiple catalogs.

Likewise, a catalog can reference multiple SongMaps representing different recordings of the same musical work.

Examples include:

* album version;
* live version;
* acoustic version;
* remastered edition.

---

### Independent Evolution

SongMap and the Music Catalog can evolve independently.

Changes to catalog metadata do not require modifications to the SongMap specification.

Likewise, new SongMap capabilities do not affect the catalog model.

---

### Reduced Duplication

Metadata such as artist or genre only needs to exist once.

It is not duplicated across every SongMap document.

---

# Negative Consequences

Applications that require both temporal information and descriptive metadata must combine data from two independent sources.

This introduces a small amount of additional implementation complexity.

---

# Alternatives Considered

## Store Everything in SongMap

One option was to include all musical metadata directly inside SongMap.

This approach was rejected because it mixes objective temporal data with descriptive information and gradually turns SongMap into a music database.

---

## Duplicate Metadata

Another option was to duplicate catalog metadata inside every SongMap.

This approach was rejected because duplicated information inevitably becomes inconsistent over time.

---

## External Metadata Only

Another possibility would be for SongMap to contain no recording information whatsoever.

This option was rejected because a minimal recording identifier is useful for traceability and reproducibility.

Basic recording information such as title, duration and source remains part of SongMap.

---

# Architectural Principles Established

This decision establishes the following principles:

* SongMap describes **when** musical events occur.
* Music Catalog describes **what** the recording is.
* SongMap never becomes a music catalogue.
* Catalog metadata must never influence temporal analysis.
* Both components evolve independently.

---

# Future Evolution

The Music Catalog may eventually contain information such as:

* artists;
* albums;
* genres;
* release dates;
* musical styles;
* practice difficulty;
* educational tags;
* YouTube links;
* streaming providers;
* playlists.

SongMap should remain unchanged regardless of how much the catalog grows.

---

# Scope

This decision applies to the entire VideoStick ecosystem.

All current and future components should obtain descriptive metadata from the Music Catalog and temporal information from SongMap.

---

# Related Documents

* `docs/specs/songmap/SPEC.md`
* `docs/prd/PRD.md`
* `docs/adr/ADR-0001-songmap-as-contract.md`

---

# Notes

This ADR reinforces one of the core architectural principles of the project:

**SongMap is not a music database.**

Its purpose is to provide a deterministic and implementation-independent description of the temporal structure of a recording.

The Music Catalog complements SongMap by providing descriptive information without compromising the simplicity, stability and long-term evolution of the SongMap specification.
