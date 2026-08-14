"use client";

import { Star } from "lucide-react";

import { cn } from "@octobeat/ui";

import { useLibraryStore } from "@/features/library/store";

export function NowPlayingSummary() {
    const dataset = useLibraryStore(
        (state) => state.dataset,
    );

    const favorites = useLibraryStore(
        (state) => state.favorites,
    );

    const toggleFavorite =
        useLibraryStore(
            (state) =>
                state.toggleFavorite,
        );

    if (!dataset) {
        return null;
    }

    const { metadata } = dataset;

    const favorite =
        favorites.includes(
            metadata.id,
        );

    return (
        <div className="pointer-events-none fixed left-4 top-28 z-40 flex items-start gap-2 bg-background/60 py-2 pl-3 pr-2 text-foreground short:left-3 short:top-16 short:gap-1 short:py-1 short:pl-2 short:pr-1">
            <div className="flex flex-col gap-0.5 border-l-2 border-l-foreground pl-3 short:gap-0 short:pl-2">
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

            <button
                type="button"
                aria-label={
                    favorite
                        ? "Quitar de favoritos"
                        : "Añadir a favoritos"
                }
                aria-pressed={favorite}
                onClick={(event) => {
                    event.stopPropagation();

                    toggleFavorite(
                        metadata.id,
                    );
                }}
                className="pointer-events-auto mt-1 flex shrink-0 cursor-pointer items-center justify-center rounded-lg p-1.5 text-muted-foreground transition-colors outline-none focus:outline-none hover:text-foreground short:mt-0 short:p-1"
            >
                <Star
                    className={cn(
                        "h-6 w-6 short:h-5 short:w-5",
                        favorite &&
                            "fill-amber-400 text-amber-400",
                    )}
                />
            </button>
        </div>
    );
}
