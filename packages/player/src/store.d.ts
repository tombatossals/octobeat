import type { MediaPlayer } from "./adapter";
interface PlayerStore {
    /**
     * Current audio player instance.
     */
    player: MediaPlayer | null;
    /**
     * Playback state.
     */
    playing: boolean;
    /**
     * Current playback position (seconds).
     */
    currentTime: number;
    /**
     * Recording duration (seconds).
     */
    duration: number;
    /**
     * Register the active player.
     */
    setPlayer(player: MediaPlayer | null): void;
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
