"use client";

import { useState } from "react";
import { Settings as SettingsIcon } from "lucide-react";

import { Button } from "@octobeat/ui";

import { SettingsDialog } from "./SettingsDialog";

export function SettingsButton() {
    const [open, setOpen] =
        useState(false);

    return (
        <>
            <Button
                type="button"
                variant="outline"
                size="icon"
                aria-label="Open settings"
                title="Settings"
                onClick={() => setOpen(true)}
                className="pointer-events-auto fixed right-4 top-4 z-50 rounded-full bg-background/70 text-muted-foreground shadow-lg backdrop-blur-md hover:text-foreground"
            >
                <SettingsIcon />
            </Button>

            <SettingsDialog
                open={open}
                onOpenChange={setOpen}
            />
        </>
    );
}
