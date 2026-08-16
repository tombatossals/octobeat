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
        <div
            key={metadata.id}
            className="pointer-events-none fixed right-24 top-[5rem] z-40 flex animate-[fadeIn_300ms_ease-out] items-start gap-2 rounded-md border border-neutral-300/60 bg-background/60 py-2 pl-2 pr-2 text-foreground short:right-8 short:top-[3.5rem] short:gap-1 short:py-1 short:pl-1 short:pr-1 dark:border-neutral-600/60"
            style={{ boxShadow: "var(--summary-shadow)" }}
        >
            <img
                src={`/resources/${metadata.id}/cover.jpg`}
                alt={`${metadata.title} cover`}
                className="h-20 w-20 shrink-0 self-center object-cover shadow-lg short:h-12 short:w-12"
            />

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
                        : "Marcar como favorita"
                }
                aria-pressed={favorite}
                title={
                    favorite
                        ? "Quitar de favoritos"
                        : "Marcar como favorita"
                }
                onClick={(event) => {
                    event.stopPropagation();

                    toggleFavorite(
                        metadata.id,
                    );
                }}
                className={cn(
                    "pointer-events-auto flex shrink-0 cursor-pointer items-center justify-center rounded-lg p-1 transition-transform outline-none focus:outline-none active:scale-90",
                    favorite
                        ? "text-amber-400 hover:scale-110"
                        : "text-muted-foreground hover:scale-110 hover:text-amber-400",
                )}
            >
                <Star
                    className={cn(
                        "h-6 w-6 short:h-5 short:w-5",
                        favorite &&
                            "fill-amber-400 drop-shadow-[0_0_6px_rgba(251,191,36,0.6)]",
                    )}
                />
            </button>
        </div>
    );
}
