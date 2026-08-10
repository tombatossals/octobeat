"use client";

const STORAGE_KEY = "octobeat.video-offset";

export interface ManualOffset {
    /**
     * Dataset id this manual offset applies to.
     */
    id: string;

    /**
     * Corrected video offset (seconds).
     */
    offset: number;
}

/**
 * Persisted manual video-offset corrections, keyed by dataset id.
 *
 * Datasets are served as static files, so the UI cannot write
 * ``songmap.json`` directly. Corrections made in the UI are stored in
 * localStorage and applied on top of the SongMap's offset when the
 * dataset loads.
 */
const VIDEO_OFFSETS = "octobeat.video-offsets";

export function readManualOffsets(): Record<string, number> {
    try {
        const raw =
            window.localStorage.getItem(
                VIDEO_OFFSETS,
            );

        if (!raw) {
            return {};
        }

        return JSON.parse(raw) as Record<
            string,
            number
        >;
    } catch {
        return {};
    }
}

export function saveManualOffset(
    id: string,
    offset: number,
): void {
    const offsets = readManualOffsets();

    offsets[id] = offset;

    window.localStorage.setItem(
        VIDEO_OFFSETS,
        JSON.stringify(offsets),
    );
}

export function clearManualOffset(
    id: string,
): void {
    const offsets = readManualOffsets();

    delete offsets[id];

    window.localStorage.setItem(
        VIDEO_OFFSETS,
        JSON.stringify(offsets),
    );
}

export function getManualOffset(
    id: string,
): number | null {
    const offsets = readManualOffsets();

    const offset = offsets[id];

    return typeof offset === "number"
        ? offset
        : null;
}

export { STORAGE_KEY };
