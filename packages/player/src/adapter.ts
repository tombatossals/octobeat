export interface MediaPlayerOptions {
    waveColor?: string;
    progressColor?: string;
    cursorColor?: string;
    height?: number | "auto";
}

export type EmptyEvent = void;

export interface PlaybackPositionEvent {
    currentTime: number;
}

export interface MediaPlayerEventMap {
    ready: EmptyEvent;
    play: EmptyEvent;
    pause: EmptyEvent;

    timeupdate: PlaybackPositionEvent;
    seek: PlaybackPositionEvent;
}

export type MediaPlayerEvent = keyof MediaPlayerEventMap;

export type MediaPlayerListener<
    K extends MediaPlayerEvent,
> = (
    event: MediaPlayerEventMap[K],
) => void;

export interface MediaPlayer {
    /**
     * Start/Pause playback.
     */
    playPause(): Promise<void>;

    /**
     * Stop playback and seek to the beginning.
     */
    stop(): void;

    /**
     * Seek to an absolute position (seconds).
     */
    seek(time: number): void;

    /**
     * Set the waveform zoom level.
     */
    zoom(pixelsPerSecond: number): void;

    /**
     * Current playback position.
     */
    currentTime(): number;

    /**
     * Recording duration.
     */
    duration(): number;

    /**
     * Whether playback is active.
     */
    isPlaying(): boolean;

    /**
     * Subscribe to player events.
     */
    on<K extends MediaPlayerEvent>(
        event: K,
        callback: MediaPlayerListener<K>,
    ): () => void;

    /**
     * Update appearance.
     */
    updateColors(
        options: MediaPlayerOptions,
    ): void;

    /**
     * Dispose resources.
     */
    destroy(): void;
}