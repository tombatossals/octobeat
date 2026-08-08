import { create } from "zustand";

const POINTER_HIDE_DELAY = 1000;

interface UiState {
    /**
     * Whether Ctrl/Cmd is held down.
     */
    revealed: boolean;

    /**
     * Whether the pointer was moved recently.
     */
    pointerActive: boolean;

    setRevealed(
        revealed: boolean,
    ): void;

    setPointerActive(
        active: boolean,
    ): void;

    /**
     * Mark the pointer as active and schedule an
     * auto-hide after a short delay.
     */
    wakePointer(): void;
}

let pointerTimer: ReturnType<
    typeof setTimeout
> | null = null;

export const useUiStore =
    create<UiState>((set) => ({
        revealed: false,

        pointerActive: false,

        setRevealed(revealed) {
            set({ revealed });
        },

        setPointerActive(active) {
            set({ pointerActive: active });
        },

        wakePointer() {
            set({
                pointerActive: true,
            });

            if (pointerTimer) {
                clearTimeout(
                    pointerTimer,
                );
            }

            pointerTimer =
                setTimeout(() => {
                    set({
                        pointerActive:
                            false,
                    });

                    pointerTimer =
                        null;
                }, POINTER_HIDE_DELAY);
        },
    }));
