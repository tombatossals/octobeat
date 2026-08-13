"use client";

import { useLibraryStore } from "@/features/library/store";

export function NowPlayingSummary() {
    const dataset = useLibraryStore(
        (state) => state.dataset,
    );

    if (!dataset) {
        return null;
    }

    const { metadata } = dataset;

    return (
        <div className="pointer-events-none fixed left-4 top-28 z-40 flex flex-col gap-0.5 border-l-2 border-l-foreground bg-background/60 py-2 pl-3 pr-4 text-foreground short:left-3 short:top-16 short:gap-0 short:py-1 short:pl-2 short:pr-3">
            <div className="text-sm font-bold leading-tight short:text-xs">
                {metadata.title}
            </div>

            <div className="text-xs text-foreground/80 short:text-[10px]">
                {metadata.artist}
            </div>

            {metadata.album && (
                <div className="text-xs text-foreground/60 short:hidden">
                    {metadata.album}
                </div>
            )}

            <div className="text-xs text-foreground/60 short:hidden">
                {metadata.genres.join(
                    ", ",
                )}
                {" · "}
                {metadata.year ?? "—"}
            </div>

            <div className="text-xs text-foreground/60 short:text-[10px]">
                {Math.round(
                    metadata.bpm,
                )}{" "}
                BPM
            </div>
        </div>
    );
}
