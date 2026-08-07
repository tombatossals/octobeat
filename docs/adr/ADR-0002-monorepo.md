# ADR-0002 — Monorepo During the Early Development Phase

**Status:** Accepted
**Date:** 2026-08-02

---

# Context

The VideoStick ecosystem is composed of several independent components with distinct responsibilities.

Examples include:

* SongMap Specification
* BeatEngine
* SongMap Editor
* VideoStick
* Music Catalog

From an architectural perspective, each component could exist as an independent repository.

However, during the proof-of-concept phase, all components are expected to evolve rapidly and simultaneously.

Maintaining multiple repositories at this stage would introduce unnecessary operational overhead.

---

# Decision

The project will initially be developed as a **single monorepository**.

Each component will live in its own directory with clear ownership and well-defined boundaries, but all components will share the same repository.

The repository structure should reflect the logical architecture of the ecosystem rather than the deployment model.

---

# Consequences

## Positive

### Simplicity

A single repository simplifies project setup, version control and contributor onboarding.

---

### Atomic Changes

Cross-cutting changes affecting multiple components can be committed together.

Examples include:

* evolving the SongMap specification;
* updating BeatEngine;
* adapting VideoStick.

---

### Shared Tooling

The project can share:

* documentation;
* continuous integration;
* formatting rules;
* linting;
* testing infrastructure.

---

### Faster Iteration

The proof-of-concept phase prioritizes experimentation over repository independence.

Developers can modify the specification and its implementations within the same change set.

---

# Negative Consequences

Repository boundaries are less explicit.

Some components may appear more tightly coupled than they actually are.

Extra discipline is required to preserve architectural separation.

---

# Alternatives Considered

## Independent Repositories

Each component could be hosted in its own repository.

This option was rejected because it introduces unnecessary complexity during the early stages of the project.

Examples include:

* coordinating multiple releases;
* synchronizing documentation;
* managing several CI pipelines;
* maintaining cross-repository changes.

These costs outweigh the benefits while the architecture is still evolving.

---

## Single Application Repository

Another option would be to develop VideoStick as a single application without separating internal components.

This option was rejected because the ecosystem is intentionally designed around independent responsibilities.

Even inside a monorepository, architectural boundaries should remain explicit.

---

# Architectural Principles Established

This decision establishes the following principles:

* Physical repository structure does not define architectural boundaries.
* Components remain logically independent even when stored in the same repository.
* SongMap continues to be the only shared contract between components.
* Every component should be designed so that it could be extracted into its own repository with minimal effort.

---

# Future Evolution

The monorepository is considered an implementation strategy, not an architectural requirement.

If any component reaches sufficient maturity or requires an independent release cycle, it may be extracted into its own repository.

Potential candidates include:

* songmap-spec
* beatengine
* music-catalog

Such a migration should not require architectural changes, only repository restructuring.

---

# Scope

This decision applies to the entire VideoStick ecosystem during the proof-of-concept and early development phases.

---

# Related Documents

* `docs/prd/PRD.md`
* `docs/specs/songmap/SPEC.md`
* `docs/adr/ADR-0001-songmap-as-contract.md`

---

# Notes

Choosing a monorepository is a practical decision intended to maximize development speed and reduce operational complexity.

It does **not** change the architectural model of the project.

The logical separation between components remains the primary design principle and should be preserved regardless of the repository layout.
