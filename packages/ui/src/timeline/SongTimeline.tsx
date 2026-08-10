"use client";

import type { SongMap } from "@octobeat/songmap";
import { usePlayerStore } from "@octobeat/player";

import type { SectionView, SongSections } from "./model";

import {
    formatTime,
    resolveSections,
    sectionAtTime,
    sectionProgress,
    songProgress,
} from "./model";

import { SectionTimeline } from "./SectionTimeline";

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

export function SongTimeline({
    songmap,
    className,
}: SongTimelineProps): React.JSX.Element {
    const player = usePlayerStore((state) => state.player);
    const currentTime = usePlayerStore((state) => state.currentTime);

    const duration = songmap.metadata.duration;

    const sections: SongSections = resolveSections(
        songmap.sections,
        duration,
        songmap.beats.length,
    );

    const active = sectionAtTime(
        sections.sections,
        currentTime,
    );

    function handleSeek(time: number): void {
        player?.seek(time);
    }

    return (
        <div className="flex w-full flex-col gap-1">
            <SectionTimeline
                sections={sections}
                currentTime={currentTime}
                onSeek={handleSeek}
                className={className}
            />

            <SongProgressFooter
                currentTime={currentTime}
                duration={duration}
                active={active}
            />
        </div>
    );
}

function SongProgressFooter({
    currentTime,
    duration,
    active,
}: {
    currentTime: number;

    duration: number;

    active: SectionView | null;
}): React.JSX.Element {
    const song = songProgress(duration, currentTime);
    const section = active
        ? sectionProgress(active, currentTime)
        : 0;

    return (
        <div className="flex items-center justify-between text-xs text-muted-foreground tabular-nums">
            <span>
                {active ? (
                    <span className="font-medium text-foreground">
                        {active.name}
                    </span>
                ) : (
                    "—"
                )}
            </span>

            <span>
                {formatTime(currentTime)} / {formatTime(duration)}
            </span>

            <span>
                song {Math.round(song * 100)}% · section{" "}
                {Math.round(section * 100)}%
            </span>
        </div>
    );
}
