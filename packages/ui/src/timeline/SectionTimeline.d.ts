import type { SongSections } from "./model";
interface SectionTimelineProps {
    /**
     * Resolved sections (see resolveSections).
     */
    sections: SongSections;
    /**
     * Current playback position (seconds).
     */
    currentTime?: number;
    /**
     * Called with the section start time when a section is clicked.
     */
    onSeek?: (time: number) => void;
    /**
     * Class name for the outer container.
     */
    className?: string;
}
export declare function SectionTimeline({ sections, currentTime, onSeek, className, }: SectionTimelineProps): React.JSX.Element;
export {};
