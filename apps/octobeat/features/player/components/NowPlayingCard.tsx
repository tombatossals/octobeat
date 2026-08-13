"use client";

import { useLibraryStore } from "@/features/library/store";

export function NowPlayingCard() {
    const dataset = useLibraryStore(
        (state) => state.dataset,
    );

    if (!dataset) {
        return null;
    }

    const { metadata } = dataset;

    const difficulty =
        metadata.difficulty;

    return (
        <div
            key={metadata.id}
            className="pointer-events-none fixed right-24 top-20 z-40 flex animate-[cardLife_5s_ease-in-out_forwards] items-start gap-3 rounded-2xl border border-border bg-background/70 py-1 pl-1 pr-4 text-foreground shadow-2xl backdrop-blur-md short:right-auto short:left-3 short:top-44 short:gap-2 short:rounded-lg short:py-0.5 short:pl-0.5 short:pr-2.5"
        >
            <img
                src={`/resources/${metadata.id}/cover.jpg`}
                alt={`${metadata.title} cover`}
                className="h-32 w-32 rounded-xl object-cover shadow-lg short:h-16 short:w-16 short:rounded-md"
            />

            <div className="mt-1 min-w-0 short:mt-0.5">
                <div className="text-3xl font-bold leading-tight short:text-lg">
                    {metadata.title}
                </div>

                <div className="truncate text-lg text-muted-foreground short:text-xs">
                    {metadata.artist}
                </div>

                {difficulty !==
                    undefined &&
                    difficulty !==
                        null && (
                    <div className="mt-1 flex items-center gap-1 text-xl short:mt-0.5 short:text-xs">
                        <span className="font-semibold">
                            {Array.from(
                                {
                                    length: 5,
                                },
                                (_, index) => (
                                    <span
                                        key={index}
                                        className={
                                            index <
                                            difficulty
                                                ? "text-amber-400"
                                                : "text-muted-foreground/40"
                                        }
                                    >
                                        ★
                                    </span>
                                ),
                            )}
                        </span>
                    </div>
                )}
            </div>
        </div>
    );
}
