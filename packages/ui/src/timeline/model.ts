"use client";

import type { Section } from "@octobeat/songmap";

/**
 * A section prepared for rendering: its duration and beat span are
 * resolved from the song duration and the next section boundary.
 */
export interface SectionView {
    index: number;

    name: string;

    sourceName: string | null;

    startBeat: number;

    startTime: number;

    endTime: number;

    duration: number;

    beats: number;
}

export interface SongSections {
    sections: SectionView[];

    duration: number;
}

/**
 * Resolve sections against the total song duration, computing each
 * section's end time (the next section's start, or the song end) and
 * its beat span.
 */
export function resolveSections(
    sections: readonly Section[] | undefined,
    duration: number,
    totalBeats: number,
): SongSections {
    if (!sections || sections.length === 0) {
        return { sections: [], duration };
    }

    const sorted = [...sections].sort(
        (a, b) => a.startTime - b.startTime,
    );

    const resolved: SectionView[] = sorted.map(
        (section, i) => {
            const next = sorted[i + 1];
            const endTime = next
                ? next.startTime
                : duration;

            const nextBeat = next
                ? next.startBeat
                : totalBeats + 1;

            return {
                index: section.index,
                name: section.name,
                sourceName: section.sourceName ?? null,
                startBeat: section.startBeat,
                startTime: section.startTime,
                endTime,
                duration: Math.max(
                    0,
                    endTime - section.startTime,
                ),
                beats: Math.max(
                    0,
                    nextBeat - section.startBeat,
                ),
            };
        },
    );

    return {
        sections: resolved,
        duration,
    };
}

/**
 * Active section at a given time, or null when no section covers it.
 */
export function sectionAtTime(
    sections: readonly SectionView[],
    time: number,
): SectionView | null {
    if (sections.length === 0) {
        return null;
    }

    if (time < sections[0]!.startTime) {
        return null;
    }

    let active: SectionView | null = null;

    for (const section of sections) {
        if (time < section.startTime) {
            break;
        }

        active = section;
    }

    if (
        active
        && time >= active.endTime
        && active !== sections[sections.length - 1]
    ) {
        return active;
    }

    return active;
}

/**
 * Fraction (0..1) of the song elapsed at ``time``.
 */
export function songProgress(
    duration: number,
    time: number,
): number {
    if (duration <= 0) {
        return 0;
    }

    return Math.max(
        0,
        Math.min(1, time / duration),
    );
}

/**
 * Fraction (0..1) of the section elapsed at ``time``.
 */
export function sectionProgress(
    section: SectionView,
    time: number,
): number {
    if (section.duration <= 0) {
        return 0;
    }

    return Math.max(
        0,
        Math.min(
            1,
            (time - section.startTime) / section.duration,
        ),
    );
}

export function formatTime(seconds: number): string {
    if (!Number.isFinite(seconds) || seconds < 0) {
        return "00:00";
    }

    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);

    return `${minutes.toString().padStart(2, "0")}:${secs
        .toString()
        .padStart(2, "0")}`;
}
