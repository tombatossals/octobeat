"use client";

import { useState } from "react";
import { Settings as SettingsIcon } from "lucide-react";

import { SettingsDialog } from "./SettingsDialog";

const ICON_OUTLINE =
    "drop-shadow(1px 1px 0 var(--icon-outline)) drop-shadow(-1px -1px 0 var(--icon-outline)) drop-shadow(1px -1px 0 var(--icon-outline)) drop-shadow(-1px 1px 0 var(--icon-outline)) drop-shadow(1px 0 0 var(--icon-outline)) drop-shadow(-1px 0 0 var(--icon-outline)) drop-shadow(0 1px 0 var(--icon-outline)) drop-shadow(0 -1px 0 var(--icon-outline))";

export function SettingsButton() {
    const [open, setOpen] =
        useState(false);

    return (
        <>
            <button
                type="button"
                aria-label="Open settings"
                onClick={() => setOpen(true)}
                className="flex cursor-pointer items-center text-foreground transition-colors outline-none focus:outline-none hover:text-muted-foreground"
            >
                <span
                    style={{
                        filter: ICON_OUTLINE,
                    }}
                >
                    <SettingsIcon className="h-9 w-9 short:h-7 short:w-7" />
                </span>
            </button>

            <SettingsDialog
                open={open}
                onOpenChange={setOpen}
            />
        </>
    );
}
