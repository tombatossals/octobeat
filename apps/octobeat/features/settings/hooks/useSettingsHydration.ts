"use client";

import { useEffect } from "react";

import { useSettingsStore } from "../store";

/**
 * Hydrates settings from storage on mount.
 */
export function useSettingsHydration(): void {
    const load = useSettingsStore(
        (state) => state.load,
    );

    useEffect(() => {
        load();
    }, [load]);
}
