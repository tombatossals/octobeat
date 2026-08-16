"use client";

import { useMemo, useState } from "react";
import { Dialog } from "@base-ui/react/dialog";
import { X } from "lucide-react";

import { DIFFICULTY_ORDER, books } from "@octobeat/exercises";
import {
    Button,
    cn,
    Label,
    MultiSelect,
} from "@octobeat/ui";

import { useLibraryStore } from "../store";

import {
    BPM_RANGES,
    DECADES,
    EMPTY_FILTERS,
} from "../filters";
import type { LibraryFilters } from "../filters";
import { GENRE_GROUPS, genreGroupKeys } from "../genres";

interface FilterDialogProps {
    open: boolean;

    onOpenChange(
        open: boolean,
    ): void;
}

interface FilterDialogContentProps {
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
        exerciseSets: [
            ...filters.exerciseSets,
        ],
        favoritesOnly:
            filters.favoritesOnly,
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

/**
 * The filter form. Mounted while the dialog is open so its draft state is
 * re-initialized from the store's current filters each time it opens. This
 * ensures filters restored from localStorage on page load are shown as
 * active.
 */
function FilterDialogContent({
    onOpenChange,
}: FilterDialogContentProps) {
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

    const [prevFilters, setPrevFilters] =
        useState(filters);

    if (filters !== prevFilters) {
        setPrevFilters(filters);

        setDraft(toDraft(filters));
    }

    const genreCounts = useMemo(() => {
        const counts = new Map<string, number>();

        for (const entry of entries) {
            for (const key of genreGroupKeys(entry.genres)) {
                counts.set(
                    key,
                    (counts.get(key) ?? 0) + 1,
                );
            }
        }

        return counts;
    }, [entries]);

    const genres = useMemo(
        () =>
            GENRE_GROUPS.map(
                (group) => ({
                    value: group.key,
                    label: `${group.label} (${genreCounts.get(group.key) ?? 0})`,
                }),
            ),
        [genreCounts],
    );

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
        <>
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

                            <MultiSelect
                                value={draft.genres}
                                onValueChange={(genres) =>
                                    setDraft(
                                        (current) => ({
                                            ...current,
                                            genres,
                                        }),
                                    )
                                }
                                options={genres}
                                placeholder="All genres"
                                countLabel={(count) =>
                                    count === 1
                                        ? "1 genre"
                                        : `${count} genres`
                                }
                            />
                        </fieldset>

                        <fieldset className="lg:col-span-2">
                            <legend className="mb-2 block text-sm font-semibold text-foreground">
                                Book Sections
                            </legend>

                            <MultiSelect
                                value={draft.exerciseSets}
                                onValueChange={(exerciseSets) =>
                                    setDraft(
                                        (current) => ({
                                            ...current,
                                            exerciseSets,
                                        }),
                                    )
                                }
                                options={[
                                    ...Object.values(
                                        books,
                                    ),
                                ]
                                    .sort(
                                        (a, b) =>
                                            DIFFICULTY_ORDER.indexOf(
                                                a.difficulty,
                                            ) -
                                            DIFFICULTY_ORDER.indexOf(
                                                b.difficulty,
                                            ),
                                    )
                                    .flatMap((book) =>
                                        Object.values(
                                            book.sets,
                                        ).map((set) => ({
                                            value: set.id,
                                            label: `${book.title} · ${set.title}`,
                                        })),
                                    )}
                                placeholder="All sections"
                                countLabel={(count) =>
                                    count === 1
                                        ? "1 section"
                                        : `${count} sections`
                                }
                            />
                        </fieldset>
                    </div>

                        <fieldset className="lg:col-span-2">
                            <legend className="mb-2 block text-sm font-semibold text-foreground">
                                Favorites
                            </legend>

                            <Label className="flex cursor-pointer items-center gap-2.5 rounded-lg px-2 py-1.5 text-sm text-muted-foreground transition hover:bg-accent hover:text-accent-foreground">
                                <input
                                    type="checkbox"
                                    checked={
                                        draft.favoritesOnly
                                    }
                                    onChange={() =>
                                        setDraft(
                                            (current) => ({
                                                ...current,
                                                favoritesOnly:
                                                    !current.favoritesOnly,
                                            }),
                                        )
                                    }
                                    className="size-4 accent-primary"
                                />

                                Solo favoritas
                            </Label>
                        </fieldset>

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
        </>
    );
}

export function FilterDialog({
    open,
    onOpenChange,
}: FilterDialogProps) {
    return (
        <Dialog.Root
            open={open}
            onOpenChange={onOpenChange}
        >
            <Dialog.Portal>
                <Dialog.Backdrop className="fixed inset-0 z-[80] bg-black/60 backdrop-blur-sm" />

                <Dialog.Popup className="fixed left-1/2 top-1/2 z-[90] flex max-h-[85vh] w-[min(90vw,28rem)] -translate-x-1/2 -translate-y-1/2 flex-col rounded-2xl border border-border bg-background p-6 text-foreground shadow-2xl lg:w-[min(90vw,42rem)]">
                    <FilterDialogContent
                        onOpenChange={onOpenChange}
                    />
                </Dialog.Popup>
            </Dialog.Portal>
        </Dialog.Root>
    );
}
