import { create } from "zustand";

import { DEFAULT_SETTINGS } from "./defaults";
import {
    loadSettings,
    saveSettings,
} from "./storage";

import type { Settings } from "./types";

const TOAST_DURATION = 2500;

let dismissTimer:
    | ReturnType<typeof setTimeout>
    | null = null;

interface SettingsState {
    /**
     * Current settings.
     */
    settings: Settings;

    /**
     * Whether settings have been hydrated from storage.
     */
    loaded: boolean;

    /**
     * Whether the "saved" toast is visible.
     */
    toastVisible: boolean;

    /**
     * Merge partial changes into the current settings and persist.
     */
    update(partial: Partial<Settings>): void;

    /**
     * Restore defaults and persist.
     */
    reset(): void;

    /**
     * Persist the current settings.
     */
    save(): void;

    /**
     * Hydrate settings from storage.
     */
    load(): void;

    /**
     * Hide the "saved" toast.
     */
    dismissToast(): void;
}

function showToast(
    set: (
        partial: Partial<SettingsState>,
    ) => void,
): void {
    set({
        toastVisible: true,
    });

    if (dismissTimer) {
        clearTimeout(
            dismissTimer,
        );
    }

    dismissTimer = setTimeout(
        () => {
            set({
                toastVisible: false,
            });

            dismissTimer = null;
        },
        TOAST_DURATION,
    );
}

export const useSettingsStore =
    create<SettingsState>((set, get) => ({
        settings: DEFAULT_SETTINGS,

        loaded: false,

        toastVisible: false,

        update(partial) {
            const next = {
                ...get().settings,
                ...partial,
            };

            saveSettings(next);

            set({
                settings: next,
            });

            showToast(set);
        },

        reset() {
            saveSettings(
                DEFAULT_SETTINGS,
            );

            set({
                settings:
                    DEFAULT_SETTINGS,
            });

            showToast(set);
        },

        save() {
            saveSettings(
                get().settings,
            );

            showToast(set);
        },

        load() {
            if (get().loaded) {
                return;
            }

            set({
                settings:
                    loadSettings(),
                loaded: true,
            });
        },

        dismissToast() {
            if (dismissTimer) {
                clearTimeout(
                    dismissTimer,
                );

                dismissTimer = null;
            }

            set({
                toastVisible: false,
            });
        },
    }));
