"use client";

import { useState } from "react";
import { Settings as SettingsIcon } from "lucide-react";

import { useShortcut } from "@/lib/useShortcut";

import { useUiStore } from "@/features/ui/store";

import { ShortcutBadge } from "@/features/library/components/ShortcutBadge";

import { SettingsDialog } from "./SettingsDialog";

const ICON_OUTLINE =
    "drop-shadow(1px 1px 0 #374151) drop-shadow(-1px -1px 0 #374151) drop-shadow(1px -1px 0 #374151) drop-shadow(-1px 1px 0 #374151) drop-shadow(1px 0 0 #374151) drop-shadow(-1px 0 0 #374151) drop-shadow(0 1px 0 #374151) drop-shadow(0 -1px 0 #374151)";

export function SettingsButton() {
    const [open, setOpen] =
        useState(false);

    useShortcut(
        { code: "Comma", meta: true },
        () => setOpen(true),
    );

    const revealed = useUiStore(
        (state) => state.revealed,
    );

    return (
        <>
            <button
                type="button"
                aria-label="Open settings"
                title="Open settings (⌘,)"
                onClick={() => setOpen(true)}
                className="relative flex cursor-pointer items-center text-white transition-colors hover:text-gray-400"
            >
                <span
                    style={{
                        filter: ICON_OUTLINE,
                    }}
                >
                    <SettingsIcon className="h-9 w-9" />
                </span>

                {revealed && (
                    <span className="absolute -right-2 -top-2">
                        <ShortcutBadge label="⌘," />
                    </span>
                )}
            </button>

            <SettingsDialog
                open={open}
                onOpenChange={setOpen}
            />
        </>
    );
}
