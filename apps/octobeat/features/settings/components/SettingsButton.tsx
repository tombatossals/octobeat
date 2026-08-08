"use client";

import { useState } from "react";
import { Settings as SettingsIcon } from "lucide-react";

import { SettingsDialog } from "./SettingsDialog";

export function SettingsButton() {
    const [open, setOpen] =
        useState(false);

    return (
        <>
            <button
                type="button"
                aria-label="Open settings"
                title="Settings"
                onClick={() => setOpen(true)}
                className="cursor-pointer text-white transition-colors hover:text-gray-400"
                style={{
                    filter:
                        "drop-shadow(1px 1px 0 #374151) drop-shadow(-1px -1px 0 #374151) drop-shadow(1px -1px 0 #374151) drop-shadow(-1px 1px 0 #374151) drop-shadow(1px 0 0 #374151) drop-shadow(-1px 0 0 #374151) drop-shadow(0 1px 0 #374151) drop-shadow(0 -1px 0 #374151)",
                }}
            >
                <SettingsIcon className="h-9 w-9" />
            </button>

            <SettingsDialog
                open={open}
                onOpenChange={setOpen}
            />
        </>
    );
}
