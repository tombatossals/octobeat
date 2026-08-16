import type { Speed } from "./store";

const STORAGE_KEY =
    "octobeat.speed";

function hasStorage(): boolean {
    return typeof window !== "undefined";
}

/**
 * Loads the practice speed from localStorage. Falls back to "x1" when
 * the stored value is missing or invalid.
 */
export function loadSpeed(): Speed {
    if (!hasStorage()) {
        return "x1";
    }

    const raw =
        window.localStorage.getItem(
            STORAGE_KEY,
        );

    if (
        raw === "x0_5" ||
        raw === "x1" ||
        raw === "x2"
    ) {
        return raw;
    }

    return "x1";
}

/**
 * Persists the practice speed to localStorage.
 */
export function saveSpeed(
    speed: Speed,
): void {
    if (!hasStorage()) {
        return;
    }

    window.localStorage.setItem(
        STORAGE_KEY,
        speed,
    );
}

/**
 * Removes the persisted practice speed.
 */
export function clearSpeed(): void {
    if (!hasStorage()) {
        return;
    }

    window.localStorage.removeItem(
        STORAGE_KEY,
    );
}
