"use client";

import { useState } from "react";
import { Filter } from "lucide-react";

import { useShortcut } from "@/lib/useShortcut";

import { useUiStore } from "@/features/ui/store";

import { ShortcutBadge } from "./ShortcutBadge";

const ICON_OUTLINE =
    "drop-shadow(1px 1px 0 #374151) drop-shadow(-1px -1px 0 #374151) drop-shadow(1px -1px 0 #374151) drop-shadow(-1px 1px 0 #374151) drop-shadow(1px 0 0 #374151) drop-shadow(-1px 0 0 #374151) drop-shadow(0 1px 0 #374151) drop-shadow(0 -1px 0 #374151)";

export function FilterButton() {
    const [active, setActive] =
        useState(false);

    const revealed = useUiStore(
        (state) => state.revealed,
    );

    useShortcut(
        { code: "KeyF", meta: true },
        () =>
            setActive(
                (current) =>
                    !current,
            ),
    );

    return (
        <button
            type="button"
            aria-label="Filters"
            title="Filters (⌘F)"
            aria-pressed={active}
            onClick={() =>
                setActive(
                    (current) =>
                        !current,
                )
            }
            className={[
                "relative flex cursor-pointer items-center transition-colors",
                active
                    ? "text-amber-400"
                    : "text-white hover:text-gray-400",
            ].join(" ")}
        >
            <span
                style={{
                    filter: ICON_OUTLINE,
                }}
            >
                <Filter className="h-7 w-7" />
            </span>

                {revealed && (
                    <span className="absolute -right-3 -top-4">
                        <ShortcutBadge
                            label="F"
                            className="border border-white/60"
                        />
                    </span>
                )}
        </button>
    );
}
