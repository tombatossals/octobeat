"use client";

import { useEffect } from "react";

import { useUiStore } from "../store";

/**
 * Drives interface visibility:
 *
 * - Moving the mouse reveals the UI (without shortcut badges).
 * - Holding Ctrl/Cmd reveals the UI and shows the shortcut badges.
 */
export function useUiVisibility(): void {
    useEffect(() => {
        const setRevealed =
            useUiStore.getState()
                .setRevealed;

        function wakePointer() {
            useUiStore.getState()
                .wakePointer();
        }

        function onKeyDown(
            event: KeyboardEvent,
        ) {
            if (
                event.ctrlKey ||
                event.metaKey
            ) {
                setRevealed(true);
            }
        }

        function onKeyUp(
            event: KeyboardEvent,
        ) {
            if (
                !event.ctrlKey &&
                !event.metaKey
            ) {
                setRevealed(false);
            }
        }

        function onBlur() {
            setRevealed(false);
        }

        window.addEventListener(
            "mousemove",
            wakePointer,
        );

        window.addEventListener(
            "mousedown",
            wakePointer,
        );

        window.addEventListener(
            "keydown",
            onKeyDown,
        );

        window.addEventListener(
            "keyup",
            onKeyUp,
        );

        window.addEventListener(
            "blur",
            onBlur,
        );

        return () => {
            window.removeEventListener(
                "mousemove",
                wakePointer,
            );

            window.removeEventListener(
                "mousedown",
                wakePointer,
            );

            window.removeEventListener(
                "keydown",
                onKeyDown,
            );

            window.removeEventListener(
                "keyup",
                onKeyUp,
            );

            window.removeEventListener(
                "blur",
                onBlur,
            );
        };
    }, []);
}
