const STORAGE_KEY =
    "octobeat.favorites";

function hasStorage(): boolean {
    return typeof window !== "undefined";
}

/**
 * Loads favorite dataset ids from localStorage. Falls back to an empty
 * list when the stored value is missing or invalid.
 */
export function loadFavorites(): string[] {
    if (!hasStorage()) {
        return [];
    }

    const raw =
        window.localStorage.getItem(
            STORAGE_KEY,
        );

    if (!raw) {
        return [];
    }

    try {
        const parsed =
            JSON.parse(raw) as unknown;

        if (!Array.isArray(parsed)) {
            return [];
        }

        return parsed.filter(
            (id): id is string =>
                typeof id === "string",
        );
    } catch {
        return [];
    }
}

/**
 * Persists favorite dataset ids to localStorage.
 */
export function saveFavorites(
    favorites: readonly string[],
): void {
    if (!hasStorage()) {
        return;
    }

    window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(favorites),
    );
}
