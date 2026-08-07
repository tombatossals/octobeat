import type {
    MediaPlayer,
    MediaPlayerEvent,
    MediaPlayerEventMap,
    MediaPlayerListener,
    MediaPlayerOptions,
} from "@octobeat/player";

import type {
    YouTubeEvent,
    YouTubePlayer,
} from "react-youtube";

const PLAYER_STATE = {
    UNSTARTED: -1,
    ENDED: 0,
    PLAYING: 1,
    PAUSED: 2,
    BUFFERING: 3,
    CUED: 5,
} as const;

export class YouTubeAdapter
    implements MediaPlayer {

    private timer: number | null = null;

    private readonly listeners: {
        [K in MediaPlayerEvent]: Set<MediaPlayerListener<K>>;
    } = {
            ready: new Set(),
            play: new Set(),
            pause: new Set(),
            seek: new Set(),
            timeupdate: new Set(),
        };

    constructor(
        private readonly player: YouTubePlayer,
    ) { }

    //
    // React callbacks
    //

    ready(): void {
        this.player.setVolume(100);
        this.player.unMute();

        this.emit("ready");
    }

    stateChanged(
        event: YouTubeEvent,
    ): void {
        switch (event.data) {
            case PLAYER_STATE.PLAYING:
                this.startTimer();

                this.emit("play");

                break;

            case PLAYER_STATE.PAUSED:
                this.stopTimer();

                this.emit("pause");

                break;

            case PLAYER_STATE.ENDED:
                this.stopTimer();

                this.emit("pause");

                this.emit("seek", {
                    currentTime: 0,
                });

                break;
        }
    }

    //
    // MediaPlayer
    //

    async playPause(): Promise<void> {
        if (this.isPlaying()) {
            this.player.pauseVideo();
        } else {
            this.player.playVideo();
        }
    }

    stop(): void {
        this.player.stopVideo();

        this.stopTimer();

        this.emit("pause");

        this.emit("seek", {
            currentTime: 0,
        });
    }

    seek(
        time: number,
    ): void {
        this.player.seekTo(
            time,
            true,
        );

        this.emit("seek", {
            currentTime: time,
        });
    }

    currentTime(): number {
        return this.player.getCurrentTime();
    }

    duration(): number {
        return this.player.getDuration();
    }

    isPlaying(): boolean {
        return (
            this.player.getPlayerState() ===
            PLAYER_STATE.PLAYING
        );
    }

    on<K extends MediaPlayerEvent>(
        event: K,
        callback: MediaPlayerListener<K>,
    ): () => void {
        const listeners = this.listeners[event];

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

    zoom(
        _pixelsPerSecond: number,
    ): void {
        // Not applicable.
    }

    destroy(): void {
        this.stopTimer();

        this.player.destroy();
    }

    //
    // Internals
    //

    private emit<K extends MediaPlayerEvent>(
        event: K,
        payload?: MediaPlayerEventMap[K],
    ): void {
        const listeners = this.listeners[event] as Set<
            MediaPlayerListener<K>
        >;

        for (const listener of listeners) {
            listener(payload as MediaPlayerEventMap[K]);
        }
    }

    private startTimer(): void {
        this.stopTimer();

        this.timer = window.setInterval(() => {
            this.emit("timeupdate", {
                currentTime: this.currentTime(),
            });
        }, 50);
    }

    private stopTimer(): void {
        if (this.timer !== null) {
            window.clearInterval(this.timer);

            this.timer = null;
        }
    }
}