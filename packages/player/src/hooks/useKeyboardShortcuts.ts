"use client";

import { useEffect } from "react";

import { usePlayerStore } from "../store";

const SEEK_SECONDS = 5;

export interface KeyboardShortcutsOptions {
    next?: () => void;
    previous?: () => void;
}

export function useKeyboardShortcuts({
    next,
    previous,
}: KeyboardShortcutsOptions = {}) {
    const player = usePlayerStore(
        (state) => state.player,
    );

    const started = usePlayerStore(
        (state) => state.started,
    );

    useEffect(() => {
        if (!started || !player) {
            return;
        }

        const mediaPlayer = player;

        function onKeyDown(
            event: KeyboardEvent,
        ) {
            // No capturar atajos mientras se escribe
            const target =
                event.target as HTMLElement | null;

            if (
                target &&
                (target.tagName === "INPUT" ||
                    target.tagName ===
                    "TEXTAREA" ||
                    target.isContentEditable)
            ) {
                return;
            }

            switch (event.code) {
                case "Space":
                    event.preventDefault();

                    void mediaPlayer.playPause();

                    break;

                case "ArrowLeft":
                    event.preventDefault();

                    mediaPlayer.seek(
                        Math.max(
                            0,
                            mediaPlayer.currentTime() -
                            SEEK_SECONDS,
                        ),
                    );

                    break;

                case "ArrowRight":
                    event.preventDefault();

                    mediaPlayer.seek(
                        Math.min(
                            mediaPlayer.duration(),
                            mediaPlayer.currentTime() +
                            SEEK_SECONDS,
                        ),
                    );

                    break;

                case "Home":
                    event.preventDefault();

                    mediaPlayer.seek(0);

                    break;

                case "End":
                    event.preventDefault();

                    mediaPlayer.seek(
                        mediaPlayer.duration(),
                    );

                    break;
                case "KeyN":
                    event.preventDefault();
                    next?.();
                    break;

                case "KeyP":
                    event.preventDefault();
                    previous?.();
                    break;
            }
        }

        window.addEventListener(
            "keydown",
            onKeyDown,
        );

        return () => {
            window.removeEventListener(
                "keydown",
                onKeyDown,
            );
        };
    }, [started, player, next, previous]);
}