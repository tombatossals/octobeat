"use client";

import { useState } from "react";

import { clsx } from "clsx";

import type {
    SectionView,
    SongSections,
} from "./model";

import {
    formatTime,
    sectionAtTime,
    songProgress,
} from "./model";

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

export function SectionTimeline({
    sections,
    currentTime = 0,
    onSeek,
    className,
}: SectionTimelineProps): React.JSX.Element {
    const [hovered, setHovered] = useState<SectionView | null>(null);

    const active = sectionAtTime(
        sections.sections,
        currentTime,
    );

    const progress = songProgress(
        sections.duration,
        currentTime,
    );

    const total = sections.sections.reduce(
        (sum, section) => sum + section.duration,
        0,
    );

    return (
        <div
            className={clsx(
                "relative flex h-10 w-full flex-col justify-center",
                className,
            )}
            onMouseLeave={() => setHovered(null)}
        >
            <div className="relative flex h-6 w-full gap-px overflow-hidden rounded-md">
                {sections.sections.map((section) => {
                    const width =
                        total > 0
                            ? (section.duration / total) * 100
                            : 0;

                    const isActive =
                        active?.index === section.index;

                    return (
                        <button
                            key={section.index}
                            type="button"
                            aria-label={`${section.name} (${formatTime(section.startTime)})`}
                            title={`${section.name} ${formatTime(section.startTime)} – ${formatTime(section.endTime)}`}
                            onClick={() =>
                                onSeek?.(section.startTime)
                            }
                            onMouseEnter={() =>
                                setHovered(section)
                            }
                            onFocus={() => setHovered(section)}
                            onBlur={() => setHovered(null)}
                            className={clsx(
                                "relative h-full cursor-pointer transition-colors",
                                "focus:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                                isActive
                                    ? "bg-primary"
                                    : "bg-primary/40 hover:bg-primary/60",
                            )}
                            style={{ width: `${width}%` }}
                        >
                            <span className="absolute inset-0 flex items-center justify-center overflow-hidden px-1 text-[10px] font-medium text-primary-foreground">
                                {section.name}
                            </span>
                        </button>
                    );
                })}

                {sections.sections.length === 0 && (
                    <div className="flex h-full w-full items-center justify-center bg-muted text-xs text-muted-foreground">
                        No sections
                    </div>
                )}
            </div>

            {active && (
                <div
                    className="pointer-events-none absolute inset-y-2 w-px bg-background"
                    style={{
                        left: `${progress * 100}%`,
                    }}
                    aria-hidden="true"
                />
            )}

            {hovered && (
                <div className="pointer-events-none absolute bottom-8 z-10 rounded-md border bg-popover px-2 py-1 text-xs shadow-md">
                    <div className="font-semibold">
                        {hovered.name}
                    </div>
                    <div className="text-muted-foreground">
                        {formatTime(hovered.startTime)} –{" "}
                        {formatTime(hovered.endTime)}
                    </div>
                    <div className="text-muted-foreground">
                        {hovered.beats} beats
                    </div>
                </div>
            )}
        </div>
    );
}
