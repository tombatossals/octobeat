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

    const videoOffset = usePlayerStore(
        (state) => state.videoOffset,
    );

    const playing = usePlayerStore(
        (state) => state.playing,
    );

    // The store time is always song time; the video element advances in
    // video time.
    const videoTime =
        currentTime + videoOffset;

    // Position the video at the correct video time once its metadata is
    // available (handles switching datasets and videos with an intro).
    useEffect(() => {
        const video = videoRef.current;

        if (!video) {
            return;
        }

        const handleLoadedMetadata = () => {
            const drift = Math.abs(
                video.currentTime -
                videoTime,
            );

            if (drift > 0.03) {
                video.currentTime =
                    videoTime;
            }
        };

        video.addEventListener(
            "loadedmetadata",
            handleLoadedMetadata,
        );

        return () => {
            video.removeEventListener(
                "loadedmetadata",
                handleLoadedMetadata,
            );
        };
    }, [videoTime]);

    // Re-sync after the source changes (new dataset) so the video does
    // not keep a stale position or show a black frame: reload the
    // element and position it at the correct video time once ready.
    useEffect(() => {
        const video = videoRef.current;

        if (!video) {
            return;
        }

        video.load();

        const sync = () => {
            video.currentTime =
                videoTime;
        };

        video.addEventListener(
            "loadedmetadata",
            sync,
            { once: true },
        );

        return () => {
            video.removeEventListener(
                "loadedmetadata",
                sync,
            );
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [src]);

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
            videoTime,
        );

        // Sólo corregimos si existe una desviación apreciable.
        if (drift > 0.03) {
            video.currentTime =
                videoTime;
        }
    }, [videoTime]);

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