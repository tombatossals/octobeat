"use client";

import {
    useEffect,
    useMemo,
    useRef,
    useState,
} from "react";
import type { JSX } from "react";
import { Dialog } from "@base-ui/react/dialog";
import { Search } from "lucide-react";

import { cn } from "@octobeat/ui";

import type { Metadata } from "@octobeat/library";

import { getLibrary } from "@/lib/library";
import { useShortcut } from "@/lib/useShortcut";

import { useUiStore } from "@/features/ui/store";

import { useLibraryStore } from "../store";

import { ShortcutBadge } from "./ShortcutBadge";

const ICON_OUTLINE =
    "drop-shadow(1px 1px 0 #374151) drop-shadow(-1px -1px 0 #374151) drop-shadow(1px -1px 0 #374151) drop-shadow(-1px 1px 0 #374151) drop-shadow(1px 0 0 #374151) drop-shadow(-1px 0 0 #374151) drop-shadow(0 1px 0 #374151) drop-shadow(0 -1px 0 #374151)";

export function CatalogSearch(): JSX.Element {
    const [open, setOpen] =
        useState(false);

    const [query, setQuery] =
        useState("");

    const [entries, setEntries] =
        useState<readonly Metadata[]>([]);

    const [selected, setSelected] =
        useState(0);

    const inputRef =
        useRef<HTMLInputElement>(null);

    const openSong = useLibraryStore(
        (state) => state.open,
    );

    const revealed = useUiStore(
        (state) => state.revealed,
    );

    useShortcut(
        { code: "KeyK", meta: true },
        () => handleOpenChange(true),
    );

    useEffect(() => {
        if (!open) {
            return;
        }

        void getLibrary()
            .list()
            .then(setEntries);

        const focusTimer =
            setTimeout(
                () =>
                    inputRef.current?.focus(),
                50,
            );

        return () => {
            clearTimeout(
                focusTimer,
            );
        };
    }, [open]);

    function handleOpenChange(
        next: boolean,
    ) {
        if (next) {
            setQuery("");
            setSelected(0);
        }

        setOpen(next);
    }

    const results = useMemo(() => {
        const needle =
            query.trim().toLowerCase();

        const filtered = needle
            ? entries.filter((entry) =>
                  `${entry.artist} ${entry.title}`
                      .toLowerCase()
                      .includes(needle),
              )
            : entries;

        return [...filtered].sort(
            (a, b) =>
                `${a.artist} - ${a.title}`.localeCompare(
                    `${b.artist} - ${b.title}`,
                ),
        );
    }, [entries, query]);

    function handleKeyDown(
        event: React.KeyboardEvent<HTMLInputElement>,
    ) {
        switch (event.key) {
            case "ArrowDown":
                event.preventDefault();

                setSelected((current) =>
                    Math.min(
                        current + 1,
                        results.length - 1,
                    ),
                );

                break;

            case "ArrowUp":
                event.preventDefault();

                setSelected((current) =>
                    Math.max(
                        current - 1,
                        0,
                    ),
                );

                break;

            case "Enter":
                event.preventDefault();

                const entry =
                    results[selected];

                if (entry) {
                    void handleSelect(
                        entry,
                    );
                }

                break;
        }
    }

    async function handleSelect(
        entry: Metadata,
    ) {
        await openSong(entry.id);

        setOpen(false);
    }

    return (
        <>
            <button
                type="button"
                aria-label="Search catalog"
                title="Search catalog (⌘K)"
                onClick={() =>
                    handleOpenChange(
                        true,
                    )
                }
                className="relative flex cursor-pointer items-center text-white transition-colors outline-none focus:outline-none hover:text-gray-400"
            >
                <span
                    style={{
                        filter: ICON_OUTLINE,
                    }}
                >
                    <Search className="h-7 w-7" />
                </span>

                {revealed && (
                    <span className="absolute -right-3 -top-4">
                        <ShortcutBadge
                            label="K"
                            className="border border-white/60"
                        />
                    </span>
                )}
            </button>

            <Dialog.Root
                open={open}
                onOpenChange={handleOpenChange}
            >
                <Dialog.Portal>
                    <Dialog.Backdrop className="fixed inset-0 z-[80] bg-black/60 backdrop-blur-sm" />

                    <Dialog.Popup className="fixed left-1/2 top-[18%] z-[90] w-[min(90vw,32rem)] -translate-x-1/2 overflow-hidden rounded-2xl border border-border bg-background shadow-2xl">
                        <div className="flex items-center gap-3 border-b border-border px-4">
                            <Search className="h-4 w-4 shrink-0 text-muted-foreground" />

                            <input
                                ref={inputRef}
                                type="text"
                                value={query}
                                onChange={(event) => {
                                    setQuery(
                                        event
                                            .target
                                            .value,
                                    );

                                    setSelected(
                                        0,
                                    );
                                }}
                                onKeyDown={
                                    handleKeyDown
                                }
                                placeholder="Buscar canción…"
                                className="h-12 w-full bg-transparent text-foreground outline-none placeholder:text-muted-foreground"
                            />

                            <kbd className="shrink-0 rounded border border-border bg-muted px-1.5 py-0.5 text-xs text-muted-foreground">
                                Esc
                            </kbd>
                        </div>

                        <ul
                            className="max-h-96 overflow-y-auto p-2"
                            role="listbox"
                        >
                            {results.map(
                                (
                                    entry,
                                    index,
                                ) => (
                                    <li
                                        key={
                                            entry.id
                                        }
                                        role="option"
                                        aria-selected={
                                            index ===
                                            selected
                                        }
                                    >
                                        <button
                                            type="button"
                                            onMouseEnter={() =>
                                                setSelected(
                                                    index,
                                                )
                                            }
                                            onClick={() =>
                                                void handleSelect(
                                                    entry,
                                                )
                                            }
                                            className={cn(
                                                "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left transition-colors",
                                                index ===
                                                    selected
                                                    ? "bg-accent text-accent-foreground"
                                                    : "text-foreground hover:bg-accent/50",
                                            )}
                                        >
                                            <div className="min-w-0">
                                                <div className="truncate text-sm font-medium">
                                                    {
                                                        entry.title
                                                    }
                                                </div>

                                                <div className="truncate text-xs text-muted-foreground">
                                                    {
                                                        entry.artist
                                                    }
                                                </div>
                                            </div>
                                        </button>
                                    </li>
                                ),
                            )}

                            {results.length ===
                                0 && (
                                <li className="px-3 py-6 text-center text-sm text-muted-foreground">
                                    Sin resultados
                                </li>
                            )}
                        </ul>

                        <div className="flex items-center gap-4 border-t border-border px-4 py-2 text-xs text-muted-foreground">
                            <span>
                                ↑↓ Navegar
                            </span>

                            <span>
                                ↵ Abrir
                            </span>
                        </div>
                    </Dialog.Popup>
                </Dialog.Portal>
            </Dialog.Root>
        </>
    );
}
