"use client";

import { useMemo, useState } from "react";
import { Dialog } from "@base-ui/react/dialog";
import { X } from "lucide-react";

import {
    Button,
    cn,
    Input,
    Label,
} from "@octobeat/ui";

import { useSettingsStore } from "../store";
import { SettingsSchema, isHttpsUrl } from "../schema";

import type { Settings } from "../types";

interface SettingsDialogProps {
    open: boolean;

    onOpenChange(
        open: boolean,
    ): void;
}

function toDraft(
    settings: Settings,
): Settings {
    return {
        catalogUrl:
            settings.catalogUrl,
        repetitionsPerLine:
            settings.repetitionsPerLine,
        theme: settings.theme,
    };
}

interface SettingsFormProps {
    settings: Settings;

    onSave(
        settings: Settings,
    ): void;

    onCancel(): void;
}

function SettingsForm({
    settings,
    onSave,
    onCancel,
}: SettingsFormProps) {
    const applyTheme = useSettingsStore(
        (state) => state.applyTheme,
    );

    const [draft, setDraft] =
        useState<Settings>(() =>
            toDraft(settings),
        );

    const result = useMemo(
        () =>
            SettingsSchema.safeParse(
                draft,
            ),
        [draft],
    );

    const dirty = useMemo(
        () =>
            JSON.stringify(draft) !==
            JSON.stringify(settings),
        [draft, settings],
    );

    const invalid =
        !result.success;

    const catalogUrlError = invalid
        ? result.error.issues.find(
              (issue) =>
                  issue.path[0] ===
                  "catalogUrl",
          )?.message
        : undefined;

    const httpsWarning =
        !catalogUrlError &&
        draft.catalogUrl.includes(
            "://",
        ) &&
        !isHttpsUrl(
            draft.catalogUrl,
        );

    function handleSave() {
        if (invalid) {
            return;
        }

        onSave(result.data);
    }

    return (
        <>
            <div className="mb-6 flex items-center justify-between">
                <Dialog.Title className="text-xl font-bold text-foreground">
                    Settings
                </Dialog.Title>

                <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    aria-label="Close settings"
                    onClick={onCancel}
                    className="text-muted-foreground hover:text-foreground"
                >
                    <X />
                </Button>
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <fieldset className="lg:col-span-2">
                    <legend className="mb-2 block text-sm font-semibold text-foreground">
                        Theme
                    </legend>

                    <div className="flex gap-1">
                        {(["dark", "light"] as const).map(
                            (theme) => (
                                <Label
                                    key={theme}
                                    className={cn(
                                        "flex cursor-pointer items-center gap-2 rounded-lg border px-4 py-2 text-sm transition",
                                        draft.theme ===
                                            theme
                                            ? "border-primary bg-accent text-foreground"
                                            : "border-border text-muted-foreground hover:bg-accent/50",
                                    )}
                                >
                                    <input
                                        type="radio"
                                        name="theme"
                                        value={theme}
                                        checked={
                                            draft.theme ===
                                            theme
                                        }
                                        onChange={() => {
                                            applyTheme(
                                                theme,
                                            );

                                            setDraft(
                                                (current) => ({
                                                    ...current,
                                                    theme,
                                                }),
                                            );
                                        }}
                                        className="sr-only"
                                    />

                                    {theme ===
                                    "dark"
                                        ? "Dark"
                                        : "Light"}
                                </Label>
                            ),
                        )}
                    </div>
                </fieldset>

                <div className="space-y-2 lg:col-span-2">
                    <Label htmlFor="settings-catalog-url">
                        Catalog URL
                    </Label>

                    <Input
                        id="settings-catalog-url"
                        type="text"
                        inputMode="url"
                        value={
                            draft.catalogUrl
                        }
                        onChange={(event) =>
                            setDraft(
                                (current) => ({
                                    ...current,
                                    catalogUrl:
                                        event
                                            .target
                                            .value,
                                }),
                            )
                        }
                        aria-invalid={
                            catalogUrlError
                                ? true
                                : undefined
                        }
                        placeholder="/resources"
                    />

                    {catalogUrlError ? (
                        <p className="text-xs text-destructive">
                            {catalogUrlError}
                        </p>
                    ) : httpsWarning ? (
                        <p className="text-xs text-amber-600 dark:text-amber-400">
                            HTTPS is recommended.
                        </p>
                    ) : null}
                </div>

                <fieldset>
                    <legend className="mb-2 block text-sm font-semibold text-foreground">
                        Exercise Repetitions per Line
                    </legend>

                    <div className="flex gap-1">
                        {[5, 10, 20].map(
                            (repetitions) => (
                                <Label
                                    key={
                                        repetitions
                                    }
                                    className={cn(
                                        "flex cursor-pointer items-center rounded-lg border px-4 py-2 text-sm transition",
                                        draft.repetitionsPerLine ===
                                            repetitions
                                            ? "border-primary bg-accent text-foreground"
                                            : "border-border text-muted-foreground hover:bg-accent/50",
                                    )}
                                >
                                    <input
                                        type="radio"
                                        name="repetitions-per-line"
                                        value={
                                            repetitions
                                        }
                                        checked={
                                            draft.repetitionsPerLine ===
                                            repetitions
                                        }
                                        onChange={() =>
                                            setDraft(
                                                (current) => ({
                                                    ...current,
                                                    repetitionsPerLine:
                                                        repetitions,
                                                }),
                                            )
                                        }
                                        className="sr-only"
                                    />

                                    {repetitions}
                                </Label>
                            ),
                        )}
                    </div>
                </fieldset>
            </div>

            <div className="mt-8 flex justify-end gap-2">
                <Button
                    variant="ghost"
                    onClick={onCancel}
                >
                    Cancel
                </Button>

                <Button
                    variant="default"
                    disabled={
                        !dirty || invalid
                    }
                    onClick={handleSave}
                >
                    Save
                </Button>
            </div>
        </>
    );
}

export function SettingsDialog({
    open,
    onOpenChange,
}: SettingsDialogProps) {
    const settings = useSettingsStore(
        (state) => state.settings,
    );

    const update = useSettingsStore(
        (state) => state.update,
    );

    function handleSave(
        next: Settings,
    ) {
        update(next);

        onOpenChange(false);
    }

    return (
        <Dialog.Root
            open={open}
            onOpenChange={onOpenChange}
        >
            <Dialog.Portal>
                <Dialog.Backdrop className="fixed inset-0 z-[80] bg-black/60 backdrop-blur-sm" />

                <Dialog.Popup className="fixed left-1/2 top-1/2 z-[90] max-h-[85vh] w-[min(90vw,28rem)] -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-2xl border border-border bg-background p-6 text-foreground shadow-2xl lg:w-[min(90vw,56rem)] short:p-4">
                    <SettingsForm
                        settings={settings}
                        onSave={handleSave}
                        onCancel={() =>
                            onOpenChange(
                                false,
                            )
                        }
                    />
                </Dialog.Popup>
            </Dialog.Portal>
        </Dialog.Root>
    );
}
