"use client";

import { useEffect, useState } from "react";
import {
    Maximize,
    Minimize,
} from "lucide-react";

import { useShortcut } from "@/lib/useShortcut";

import { ShortcutBadge } from "@/features/library/components/ShortcutBadge";
import { useUiStore } from "@/features/ui/store";

const ICON_OUTLINE =
    "drop-shadow(1px 1px 0 var(--icon-outline)) drop-shadow(-1px -1px 0 var(--icon-outline)) drop-shadow(1px -1px 0 var(--icon-outline)) drop-shadow(-1px 1px 0 var(--icon-outline)) drop-shadow(1px 0 0 var(--icon-outline)) drop-shadow(-1px 0 0 var(--icon-outline)) drop-shadow(0 1px 0 var(--icon-outline)) drop-shadow(0 -1px 0 var(--icon-outline))";

export function FullscreenButton() {
    const [isFullscreen, setIsFullscreen] =
        useState(false);

    const revealed = useUiStore(
        (state) => state.revealed,
    );

    useEffect(() => {
        function handleChange() {
            setIsFullscreen(
                Boolean(
                    document.fullscreenElement,
                ),
            );
        }

        document.addEventListener(
            "fullscreenchange",
            handleChange,
        );

        return () => {
            document.removeEventListener(
                "fullscreenchange",
                handleChange,
            );
        };
    }, []);

    function handleToggle() {
        if (document.fullscreenElement) {
            void document.exitFullscreen();
        } else {
            void document.documentElement.requestFullscreen();
        }
    }

    useShortcut(
        { code: "KeyF", plain: true },
        handleToggle,
    );

    const Icon = isFullscreen
        ? Minimize
        : Maximize;

    return (
        <button
            type="button"
            aria-label="Toggle fullscreen"
            title="Toggle fullscreen"
            onClick={handleToggle}
            className="relative flex cursor-pointer items-center text-foreground transition-colors outline-none focus:outline-none hover:text-muted-foreground"
        >
            <span
                style={{
                    filter: ICON_OUTLINE,
                }}
            >
                <Icon className="h-7 w-7" />
            </span>

            {revealed && (
                <span className="absolute -right-3 -top-4">
                    <ShortcutBadge
                        label="F"
                        className="border border-border"
                    />
                </span>
            )}
        </button>
    );
}
