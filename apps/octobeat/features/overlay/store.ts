import { create } from "zustand";

interface DebugStore {
    enabled: boolean;

    toggle(): void;
}

export const useDebugStore =
    create<DebugStore>((set) => ({
        enabled: true,

        toggle() {
            set((state) => ({
                enabled: !state.enabled,
            }));
        },
    }));