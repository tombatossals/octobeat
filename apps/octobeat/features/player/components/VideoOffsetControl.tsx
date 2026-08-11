"use client";

import { useEffect, useState } from "react";
import {
    Check,
    Minus,
    Plus,
    RotateCcw,
    Video,
} from "lucide-react";

import { usePlayerStore } from "@octobeat/player";

import { useLibraryStore } from "@/features/library/store";

import {
    clearManualOffset,
    readManualOffsets,
    saveManualOffset,
} from "../videoOffsetStorage";

const STEP_SECONDS = 0.01;

export function VideoOffsetControl() {
    const dataset = useLibraryStore(
        (state) => state.dataset,
    );

    const videoOffset = usePlayerStore(
        (state) => state.videoOffset,
    );

    const setVideoOffset = usePlayerStore(
        (state) => state.setVideoOffset,
    );

    const [saved, setSaved] =
        useState(false);

    useEffect(() => {
        if (!saved) {
            return;
        }

        const timer = window.setTimeout(
            () => setSaved(false),
            1200,
        );

        return () => {
            window.clearTimeout(timer);
        };
    }, [saved]);

    // The synced offset from the SongMap (for reference / reset).
    const songOffset =
        dataset?.songmap.media?.video
            ?.offset ?? 0;

    const hasVideo = Boolean(
        dataset?.songmap.media?.video,
    );

    const manualOffsets =
        readManualOffsets();

    const isManual = dataset
        ? Boolean(
              manualOffsets[
                  dataset.metadata.id
              ],
          )
        : false;

    if (!dataset || !hasVideo) {
        return null;
    }

    const datasetId =
        dataset.metadata.id;

    function adjust(delta: number) {
        // The offset may be negative when the recording starts with a
        // count-in the video does not have.
        const next = Math.min(
            120,
            Math.max(-120, videoOffset + delta),
        );

        setVideoOffset(next);
    }

    function save() {
        saveManualOffset(
            datasetId,
            videoOffset,
        );

        setSaved(true);
    }

    function reset() {
        clearManualOffset(datasetId);

        setVideoOffset(songOffset);
    }

    return (
        <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-gray-800/60 px-3 py-2 text-white shadow-2xl backdrop-blur-md">
            <Video className="h-4 w-4 text-white/70" />

            <div className="flex flex-col leading-tight">
                <span className="text-[10px] uppercase tracking-wide text-white/50">
                    Video offset
                    {isManual && (
                        <span className="ml-1 text-amber-300">
                            · manual
                        </span>
                    )}
                </span>

                <span className="text-sm font-semibold tabular-nums">
                    {videoOffset.toFixed(2)} s
                </span>
            </div>

            <div className="flex items-center gap-1">
                <button
                    type="button"
                    aria-label="Offset -10 ms"
                    onClick={() =>
                        adjust(-STEP_SECONDS)
                    }
                    className="flex h-7 w-7 items-center justify-center rounded-md bg-white/10 transition-colors hover:bg-white/20"
                >
                    <Minus className="h-3.5 w-3.5" />
                </button>

                <button
                    type="button"
                    aria-label="Offset +10 ms"
                    onClick={() =>
                        adjust(STEP_SECONDS)
                    }
                    className="flex h-7 w-7 items-center justify-center rounded-md bg-white/10 transition-colors hover:bg-white/20"
                >
                    <Plus className="h-3.5 w-3.5" />
                </button>
            </div>

            <div className="flex items-center gap-1">
                <button
                    type="button"
                    aria-label="Reset offset"
                    onClick={reset}
                    className="flex h-7 w-7 items-center justify-center rounded-md bg-white/10 transition-colors hover:bg-white/20"
                >
                    <RotateCcw className="h-3.5 w-3.5" />
                </button>

                <button
                    type="button"
                    onClick={save}
                    className="flex h-7 items-center gap-1 rounded-md bg-emerald-500/80 px-2 text-xs font-medium text-white transition-colors hover:bg-emerald-500"
                >
                    <Check className="h-3.5 w-3.5" />
                    {saved ? "Saved" : "Save"}
                </button>
            </div>
        </div>
    );
}
