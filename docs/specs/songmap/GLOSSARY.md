# Glossary

# Bar

A group of beats defined by the time signature.

The first beat of a bar is its downbeat. In `songmap/v1` each bar
references the index of its first beat rather than listing its beats.

# Beat

A regular pulse occurring at a specific instant in time.

Beat indices are absolute and continuous: they keep counting even when
the tempo changes.

# Confidence

A value in `[0, 1]` describing the reliability of an analysis.

The overall confidence combines independent metrics: tempo confidence,
beat confidence and grid stability.

# Downbeat

The first beat of a bar.

Downbeats are detected from the onset evidence rather than assumed to
be beat 1, so recordings that begin on a pickup are represented
correctly.

# Grid

The set of beats arranged in time, built from the detected tempo,
phase and tempo map. The grid governs the SongMap even when individual
onsets are noisy.

# Offset

The time (in seconds) at which the actual music begins, used to skip
intros and count-ins.

# Phase

The temporal position of the beat grid relative to the start of the
recording.

# Recording

A specific audio performance.

# Song

The abstract musical work.

# SongMap

A deterministic temporal description of a specific audio recording.

# Tempo map

A list of segments describing how the tempo changes over time.

Between consecutive segments the tempo is interpolated linearly,
supporting constant tempo, discrete changes and gradual ramps
(accelerando and ritardando).

# Time signature

The rhythmic structure of the recording (for example `4/4`), expressed
as beats per bar.

# Timeline

Ordered sequence of temporal events.
