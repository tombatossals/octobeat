"use client";

import { SettingsButton } from "@/features/settings/components/SettingsButton";

import { CatalogSearch } from "./CatalogSearch";
import { FilterButton } from "./FilterButton";

export function HeaderActions() {
    return (
        <div
            onClick={(event) =>
                event.stopPropagation()
            }
            className="pointer-events-auto fixed right-10 top-8 z-50 flex items-center gap-3"
        >
            <FilterButton />

            <CatalogSearch />

            <SettingsButton />
        </div>
    );
}
