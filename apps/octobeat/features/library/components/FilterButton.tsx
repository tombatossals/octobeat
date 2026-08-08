"use client";

import { useState } from "react";
import { Filter } from "lucide-react";

const ICON_OUTLINE =
    "drop-shadow(1px 1px 0 #374151) drop-shadow(-1px -1px 0 #374151) drop-shadow(1px -1px 0 #374151) drop-shadow(-1px 1px 0 #374151) drop-shadow(1px 0 0 #374151) drop-shadow(-1px 0 0 #374151) drop-shadow(0 1px 0 #374151) drop-shadow(0 -1px 0 #374151)";

export function FilterButton() {
    const [active, setActive] =
        useState(false);

    return (
        <button
            type="button"
            aria-label="Filters"
            title="Filters"
            aria-pressed={active}
            onClick={() =>
                setActive(
                    (current) =>
                        !current,
                )
            }
            className={[
                "cursor-pointer transition-colors",
                active
                    ? "text-amber-400"
                    : "text-white hover:text-gray-400",
            ].join(" ")}
            style={{
                filter: ICON_OUTLINE,
            }}
        >
            <Filter className="h-7 w-7" />
        </button>
    );
}
