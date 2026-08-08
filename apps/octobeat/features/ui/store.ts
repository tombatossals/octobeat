import { create } from "zustand";

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
}

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
    }));
