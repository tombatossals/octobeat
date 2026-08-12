import type { SectionView } from "./model";
export interface SectionRange {
    /**
     * Section being practised.
     */
    section: SectionView | null;
    /**
     * Absolute start time (seconds).
     */
    startTime: number;
    /**
     * Absolute end time (seconds).
     */
    endTime: number;
    /**
     * Duration of the practice window (seconds).
     */
    duration: number;
}
export interface SectionPracticeState {
    /**
     * The currently selected section, or null for the whole song.
     */
    section: SectionView | null;
    /**
     * Select a section to practise (null restores whole-song mode).
     */
    select(section: SectionView | null): void;
    /**
     * The practice range for the selected section.
     */
    range: SectionRange | null;
    /**
     * True when practising a single section.
     */
    active: boolean;
}
/**
 * Section-scoped practice seam.
 *
 * Prepares the structure for "practice only this section": selects a
 * section and exposes its time range, which the player can confine
 * playback to and the Exercise Engine can limit exercises to.
 *
 * The actual loop/confined playback is not implemented here; consumers
 * use ``range`` to constrain playback and exercises.
 */
export declare function useSectionPractice(sections: readonly SectionView[]): SectionPracticeState;
