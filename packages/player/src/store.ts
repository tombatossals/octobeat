import { create } from "zustand";

import type { MediaPlayer } from "./adapter";

interface PlayerStore {
    /**
     * Current audio player instance.
     */
    player: MediaPlayer | null;

    /**
     * Whether playback has been started by the user.
     */
    started: boolean;

    /**
     * Playback state.
     */
    playing: boolean;

    /**
     * Current playback position (seconds) — always **song time**.
     */
    currentTime: number;

    /**
     * Recording duration (seconds).
     */
    duration: number;

    /**
     * Volume level (0..1).
     */
    volume: number;

    /**
     * Register the active player.
     */
    setPlayer(player: MediaPlayer | null): void;

    /**
     * Update the volume level.
     */
    setVolume(volume: number): void;

    /**
     * Update whether playback has started.
     */
    setStarted(started: boolean): void;

    /**
     * Update playback state.
     */
    setPlaying(playing: boolean): void;

    /**
     * Update the current playback time.
     */
    setCurrentTime(time: number): void;

    /**
     * Update the recording duration.
     */
    setDuration(duration: number): void;

    /**
     * Transport controls.
     */
    playPause(): Promise<void>;

    stop(): void;

    seek(time: number): void;
}

export const usePlayerStore = create<PlayerStore>((set, get) => ({
    player: null,

    started: false,

    playing: false,

    currentTime: 0,

    duration: 0,

    volume: 1,

    setPlayer(player) {
        set({
            player,
        });

        if (player) {
            player.setVolume(
                get().volume,
            );
        }
    },

    setVolume(volume) {
        const clamped =
            Math.max(0, Math.min(1, volume));

        set({
            volume: clamped,
        });

        get().player?.setVolume(
            clamped,
        );
    },

    setStarted(started) {
        set({
            started,
        });
    },

    setPlaying(playing) {
        set({
            playing,
        });
    },

    setCurrentTime(currentTime) {
        set({
            currentTime,
        });
    },

    setDuration(duration) {
        set({
            duration,
        });
    },

    async playPause() {
        const player = get().player;

        if (!player) {
            return;
        }

        await player.playPause();
    },

    stop() {
        const player = get().player;

        if (!player) {
            return;
        }

        player.stop();

        set({
            playing: false,
            currentTime: 0,
        });
    },

    seek(time) {
        const player = get().player;

        if (!player) {
            return;
        }

        player.seek(time);

        set({
            currentTime: time,
        });
    },
}));