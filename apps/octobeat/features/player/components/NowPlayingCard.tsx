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
            className="pointer-events-none fixed left-4 top-4 z-40 flex animate-[slideIn_0.4s_ease-out] items-center gap-4 rounded-2xl border border-border bg-background/70 p-4 text-foreground shadow-2xl backdrop-blur-md"
        >
            <img
                src={`/resources/${metadata.id}/cover.jpg`}
                alt={`${metadata.title} cover`}
                className="h-24 w-24 rounded-xl object-cover"
            />

            <div className="min-w-0">
                <div className="text-lg font-bold leading-tight">
                    {metadata.title}
                </div>

                <div className="truncate text-sm text-muted-foreground">
                    {metadata.artist}
                </div>

                <div className="mt-2 flex items-center gap-4 text-sm">
                    <div>
                        <span className="text-muted-foreground">
                            BPM{" "}
                        </span>
                        <span className="font-mono font-semibold">
                            {metadata.bpm}
                        </span>
                    </div>

                    {difficulty !==
                        undefined && (
                        <div>
                            <span className="text-muted-foreground">
                                Difficulty{" "}
                            </span>
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
        </div>
    );
}
