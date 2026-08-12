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
export declare function resolveSections(sections: readonly Section[] | undefined, duration: number, totalBeats: number): SongSections;
/**
 * Active section at a given time, or null when no section covers it.
 */
export declare function sectionAtTime(sections: readonly SectionView[], time: number): SectionView | null;
/**
 * Fraction (0..1) of the song elapsed at ``time``.
 */
export declare function songProgress(duration: number, time: number): number;
/**
 * Fraction (0..1) of the section elapsed at ``time``.
 */
export declare function sectionProgress(section: SectionView, time: number): number;
export declare function formatTime(seconds: number): string;
