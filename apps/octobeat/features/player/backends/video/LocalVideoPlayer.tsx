"use client";

import { useEffect, useRef } from "react";

import { usePlayerStore } from "@octobeat/player";

interface LocalVideoPlayerProps {
    src: string;
}

export function LocalVideoPlayer({
    src,
}: LocalVideoPlayerProps) {
    const videoRef =
        useRef<HTMLVideoElement>(null);

    const currentTime = usePlayerStore(
        (state) => state.currentTime,
    );

    const playing = usePlayerStore(
        (state) => state.playing,
    );

    useEffect(() => {
        const video = videoRef.current;

        if (!video) {
            return;
        }

        if (playing && video.paused) {
            void video.play().catch(
                console.error,
            );
        }

        if (
            !playing &&
            !video.paused
        ) {
            video.pause();
        }
    }, [playing]);

    useEffect(() => {
        const video = videoRef.current;

        if (!video) {
            return;
        }

        const drift = Math.abs(
            video.currentTime -
            currentTime,
        );

        // Sólo corregimos si existe una desviación apreciable.
        if (drift > 0.03) {
            video.currentTime =
                currentTime;
        }
    }, [currentTime]);

    return (
        <video
            ref={videoRef}
            src={src}
            className="h-full w-full"
            preload="auto"
            muted
            playsInline
        />
    );
}