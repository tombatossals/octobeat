"use client";

import { useEffect } from "react";

import { useUiStore } from "../store";

const POINTER_HIDE_DELAY = 2500;

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

        const setPointerActive =
            useUiStore.getState()
                .setPointerActive;

        let pointerTimer: ReturnType<
            typeof setTimeout
        > | null = null;

        function wakePointer() {
            setPointerActive(true);

            if (pointerTimer) {
                clearTimeout(
                    pointerTimer,
                );
            }

            pointerTimer = setTimeout(
                () => {
                    setPointerActive(
                        false,
                    );

                    pointerTimer =
                        null;
                },
                POINTER_HIDE_DELAY,
            );
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

            if (pointerTimer) {
                clearTimeout(
                    pointerTimer,
                );
            }
        };
    }, []);
}
