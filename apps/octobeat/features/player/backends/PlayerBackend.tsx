"use client";

import { useLibraryStore } from "@/features/library/store";

import { LocalAudioPlayer } from "./audio";
import { WaveformPlayer } from "./waveform";

export function PlayerBackend() {
    const dataset = useLibraryStore(
        (state) => state.dataset,
    );

    if (!dataset) {
        return null;
    }

    const { resources, id } =
        dataset.metadata;

    return (
        <>
            <WaveformPlayer
                key={`waveform-${id}`}
                src={resources.audio}
                sections={
                    dataset.songmap
                        .sections
                }
            />

            <LocalAudioPlayer
                key={`audio-${id}`}
                src={resources.audio}
            />
        </>
    );
}
