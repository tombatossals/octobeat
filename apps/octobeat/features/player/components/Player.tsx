"use client";

import { useEffect } from "react";
import type { MouseEvent } from "react";

import { PlayerBackend } from "../backends/PlayerBackend";

import { usePlayerStore } from "@octobeat/player";

import { Logo } from "@/features/overlay/components/Logo";
import { ExerciseOverlay } from "@/features/exercises/components/ExerciseOverlay";
import { DifficultySwitcher } from "@/features/exercises/components/DifficultySwitcher";
import { HeaderActions } from "@/features/library/components/HeaderActions";
import { LyricsOverlay } from "@/features/lyrics/components/LyricsOverlay";
import { SettingsToast } from "@/features/settings/components/SettingsToast";
import { useSettingsHydration } from "@/features/settings/hooks/useSettingsHydration";
import { NowPlayingCard } from "./NowPlayingCard";
import { NowPlayingSummary } from "./NowPlayingSummary";
import { PlayerControlsOverlay } from "./PlayerControlsOverlay";
import { CountdownOverlay } from "./CountdownOverlay";

import {
    useKeyboardShortcuts,
} from "@octobeat/player";

import { useLibraryStore } from "@/features/library/store";
import { useLyricsStore } from "@/features/lyrics/store";
import { useUiVisibility } from "@/features/ui/hooks/useUiVisibility";
import { useUiStore } from "@/features/ui/store";

export function Player() {
    useSettingsHydration();

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

    const dataset = useLibraryStore(
        (state) => state.dataset,
    );

    useEffect(() => {
        if (!dataset) {
            useLyricsStore
                .getState()
                .clear();

            return;
        }

        const stored =
            dataset.songmap.lyrics;

        if (
            stored &&
            stored.length > 0
        ) {
            useLyricsStore
                .getState()
                .setLyrics(stored);

            return;
        }

        void useLyricsStore
            .getState()
            .load(dataset.metadata);
    }, [dataset]);

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

            <CountdownOverlay />

            <Logo />

            <NowPlayingSummary />

            <DifficultySwitcher />

            <NowPlayingCard />

            <ExerciseOverlay />

            <LyricsOverlay />

            <HeaderActions />

            <SettingsToast />

            {uiVisible && (
                <PlayerControlsOverlay />
            )}
        </div>
    );
}