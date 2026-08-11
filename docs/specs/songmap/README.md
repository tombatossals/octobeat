# SongMap

> **An open specification for describing the temporal structure of an audio recording.**

SongMap is an open, deterministic and versioned specification that defines how temporal musical information is represented and exchanged.

It is the common contract shared by every component of the OctoBeat ecosystem and any third-party application that chooses to implement the specification.

---

# Current Status

| Property            | Value        |
| ------------------- | ------------ |
| **Current Version** | `songmap/v1` |
| **Status**          | Draft        |

The current schema supports:

* beats and bars (with downbeat detection);
* global tempo, offset and time signature;
* a tempo map (constant, discrete changes, accelerando/ritardando);
* overall and per-metric confidence.

---

# Repository Structure

```text
songmap/

├── README.md
├── SPEC.md
├── GLOSSARY.md
├── CHANGELOG.md
├── songmap.schema.json
└── examples/
```

---

# Documents

## SPEC.md

The normative specification of SongMap.

It defines:

* the philosophy of the format;
* the conceptual model;
* the JSON structure;
* compatibility rules;
* future evolution.

Every implementation should follow this document.

---

## GLOSSARY.md

Definitions of the concepts used by the specification.

---

## CHANGELOG.md

A chronological record of changes to the specification.

---

## songmap.schema.json

Machine-readable JSON Schema.

Every valid SongMap document should validate against this schema.

---

## examples/

Reference SongMap documents used for testing, validation and documentation.

---

# Design Principles

SongMap follows a small set of core principles.

* A SongMap describes **one specific audio recording**.
* A SongMap contains only **objective temporal information**.
* A SongMap is **deterministic**.
* A SongMap is **application independent**.
* A SongMap is **instrument agnostic**.
* A SongMap is **versioned and extensible**.
* A SongMap never contains exercises, sessions or user data.

---

# Ecosystem

SongMap acts as the common language between all tools.

```text
                BeatEngine
                     │
                     ▼

              SongMap (.json)

        ┌────────────┼────────────┐
        ▼            ▼            ▼

   OctoBeat   SongMap Editor   Viewer
```

Applications communicate by exchanging SongMaps, never internal data structures.

---

# Versioning

The current specification is identified as:

```text
songmap/v1
```

Compatible extensions should be introduced by adding optional blocks.

Breaking changes require a new schema version.

---

# Related Documentation

```text
docs/prd/PRD.md
docs/adr/ADR-0001-songmap-as-contract.md
```

---

# Guiding Principle

> **A SongMap is a deterministic temporal description of a specific audio recording.**
