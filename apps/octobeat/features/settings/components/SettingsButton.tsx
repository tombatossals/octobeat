"use client";

import { useState } from "react";
import { Settings as SettingsIcon } from "lucide-react";

import { SettingsDialog } from "./SettingsDialog";

const ICON_OUTLINE =
    "drop-shadow(1px 1px 0 #374151) drop-shadow(-1px -1px 0 #374151) drop-shadow(1px -1px 0 #374151) drop-shadow(-1px 1px 0 #374151) drop-shadow(1px 0 0 #374151) drop-shadow(-1px 0 0 #374151) drop-shadow(0 1px 0 #374151) drop-shadow(0 -1px 0 #374151)";

export function SettingsButton() {
    const [open, setOpen] =
        useState(false);

    return (
        <>
            <button
                type="button"
                aria-label="Open settings"
                onClick={() => setOpen(true)}
                className="flex cursor-pointer items-center text-white transition-colors outline-none focus:outline-none hover:text-gray-400"
            >
                <span
                    style={{
                        filter: ICON_OUTLINE,
                    }}
                >
                    <SettingsIcon className="h-9 w-9" />
                </span>
            </button>

            <SettingsDialog
                open={open}
                onOpenChange={setOpen}
            />
        </>
    );
}
