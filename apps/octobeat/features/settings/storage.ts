import { DEFAULT_SETTINGS } from "./defaults";
import { SettingsSchema } from "./schema";

import type { Settings } from "./types";

const STORAGE_KEY = "octobeat.settings";

function hasStorage(): boolean {
    return typeof window !== "undefined";
}

/**
 * Loads settings from localStorage, merged with defaults.
 * Falls back to defaults when the stored value is missing or invalid.
 */
export function loadSettings(): Settings {
    if (!hasStorage()) {
        return DEFAULT_SETTINGS;
    }

    const raw = window.localStorage.getItem(
        STORAGE_KEY,
    );

    if (!raw) {
        return DEFAULT_SETTINGS;
    }

    try {
        const parsed =
            SettingsSchema.safeParse({
                ...DEFAULT_SETTINGS,
                ...JSON.parse(raw),
            });

        if (!parsed.success) {
            return DEFAULT_SETTINGS;
        }

        return {
            ...DEFAULT_SETTINGS,
            ...parsed.data,
        };
    } catch {
        return DEFAULT_SETTINGS;
    }
}

/**
 * Persists settings to localStorage.
 */
export function saveSettings(
    settings: Settings,
): void {
    if (!hasStorage()) {
        return;
    }

    window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(settings),
    );
}

/**
 * Removes persisted settings.
 */
export function clearSettings(): void {
    if (!hasStorage()) {
        return;
    }

    window.localStorage.removeItem(
        STORAGE_KEY,
    );
}
