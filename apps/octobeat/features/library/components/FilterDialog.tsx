"use client";

import { useMemo, useState } from "react";
import { Dialog } from "@base-ui/react/dialog";
import { X } from "lucide-react";

import { Button, cn, Label } from "@octobeat/ui";

import { useLibraryStore } from "../store";

import {
    BPM_RANGES,
    DECADES,
    EMPTY_FILTERS,
} from "../filters";
import type { LibraryFilters } from "../filters";

interface FilterDialogProps {
    open: boolean;

    onOpenChange(
        open: boolean,
    ): void;
}

function toDraft(
    filters: LibraryFilters,
): LibraryFilters {
    return {
        bpmRanges: [
            ...filters.bpmRanges,
        ],
        genres: [...filters.genres],
        decades: [...filters.decades],
    };
}

function toggle(
    list: readonly string[],
    value: string,
): string[] {
    return list.includes(value)
        ? list.filter(
              (item) =>
                  item !== value,
          )
        : [...list, value];
}

export function FilterDialog({
    open,
    onOpenChange,
}: FilterDialogProps) {
    const filters = useLibraryStore(
        (state) => state.filters,
    );

    const entries = useLibraryStore(
        (state) => state.entries,
    );

    const setFilters =
        useLibraryStore(
            (state) =>
                state.setFilters,
        );

    const [draft, setDraft] =
        useState<LibraryFilters>(
            () => toDraft(filters),
        );

    const genres = useMemo(() => {
        const seen = new Set<string>();

        for (const entry of entries) {
            for (const genre of entry.genres) {
                seen.add(genre);
            }
        }

        return [
            ...seen,
        ].sort((a, b) =>
            a.localeCompare(b),
        );
    }, [entries]);

    const dirty = useMemo(
        () =>
            JSON.stringify(draft) !==
            JSON.stringify(filters),
        [draft, filters],
    );

    function handleSave() {
        setFilters(draft);

        onOpenChange(false);
    }

    return (
        <Dialog.Root
            open={open}
            onOpenChange={onOpenChange}
        >
            <Dialog.Portal>
                <Dialog.Backdrop className="fixed inset-0 z-[80] bg-black/60 backdrop-blur-sm" />

                <Dialog.Popup className="fixed left-1/2 top-1/2 z-[90] flex max-h-[85vh] w-[min(90vw,28rem)] -translate-x-1/2 -translate-y-1/2 flex-col rounded-2xl border border-border bg-background p-6 text-foreground shadow-2xl lg:w-[min(90vw,42rem)]">
                    <div className="mb-6 flex items-center justify-between">
                        <Dialog.Title className="text-xl font-bold text-foreground">
                            Filters
                        </Dialog.Title>

                        <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            aria-label="Close filters"
                            onClick={() =>
                                onOpenChange(
                                    false,
                                )
                            }
                            className="text-muted-foreground hover:text-foreground"
                        >
                            <X />
                        </Button>
                    </div>

                    <div className="grid grid-cols-1 gap-6 overflow-y-auto pr-1 lg:grid-cols-2">
                        <fieldset className="lg:col-span-2">
                            <legend className="mb-2 block text-sm font-semibold text-foreground">
                                BPM
                            </legend>

                            <div className="flex flex-wrap gap-1">
                                {BPM_RANGES.map(
                                    (range) => {
                                        const checked =
                                            draft.bpmRanges.includes(
                                                range.key,
                                            );

                                        return (
                                            <Label
                                                key={
                                                    range.key
                                                }
                                                className={cn(
                                                    "flex cursor-pointer items-center rounded-lg border px-3 py-1.5 text-sm transition",
                                                    checked
                                                        ? "border-primary bg-accent text-foreground"
                                                        : "border-border text-muted-foreground hover:bg-accent/50",
                                                )}
                                            >
                                                <input
                                                    type="checkbox"
                                                    checked={
                                                        checked
                                                    }
                                                    onChange={() =>
                                                        setDraft(
                                                            (current) => ({
                                                                ...current,
                                                                bpmRanges:
                                                                    toggle(
                                                                        current.bpmRanges,
                                                                        range.key,
                                                                    ),
                                                            }),
                                                        )
                                                    }
                                                    className="sr-only"
                                                />

                                                {
                                                    range.label
                                                }
                                            </Label>
                                        );
                                    },
                                )}
                            </div>
                        </fieldset>

                        <fieldset className="lg:col-span-2">
                            <legend className="mb-2 block text-sm font-semibold text-foreground">
                                Year Released
                            </legend>

                            <div className="flex flex-wrap gap-1">
                                {DECADES.map(
                                    (decade) => {
                                        const checked =
                                            draft.decades.includes(
                                                decade.key,
                                            );

                                        return (
                                            <Label
                                                key={
                                                    decade.key
                                                }
                                                className={cn(
                                                    "flex cursor-pointer items-center rounded-lg border px-3 py-1.5 text-sm transition",
                                                    checked
                                                        ? "border-primary bg-accent text-foreground"
                                                        : "border-border text-muted-foreground hover:bg-accent/50",
                                                )}
                                            >
                                                <input
                                                    type="checkbox"
                                                    checked={
                                                        checked
                                                    }
                                                    onChange={() =>
                                                        setDraft(
                                                            (current) => ({
                                                                ...current,
                                                                decades:
                                                                    toggle(
                                                                        current.decades,
                                                                        decade.key,
                                                                    ),
                                                            }),
                                                        )
                                                    }
                                                    className="sr-only"
                                                />

                                                {
                                                    decade.label
                                                }
                                            </Label>
                                        );
                                    },
                                )}
                            </div>
                        </fieldset>

                        <fieldset className="lg:col-span-2">
                            <legend className="mb-2 block text-sm font-semibold text-foreground">
                                Genres
                            </legend>

                            <div className="grid max-h-56 grid-cols-2 gap-1 overflow-y-auto pr-1 lg:grid-cols-3">
                                {genres.map(
                                    (genre) => {
                                        const checked =
                                            draft.genres.includes(
                                                genre,
                                            );

                                        return (
                                            <Label
                                                key={
                                                    genre
                                                }
                                                className="flex cursor-pointer items-center gap-2.5 rounded-lg px-2 py-1.5 text-sm text-muted-foreground transition hover:bg-accent hover:text-accent-foreground"
                                            >
                                                <input
                                                    type="checkbox"
                                                    checked={
                                                        checked
                                                    }
                                                    onChange={() =>
                                                        setDraft(
                                                            (current) => ({
                                                                ...current,
                                                                genres:
                                                                    toggle(
                                                                        current.genres,
                                                                        genre,
                                                                    ),
                                                            }),
                                                        )
                                                    }
                                                    className="size-4 accent-primary"
                                                />

                                                {genre}
                                            </Label>
                                        );
                                    },
                                )}
                            </div>
                        </fieldset>
                    </div>

                    <div className="mt-8 flex justify-end gap-2">
                        <Button
                            variant="ghost"
                            onClick={() => {
                                setFilters(
                                    toDraft(
                                        EMPTY_FILTERS,
                                    ),
                                );

                                onOpenChange(
                                    false,
                                );
                            }}
                        >
                            Clear Filters
                        </Button>

                        <Button
                            variant="ghost"
                            onClick={() =>
                                onOpenChange(
                                    false,
                                )
                            }
                        >
                            Cancel
                        </Button>

                        <Button
                            variant="default"
                            disabled={
                                !dirty
                            }
                            onClick={handleSave}
                        >
                            Apply
                        </Button>
                    </div>
                </Dialog.Popup>
            </Dialog.Portal>
        </Dialog.Root>
    );
}
