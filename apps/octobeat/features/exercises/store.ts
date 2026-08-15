import { create } from "zustand";

import {
    loadSpeed,
    saveSpeed,
} from "./speedStorage";

export type Speed =
    | "x1"
    | "x2"
    | "x4";

export const SPEED_FACTOR:
    Record<Speed, number> = {
        x1: 1,
        x2: 2,
        x4: 4,
    };

export const SPEED_LABELS:
    Record<Speed, string> = {
        x1: "1x",
        x2: "2x",
        x4: "4x",
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
