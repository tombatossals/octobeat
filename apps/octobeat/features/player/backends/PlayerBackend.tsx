"use client";

import { useLibraryStore } from "@/features/library/store";

import { LocalAudioPlayer } from "./audio";
import { WaveformPlayer } from "./waveform";

export function PlayerBackend() {
    const dataset = useLibraryStore(
        (state) => state.dataset,
    );

    const revision = useLibraryStore(
        (state) => state.revision,
    );

    if (!dataset) {
        return null;
    }

    const { resources, id } =
        dataset.metadata;

    return (
        <>
            <WaveformPlayer
                key={`waveform-${id}-${revision}`}
                src={resources.audio}
                sections={
                    dataset.songmap
                        .sections
                }
            />

            <LocalAudioPlayer
                key={`audio-${id}-${revision}`}
                src={resources.audio}
            />
        </>
    );
}
