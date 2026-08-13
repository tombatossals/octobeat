"use client";

import { useState } from "react";
import { Filter } from "lucide-react";

import { useShortcut } from "@/lib/useShortcut";

import { useUiStore } from "@/features/ui/store";

import { useLibraryStore } from "../store";
import { isEmptyFilters } from "../filters";

import { ShortcutBadge } from "./ShortcutBadge";
import { FilterDialog } from "./FilterDialog";

const ICON_OUTLINE =
    "drop-shadow(1px 1px 0 var(--icon-outline)) drop-shadow(-1px -1px 0 var(--icon-outline)) drop-shadow(1px -1px 0 var(--icon-outline)) drop-shadow(-1px 1px 0 var(--icon-outline)) drop-shadow(1px 0 0 var(--icon-outline)) drop-shadow(-1px 0 0 var(--icon-outline)) drop-shadow(0 1px 0 var(--icon-outline)) drop-shadow(0 -1px 0 var(--icon-outline))";

export function FilterButton() {
    const [open, setOpen] =
        useState(false);

    const filters = useLibraryStore(
        (state) => state.filters,
    );

    const revealed = useUiStore(
        (state) => state.revealed,
    );

    const active = !isEmptyFilters(
        filters,
    );

    useShortcut(
        { code: "KeyF", meta: true },
        () =>
            setOpen(
                (current) =>
                    !current,
            ),
    );

    return (
        <>
            <button
                type="button"
                aria-label="Filters"
                title="Filters (⌘F)"
                aria-pressed={active}
                onClick={() =>
                    setOpen(
                        (current) =>
                            !current,
                    )
                }
                className={[
                    "relative flex cursor-pointer items-center transition-colors",
                    active
                        ? "text-amber-400"
                        : "text-foreground hover:text-muted-foreground",
                ].join(" ")}
            >
                <span
                    style={{
                        filter: ICON_OUTLINE,
                    }}
                >
                    <Filter className="h-7 w-7 short:h-6 short:w-6" />
                </span>

                {revealed && (
                    <span className="absolute -right-3 -top-4">
                        <ShortcutBadge
                            label="F"
                            className="border border-border"
                        />
                    </span>
                )}
            </button>

            <FilterDialog
                open={open}
                onOpenChange={setOpen}
            />
        </>
    );
}
