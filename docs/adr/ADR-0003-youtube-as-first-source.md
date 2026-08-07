# ADR-0003 — YouTube as the Initial Recording Source

**Status:** Accepted
**Date:** 2026-08-02

---

# Context

VideoStick aims to synchronize educational content with real music.

To achieve this, users need access to complete recordings that can be analyzed by BeatEngine and played back by VideoStick.

Several potential sources were considered, including:

* local audio files;
* YouTube;
* Spotify;
* Apple Music;
* other streaming services.

During the proof-of-concept phase, the primary objective is to validate synchronization rather than support every possible audio source.

---

# Decision

YouTube is selected as the initial recording source for the proof of concept.

The ecosystem will initially assume that recordings originate from YouTube.

BeatEngine will be capable of analyzing YouTube recordings, and VideoStick will synchronize its overlay with the YouTube player.

This decision is limited to the early stages of the project and does not define the long-term architecture.

---

# Consequences

## Positive

### Accessibility

Most users already have access to YouTube without requiring additional subscriptions.

---

### Large Music Catalog

YouTube provides access to an extensive catalogue of official music videos, live performances, remasters and alternative versions.

---

### Simple User Experience

Users only need to provide a YouTube URL to analyze a recording or create a SongMap.

---

### Fast Prototyping

The proof of concept can focus entirely on synchronization instead of dealing with multiple playback providers.

---

# Negative Consequences

The project becomes partially dependent on YouTube during the proof-of-concept phase.

The YouTube player also introduces technical limitations compared to local playback, such as restrictions imposed by the IFrame API.

---

# Alternatives Considered

## Local Audio Files

Supporting local MP3, WAV or FLAC files from the beginning would provide greater flexibility.

This option was rejected because it introduces unnecessary complexity during the validation phase.

Support for local files remains an important future capability.

---

## Spotify

Spotify offers a rich music catalogue and metadata.

This option was rejected because playback restrictions and licensing limitations make it less suitable for an initial proof of concept.

Spotify may become a metadata source or playback provider in future versions.

---

## Multiple Sources from Day One

Supporting several providers simultaneously would make the architecture more complete.

This option was rejected because it increases implementation complexity without contributing to the primary objective of validating synchronization.

---

# Architectural Principles Established

This decision establishes the following principles:

* SongMap remains independent of the recording source.
* BeatEngine should be designed to support additional sources in the future.
* VideoStick should synchronize using SongMaps rather than provider-specific information.
* Playback providers are implementation details, not architectural concepts.

---

# Future Evolution

The ecosystem should eventually support multiple recording sources.

Potential sources include:

* local audio files;
* YouTube;
* Spotify;
* Apple Music;
* cloud storage;
* user-managed music libraries.

Regardless of the source, every recording should produce the same SongMap representation.

---

# Scope

This decision applies only to the proof-of-concept and early development phases.

It should not be interpreted as a permanent limitation of the ecosystem.

---

# Related Documents

* `docs/prd/PRD.md`
* `docs/specs/songmap/SPEC.md`
* `docs/adr/ADR-0001-songmap-as-contract.md`

---

# Notes

The project is built around SongMap rather than any specific playback provider.

YouTube is simply the most practical source for validating the core concept of synchronized practice.

Future versions of the ecosystem should support additional sources without requiring changes to the SongMap specification or the overall architecture.
