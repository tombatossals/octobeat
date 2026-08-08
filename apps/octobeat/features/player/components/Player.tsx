"use client";

import { useEffect } from "react";
import type { MouseEvent } from "react";

import { PlayerBackend } from "../backends/PlayerBackend";

import { usePlayerStore } from "@octobeat/player";

import { DebugHud } from "@/features/overlay/components/DebugHud";
import { Logo } from "@/features/overlay/components/Logo";
import { ExerciseOverlay } from "@/features/exercises/components/ExerciseOverlay";
import { DifficultySwitcher } from "@/features/exercises/components/DifficultySwitcher";
import { HeaderActions } from "@/features/library/components/HeaderActions";
import { SettingsToast } from "@/features/settings/components/SettingsToast";
import { useSettingsHydration } from "@/features/settings/hooks/useSettingsHydration";
import { NowPlayingCard } from "./NowPlayingCard";
import { PlayerControlsOverlay } from "./PlayerControlsOverlay";

import {
    useKeyboardShortcuts,
} from "@octobeat/player";

import { useLibraryStore } from "@/features/library/store";

export function Player() {
    useSettingsHydration();

    const next = useLibraryStore(
        (state) => state.next,
    );

    const previous = useLibraryStore(
        (state) => state.previous,
    );

    useKeyboardShortcuts({
        next,
        previous,
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

    function handleVideoClick(
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
            onClick={handleVideoClick}
            className="relative h-screen w-screen overflow-hidden bg-black"
        >
            <PlayerBackend />

            <Logo />

            <DifficultySwitcher />

            <NowPlayingCard />

            <PlayerControlsOverlay />

            <ExerciseOverlay />

            <DebugHud />

            <HeaderActions />

            <SettingsToast />
        </div>
    );
}