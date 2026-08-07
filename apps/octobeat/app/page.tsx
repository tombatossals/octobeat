"use client";

import { useEffect } from "react";

import { useLibraryStore } from "@/features/library/store";
import { useSettingsStore } from "@/features/settings/store";

import { Player } from "@/features/player/components/Player";

export default function HomePage() {
  const initialize = useLibraryStore(
    (state) => state.initialize,
  );

  const open = useLibraryStore(
    (state) => state.open,
  );

  useEffect(() => {
    async function setup() {
      useSettingsStore
        .getState()
        .load();

      const ids = await initialize();

      if (ids.length === 0) {
        return;
      }

      await open(ids[0]);
    }

    void setup();
  }, [initialize, open]);

  return <Player />;
}