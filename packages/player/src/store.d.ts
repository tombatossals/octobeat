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
export declare const usePlayerStore: import("zustand").UseBoundStore<import("zustand").StoreApi<PlayerStore>>;
export {};
