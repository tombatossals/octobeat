"use client";

import { useEffect } from "react";
import type { MouseEvent } from "react";

import { PlayerBackend } from "../backends/PlayerBackend";

import { usePlayerStore } from "@octobeat/player";

import { Logo } from "@/features/overlay/components/Logo";
import { ExerciseOverlay } from "@/features/exercises/components/ExerciseOverlay";
import { SpeedSwitcher } from "@/features/exercises/components/SpeedSwitcher";
import { HeaderActions } from "@/features/library/components/HeaderActions";
import { SettingsToast } from "@/features/settings/components/SettingsToast";
import { useSettingsHydration } from "@/features/settings/hooks/useSettingsHydration";
import { useTheme } from "@/features/settings/hooks/useTheme";
import { NowPlayingSummary } from "./NowPlayingSummary";
import { PlayerControlsOverlay } from "./PlayerControlsOverlay";

import {
    useKeyboardShortcuts,
} from "@octobeat/player";

import { useLibraryStore } from "@/features/library/store";
import { useUiVisibility } from "@/features/ui/hooks/useUiVisibility";
import { useUiStore } from "@/features/ui/store";

export function Player() {
    useSettingsHydration();

    useTheme();

    useUiVisibility();

    const revealed = useUiStore(
        (state) => state.revealed,
    );

    const pointerActive =
        useUiStore(
            (state) =>
                state.pointerActive,
        );

    const uiVisible =
        revealed || pointerActive;

    const next = useLibraryStore(
        (state) => state.next,
    );

    const previous = useLibraryStore(
        (state) => state.previous,
    );

    useKeyboardShortcuts({
        next,
        previous,
        onShortcut: () =>
            useUiStore.getState().wakePointer(),
    });

    const playPause = usePlayerStore(
        (state) => state.playPause,
    );

    const setStarted = usePlayerStore(
        (state) => state.setStarted,
    );

    useEffect(() => {
        async function autoStart() {
            try {
                await playPause();

                setStarted(true);
            } catch (error) {
                console.error(error);
            }
        }

        void autoStart();
    }, [playPause, setStarted]);

    const player = usePlayerStore(
        (state) => state.player,
    );

    useEffect(() => {
        if (!player) {
            return;
        }

        return player.on("ended", () => {
            void next();
        });
    }, [player, next]);

    function handleClick(
        event: MouseEvent<HTMLDivElement>,
    ) {
        const target =
            event.target as HTMLElement | null;

        if (
            target &&
            target.closest(
                "button, a, input, select, textarea, [role='button']",
            )
        ) {
            return;
        }

        void playPause();
    }

    return (
        <div
            onClick={handleClick}
            className="relative h-screen w-screen overflow-hidden bg-background"
        >
            <PlayerBackend />

            <Logo />

            <SpeedSwitcher />

            <NowPlayingSummary />

            <ExerciseOverlay />

            <HeaderActions />

            <SettingsToast />

            {uiVisible && (
                <PlayerControlsOverlay />
            )}
        </div>
    );
}