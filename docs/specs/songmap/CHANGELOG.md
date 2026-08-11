# Changelog

All notable changes to the SongMap specification are documented in
this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Changed

- `timing` may now include an optional `tempoMap` describing tempo
  changes, including discrete changes and gradual ramps
  (accelerando/ritardando). The tempo is interpolated linearly between
  consecutive segments.
- `bars` are now aligned to detected downbeats instead of assuming
  beat 1 is always the first beat of a bar.

### Added

- Confidence is documented as a combination of tempo confidence, beat
  confidence and grid stability.
- Optional `sections` block describing the musical form (intro, verse,
  chorus, bridge, solo, outro, ...). Sections reference beats
  preferentially (`startBeat`) and keep `startTime` for convenience;
  `sourceName` preserves the original chart label. This is an additive
  change to `songmap/v1` (see the versioning rules: optional blocks may
  be added without a new schema).
- Optional `timing.source` field recording where the timing came from
  (`sng`, `midi`, `chart`, `audio-analysis`, `manual`).

## [1.0] — 2026-08-02

Initial draft of the `songmap/v1` specification.

- Core collections: `beats` and `bars`.
- Global `timing` block: tempo, offset, time signature and confidence.
- Recording metadata: title, duration and source.
- Versioning and compatibility rules.
