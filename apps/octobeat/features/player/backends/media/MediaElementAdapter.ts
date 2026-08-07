import type {
    MediaPlayer,
    MediaPlayerEvent,
    MediaPlayerEventMap,
    MediaPlayerListener,
    MediaPlayerOptions,
} from "@octobeat/player";

export class MediaElementAdapter
    implements MediaPlayer {
    private readonly listeners: {
        [K in MediaPlayerEvent]: Set<
            MediaPlayerListener<K>
        >;
    } = {
            ready: new Set(),
            play: new Set(),
            pause: new Set(),
            ended: new Set(),
            seek: new Set(),
            timeupdate: new Set(),
        };

    constructor(
        private readonly media: HTMLMediaElement,
    ) {
        media.addEventListener(
            "loadedmetadata",
            this.handleReady,
        );

        media.addEventListener(
            "play",
            this.handlePlay,
        );

        media.addEventListener(
            "pause",
            this.handlePause,
        );

        media.addEventListener(
            "timeupdate",
            this.handleTimeUpdate,
        );

        media.addEventListener(
            "seeked",
            this.handleSeek,
        );

        media.addEventListener(
            "ended",
            this.handleEnded,
        );
    }

    ready(): void {
        this.emit("ready");
    }

    async playPause(): Promise<void> {
        if (this.media.paused) {
            await this.media.play();
        } else {
            this.media.pause();
        }
    }

    stop(): void {
        this.media.pause();
        this.media.currentTime = 0;
    }

    seek(
        time: number,
    ): void {
        this.media.currentTime = time;
    }

    zoom(
        _pixelsPerSecond: number,
    ): void {
        // Not applicable.
    }

    currentTime(): number {
        return this.media.currentTime;
    }

    duration(): number {
        return this.media.duration;
    }

    isPlaying(): boolean {
        return !this.media.paused;
    }

    on<K extends MediaPlayerEvent>(
        event: K,
        callback: MediaPlayerListener<K>,
    ): () => void {
        const listeners =
            this.listeners[event];

        listeners.add(callback);

        return () => {
            listeners.delete(callback);
        };
    }

    updateColors(
        _options: MediaPlayerOptions,
    ): void {
        // Not applicable.
    }

    destroy(): void {
        this.media.removeEventListener(
            "loadedmetadata",
            this.handleReady,
        );

        this.media.removeEventListener(
            "play",
            this.handlePlay,
        );

        this.media.removeEventListener(
            "pause",
            this.handlePause,
        );

        this.media.removeEventListener(
            "timeupdate",
            this.handleTimeUpdate,
        );

        this.media.removeEventListener(
            "seeked",
            this.handleSeek,
        );

        this.media.removeEventListener(
            "ended",
            this.handleEnded,
        );
    }

    //
    // Events
    //

    private handleReady = (): void => {
        this.emit("ready");
    };

    private handlePlay = (): void => {
        this.emit("play");
    };

    private handlePause = (): void => {
        this.emit("pause");
    };

    private handleTimeUpdate = (): void => {
        this.emit("timeupdate", {
            currentTime:
                this.media.currentTime,
        });
    };

    private handleSeek = (): void => {
        this.emit("seek", {
            currentTime:
                this.media.currentTime,
        });
    };

    private handleEnded = (): void => {
        this.emit("ended");

        this.emit("pause");

        this.emit("seek", {
            currentTime: 0,
        });
    };

    //
    // Internals
    //

    private emit<K extends MediaPlayerEvent>(
        event: K,
        payload?: MediaPlayerEventMap[K],
    ): void {
        const listeners =
            this.listeners[event] as Set<
                MediaPlayerListener<K>
            >;

        for (const listener of listeners) {
            listener(
                payload as MediaPlayerEventMap[K],
            );
        }
    }
}