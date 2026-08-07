"use client";

import { useSettingsStore } from "../store";

export function SettingsToast() {
    const visible =
        useSettingsStore(
            (state) =>
                state.toastVisible,
        );

    if (!visible) {
        return null;
    }

    return (
        <button
            type="button"
            onClick={() =>
                useSettingsStore
                    .getState()
                    .dismissToast()
            }
            className="pointer-events-auto fixed bottom-6 left-1/2 z-[100] -translate-x-1/2 rounded-full border border-border bg-background/90 px-4 py-2 text-sm font-medium text-emerald-600 shadow-2xl backdrop-blur-md dark:text-emerald-400"
        >
            ✓ Settings saved
        </button>
    );
}
