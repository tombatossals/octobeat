import { create } from "zustand";

import {
    loadSpeed,
    saveSpeed,
} from "./speedStorage";

export type Speed =
    | "x0_5"
    | "x1"
    | "x2";

export const SPEED_FACTOR:
    Record<Speed, number> = {
        x0_5: 0.5,
        x1: 1,
        x2: 2,
    };

export const SPEED_LABELS:
    Record<Speed, string> = {
        x0_5: "0.5x",
        x1: "1x",
        x2: "2x",
    };

export const SPEED_SHORTCUTS:
    Record<Speed, string> = {
        x0_5: "0",
        x1: "1",
        x2: "2",
    };

interface SpeedState {
    speed: Speed;

    setSpeed(
        speed: Speed,
    ): void;
}

export const useSpeedStore =
    create<SpeedState>((set) => ({
        speed: loadSpeed(),

        setSpeed(speed) {
            saveSpeed(speed);

            set({
                speed,
            });
        },
    }));
