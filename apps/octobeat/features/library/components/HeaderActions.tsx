"use client";

import { FullscreenButton } from "@/features/player/components/FullscreenButton";
import { VolumeControl } from "@/features/player/components/VolumeControl";
import { SettingsButton } from "@/features/settings/components/SettingsButton";

import { CatalogSearch } from "./CatalogSearch";
import { FilterButton } from "./FilterButton";

export function HeaderActions() {
    return (
        <div
            onClick={(event) =>
                event.stopPropagation()
            }
            className="pointer-events-auto fixed right-10 top-8 z-50 flex items-start gap-5"
        >
            <FilterButton />

            <CatalogSearch />

            <div className="flex flex-col items-center gap-4">
                <SettingsButton />

                <VolumeControl />

                <FullscreenButton />
            </div>
        </div>
    );
}
