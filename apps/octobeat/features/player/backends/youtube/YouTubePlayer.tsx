"use client";

import { useEffect, useRef } from "react";

import YouTube, {
    type YouTubeEvent,
} from "react-youtube";

import { YouTubeAdapter } from "./youtubeAdapter";

import { usePlayerStore } from "@octobeat/player";

interface YouTubePlayerProps {
    videoId: string;
}

export function YouTubePlayer({
    videoId,
}: YouTubePlayerProps) {
    const adapterRef =
        useRef<YouTubeAdapter | null>(null);

    const setPlayer = usePlayerStore(
        (state) => state.setPlayer,
    );

    const setDuration = usePlayerStore(
        (state) => state.setDuration,
    );

    const setPlaying = usePlayerStore(
        (state) => state.setPlaying,
    );

    const setCurrentTime = usePlayerStore(
        (state) => state.setCurrentTime,
    );

    useEffect(() => {
        return () => {
            adapterRef.current?.destroy();

            setPlayer(null);
        };
    }, [setPlayer]);

    function handleReady(
        event: YouTubeEvent,
    ) {
        const adapter =
            new YouTubeAdapter(
                event.target,
            );

        adapterRef.current = adapter;

        adapter.on("ready", () => {
            setDuration(
                adapter.duration(),
            );
        });

        adapter.on("play", () => {
            setPlaying(true);
        });

        adapter.on("pause", () => {
            setPlaying(false);
        });

        adapter.on(
            "timeupdate",
            ({ currentTime }) => {
                setCurrentTime(
                    currentTime,
                );
            },
        );

        adapter.on(
            "seek",
            ({ currentTime }) => {
                setCurrentTime(
                    currentTime,
                );
            },
        );

        setPlayer(adapter);

        adapter.ready();
    }

    function handleStateChange(
        event: YouTubeEvent,
    ) {
        adapterRef.current?.stateChanged(
            event,
        );
    }

    return (
        <div className="absolute inset-0">
            <YouTube
                videoId={videoId}
                onReady={handleReady}
                onStateChange={
                    handleStateChange
                }
                className="h-full w-full"
                iframeClassName="h-full w-full"
                opts={{
                    width: "100%",
                    height: "100%",
                    playerVars: {
                        autoplay: 1,
                        mute: 1,
                        controls: 0,
                        rel: 0,
                        modestbranding: 1,
                        playsinline: 1,
                    },
                }}
            />
        </div>
    );
}