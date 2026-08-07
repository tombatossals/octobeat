"use client";

import { useEffect } from "react";

import { PlayerBackend } from "../backends/PlayerBackend";

import { usePlayerStore } from "@octobeat/player";

import { DebugHud } from "@/features/overlay/components/DebugHud";
import { ExerciseOverlay } from "@/features/exercises/components/ExerciseOverlay";
import { DifficultySwitcher } from "@/features/exercises/components/DifficultySwitcher";
import { SettingsButton } from "@/features/settings/components/SettingsButton";
import { SettingsToast } from "@/features/settings/components/SettingsToast";
import { useSettingsHydration } from "@/features/settings/hooks/useSettingsHydration";
import { NowPlayingCard } from "./NowPlayingCard";

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

    return (
        <div className="relative h-screen w-screen overflow-hidden bg-black">
            <PlayerBackend />

            <DifficultySwitcher />

            <NowPlayingCard />

            <ExerciseOverlay />

            <DebugHud />

            <SettingsButton />

            <SettingsToast />
        </div>
    );
}