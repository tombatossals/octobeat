"use client";

import { useState } from "react";
import { Filter } from "lucide-react";

import { useShortcut } from "@/lib/useShortcut";

import { ShortcutBadge } from "./ShortcutBadge";

const ICON_OUTLINE =
    "drop-shadow(1px 1px 0 #374151) drop-shadow(-1px -1px 0 #374151) drop-shadow(1px -1px 0 #374151) drop-shadow(-1px 1px 0 #374151) drop-shadow(1px 0 0 #374151) drop-shadow(-1px 0 0 #374151) drop-shadow(0 1px 0 #374151) drop-shadow(0 -1px 0 #374151)";

export function FilterButton() {
    const [active, setActive] =
        useState(false);

    useShortcut(
        { code: "KeyF" },
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
            title="Filters (F)"
            aria-pressed={active}
            onClick={() =>
                setActive(
                    (current) =>
                        !current,
                )
            }
            className={[
                "flex cursor-pointer items-center gap-1.5 transition-colors",
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

            <ShortcutBadge label="F" />
        </button>
    );
}
