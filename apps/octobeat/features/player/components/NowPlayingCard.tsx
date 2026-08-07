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
            className="pointer-events-none fixed left-4 top-28 z-40 flex animate-[slideIn_0.4s_ease-out] items-center gap-3 rounded-xl border border-border bg-background/70 p-2 text-foreground shadow-2xl backdrop-blur-md"
        >
            <img
                src={`/resources/${metadata.id}/cover.jpg`}
                alt={`${metadata.title} cover`}
                className="h-12 w-12 rounded-lg object-cover"
            />

            <div className="min-w-0">
                <div className="text-base font-bold leading-tight">
                    {metadata.title}
                </div>

                <div className="truncate text-xs text-muted-foreground">
                    {metadata.artist}
                </div>

                {difficulty !==
                    undefined && (
                    <div className="mt-1 flex items-center gap-1 text-xs">
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
