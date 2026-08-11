"use client";

import { useLibraryStore } from "@/features/library/store";

import { LocalAudioPlayer } from "./audio";
import { LocalVideoPlayer } from "./video";
import { WaveformPlayer } from "./waveform";
import { YouTubePlayer } from "./youtube/YouTubePlayer";

export function PlayerBackend() {
    const dataset = useLibraryStore(
        (state) => state.dataset,
    );

    if (!dataset) {
        return null;
    }

    const {
        resources,
        youtube,
        id,
    } = dataset.metadata;

    if (resources.video) {
        return (
            <>
                <LocalVideoPlayer
                    key={`video-${id}`}
                    src={resources.video}
                />

                <LocalAudioPlayer
                    key={`audio-${id}`}
                    src={resources.audio}
                />
            </>
        );
    }

    if (youtube) {
        return (
            <YouTubePlayer
                key={`youtube-${id}`}
                videoId={youtube}
            />
        );
    }

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