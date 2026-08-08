"use client";

import { useEffect, useRef } from "react";

export interface ShortcutOptions {
    /**
     * KeyboardEvent.code, e.g. "KeyF", "Comma".
     */
    code: string;

    /**
     * Require Cmd (macOS) / Ctrl (other platforms).
     */
    meta?: boolean;

    /**
     * Require Shift.
     */
    shift?: boolean;

    /**
     * Require Alt.
     */
    alt?: boolean;

    /**
     * Require that no modifier (Ctrl/Cmd/Shift/Alt) is pressed.
     */
    plain?: boolean;
}

/**
 * Registers a global keyboard shortcut.
 */
export function useShortcut(
    options: ShortcutOptions,
    handler: () => void,
): void {
    const handlerRef =
        useRef(handler);

    useEffect(() => {
        handlerRef.current = handler;
    }, [handler]);

    useEffect(() => {
        function onKeyDown(
            event: KeyboardEvent,
        ) {
            const target =
                event.target as HTMLElement | null;

            if (
                target &&
                (target.tagName ===
                    "INPUT" ||
                    target.tagName ===
                        "TEXTAREA" ||
                    target.isContentEditable)
            ) {
                return;
            }

            if (
                event.code !==
                options.code
            ) {
                return;
            }

            // Cuando meta es true, exige Ctrl/Cmd pulsado.
            // Cuando no se especifica, el modificador se ignora.
            if (
                options.meta &&
                !(
                    event.metaKey ||
                    event.ctrlKey
                )
            ) {
                return;
            }

            if (
                (options.shift ??
                    false) !==
                event.shiftKey
            ) {
                return;
            }

            if (
                (options.alt ?? false) !==
                event.altKey
            ) {
                return;
            }

            if (
                options.plain &&
                (event.metaKey ||
                    event.ctrlKey ||
                    event.shiftKey ||
                    event.altKey)
            ) {
                return;
            }

            event.preventDefault();

            handlerRef.current();
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
    }, [
        options.code,
        options.meta,
        options.shift,
        options.alt,
        options.plain,
    ]);
}
