"use client";

import { useEffect } from "react";

import { useSettingsStore } from "../store";

/**
 * Sincroniza el tema seleccionado con la clase `dark` del elemento
 * `<html>`.
 */
export function useTheme(): void {
    const theme = useSettingsStore(
        (state) =>
            state.settings.theme,
    );

    useEffect(() => {
        const root =
            document.documentElement;

        root.classList.toggle(
            "dark",
            theme === "dark",
        );
    }, [theme]);
}
