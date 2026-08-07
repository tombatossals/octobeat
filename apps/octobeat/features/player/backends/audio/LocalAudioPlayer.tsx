"use client";

import { useCallback, useEffect, useRef } from "react";

import { usePlayerStore } from "@octobeat/player";

import { MediaElementAdapter } from "../media";

interface LocalAudioPlayerProps {
    src: string;
}

export function LocalAudioPlayer({
    src,
}: LocalAudioPlayerProps) {
    const audioRef =
        useRef<HTMLAudioElement>(null);

    const setPlayer = usePlayerStore(
        (state) => state.setPlayer,
    );

    const setDuration = usePlayerStore(
        (state) => state.setDuration,
    );

    const setPlaying = usePlayerStore(
        (state) => state.setPlaying,
    );

    const setCurrentTime =
        usePlayerStore(
            (state) =>
                state.setCurrentTime,
        );

    const playAudio = useCallback(() => {
        const audio =
            audioRef.current;

        if (!audio) {
            return;
        }

        void audio.play().catch(() => {
            // El navegador puede bloquear el autoplay hasta que el
            // usuario interactúe; reintentamos con el primer gesto.
            const unlock =
                () => {
                    window.removeEventListener(
                        "keydown",
                        unlock,
                    );
                    window.removeEventListener(
                        "pointerdown",
                        unlock,
                    );

                    void audio.play().catch(
                        console.error,
                    );
                };

            window.addEventListener(
                "keydown",
                unlock,
            );
            window.addEventListener(
                "pointerdown",
                unlock,
            );
        });
    }, []);

    useEffect(() => {
        const audio =
            audioRef.current;

        if (!audio) {
            return;
        }

        const adapter =
            new MediaElementAdapter(
                audio,
            );

        adapter.on("ready", () => {
            setDuration(
                adapter.duration(),
            );

            void playAudio();
        });

        adapter.on("play", () => {
            setPlaying(true);
        });

        adapter.on("pause", () => {
            setPlaying(false);
        });

        adapter.on(
            "timeupdate",
            ({ currentTime }) =>
                setCurrentTime(
                    currentTime,
                ),
        );

        adapter.on(
            "seek",
            ({ currentTime }) =>
                setCurrentTime(
                    currentTime,
                ),
        );

        setPlayer(adapter);

        adapter.ready();

        return () => {
            adapter.destroy();

            setPlayer(null);
        };
    }, [
        setCurrentTime,
        setDuration,
        setPlayer,
        setPlaying,
        playAudio,
    ]);

    return (
        <audio
            ref={audioRef}
            src={src}
            preload="auto"
            playsInline
        />
    );
}