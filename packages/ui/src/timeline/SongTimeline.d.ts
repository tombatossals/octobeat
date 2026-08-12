import type { SongMap } from "@octobeat/songmap";
interface SongTimelineProps {
    /**
     * The loaded SongMap.
     */
    songmap: SongMap;
    /**
     * Class name for the outer container.
     */
    className?: string;
}
export declare function SongTimeline({ songmap, className, }: SongTimelineProps): React.JSX.Element;
export {};
