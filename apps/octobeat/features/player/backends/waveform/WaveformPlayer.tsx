"use client";

import { useEffect, useRef, useState } from "react";

import { usePlayerStore } from "@octobeat/player";
import type { Section } from "@octobeat/songmap";

// Número de columnas del waveform (independiente de la resolución de
// pantalla; a resolución alta se dibujan más anchas).
const PEAK_BINS = 360;

// Paleta para las secciones de la canción (estructura).
const SECTION_COLORS = [
    {
        fill: "rgba(96, 165, 250, 0.10)",
        text: "rgba(147, 197, 253, 0.85)",
    },
    {
        fill: "rgba(167, 139, 250, 0.10)",
        text: "rgba(196, 181, 253, 0.85)",
    },
    {
        fill: "rgba(45, 212, 191, 0.08)",
        text: "rgba(94, 234, 212, 0.85)",
    },
    {
        fill: "rgba(251, 191, 36, 0.08)",
        text: "rgba(252, 211, 77, 0.85)",
    },
    {
        fill: "rgba(248, 113, 113, 0.08)",
        text: "rgba(252, 165, 165, 0.85)",
    },
    {
        fill: "rgba(74, 222, 128, 0.08)",
        text: "rgba(134, 239, 172, 0.85)",
    },
];

// AudioContext compartido: decodificar no requiere gesto del usuario,
// y se reutiliza para no agotar el límite de contextos del navegador.
let audioContext: AudioContext | null =
    null;

function sharedAudioContext(): AudioContext {
    audioContext ??=
        new AudioContext();
    return audioContext;
}

// Cache de picos por URL para no re-decodificar al cambiar de dataset.
const peaksCache = new Map<
    string,
    Promise<number[]>
>();

async function computePeaks(
    src: string,
): Promise<number[]> {
    const cached =
        peaksCache.get(src);

    if (cached) {
        return cached;
    }

    const task = (async () => {
        const response =
            await fetch(src);

        if (!response.ok) {
            throw new Error(
                `Failed to fetch audio: ${response.status}`,
            );
        }

        const buffer =
            await response.arrayBuffer();

        const decoded =
            await sharedAudioContext().decodeAudioData(
                buffer,
            );

        const channel =
            decoded.getChannelData(0);

        const peaks = new Array<number>(
            PEAK_BINS,
        ).fill(0);

        const perBin = Math.floor(
            channel.length /
                PEAK_BINS,
        );

        for (
            let bin = 0;
            bin < PEAK_BINS;
            bin++
        ) {
            let max = 0;
            const start =
                bin * perBin;
            const end = Math.min(
                channel.length,
                start + perBin,
            );

            for (
                let index = start;
                index < end;
                index++
            ) {
                const value = Math.abs(
                    channel[index]!,
                );

                if (
                    value > max
                ) {
                    max = value;
                }
            }

            peaks[bin] = max;
        }

        const peakMax =
            Math.max(...peaks, 1e-6);

        return peaks.map(
            (peak) =>
                peak / peakMax,
        );
    })();

    peaksCache.set(src, task);

    return task;
}

interface WaveformPlayerProps {
    src: string;

    /**
     * Secciones de la canción (estructura) que se dibujan sobre el
     * waveform durante toda la reproducción.
     */
    sections?: readonly Section[];
}

interface Peaks {
    src: string;
    values: number[];
}

export function WaveformPlayer({
    src,
    sections: sectionsProp,
}: WaveformPlayerProps) {
    const canvasRef =
        useRef<HTMLCanvasElement>(null);

    const [peaks, setPeaks] =
        useState<Peaks | null>(
            null,
        );

    useEffect(() => {
        let cancelled = false;

        computePeaks(src)
            .then((values) => {
                if (!cancelled) {
                    setPeaks({
                        src,
                        values,
                    });
                }
            })
            .catch(() => {
                // Sin waveform: la zona queda en negro.
            });

        return () => {
            cancelled = true;
        };
    }, [src]);

    useEffect(() => {
        const canvas =
            canvasRef.current;

        if (!canvas) {
            return;
        }

        const context =
            canvas.getContext("2d");

        if (!context) {
            return;
        }

        const canvasEl = canvas;
        const ctx = context;

        const values =
            peaks?.src === src
                ? peaks.values
                : null;

        let frame = 0;

        let anchorMedia = 0;
        let anchorPerf =
            performance.now();

        function resize() {
            const { clientWidth, clientHeight } =
                canvasEl;

            const dpr =
                window.devicePixelRatio ||
                1;

            canvasEl.width =
                Math.max(
                    1,
                    Math.round(
                        clientWidth * dpr,
                    ),
                );

            canvasEl.height =
                Math.max(
                    1,
                    Math.round(
                        clientHeight * dpr,
                    ),
                );

            ctx.setTransform(
                dpr,
                0,
                0,
                dpr,
                0,
                0,
            );
        }

        function draw() {
            // Usamos el tamaño CSS (clientWidth/Height) para el layout:
            // el transform de `resize` ya escala a píxeles físicos, así
            // que usar canvas.width (backing store) desbordaría en
            // pantallas con devicePixelRatio > 1.
            const {
                clientWidth: width,
                clientHeight: height,
            } = canvasEl;

            ctx.clearRect(
                0,
                0,
                width,
                height,
            );

            const store =
                usePlayerStore.getState();

            const now =
                performance.now();

            if (
                store.currentTime !==
                anchorMedia
            ) {
                anchorMedia =
                    store.currentTime;
                anchorPerf = now;
            }

            const smoothTime =
                store.playing
                    ? anchorMedia +
                      (now -
                          anchorPerf) /
                          1000
                    : store.currentTime;

            const duration =
                store.duration;

            const progress =
                duration > 0
                    ? Math.min(
                          1,
                          Math.max(
                              0,
                              smoothTime /
                                  duration,
                          ),
                      )
                    : 0;

            // Márgenes laterales coherentes con el resto de la página
            // (elementos fijos a 1rem de los bordes).
            const margin = 24;

            const bandHeight =
                height * 0.24;

            const midY =
                height * 0.5;

            const plotWidth =
                width -
                margin * 2;

            const playX =
                margin +
                progress * plotWidth;

            const sections =
                sectionsProp ?? [];

            // Estructura de la canción: regiones por sección con su
            // nombre, siempre visibles durante toda la canción.
            for (
                let index = 0;
                index <
                sections.length;
                index++
            ) {
                const section =
                    sections[index]!;

                const start =
                    duration > 0
                        ? section.startTime /
                          duration
                        : 0;

                const end =
                    duration > 0 &&
                    index + 1 <
                        sections.length
                        ? sections[
                              index + 1
                          ]!.startTime /
                          duration
                        : 1;

                if (
                    start >= 1 ||
                    end <= 0
                ) {
                    continue;
                }

                const x0 =
                    margin +
                    Math.max(0, start) *
                        plotWidth;

                const x1 =
                    margin +
                    Math.max(0, end) *
                        plotWidth;

                const palette =
                    SECTION_COLORS[
                        index %
                            SECTION_COLORS.length
                    ]!;

                ctx.fillStyle =
                    palette.fill;

                ctx.fillRect(
                    x0,
                    0,
                    Math.max(
                        0,
                        x1 - x0,
                    ),
                    height,
                );

                if (
                    x1 - x0 > 56
                ) {
                    ctx.fillStyle =
                        palette.text;
                    ctx.font =
                        "600 12px ui-sans-serif, system-ui, sans-serif";
                    ctx.textAlign =
                        "center";
                    ctx.textBaseline =
                        "bottom";
                    ctx.fillText(
                        section.name,
                        (x0 + x1) /
                            2,
                        midY -
                            bandHeight /
                                2 -
                            height *
                                0.015,
                    );
                }
            }

            if (!values) {
                frame =
                    requestAnimationFrame(
                        draw,
                    );

                return;
            }

            const barWidth =
                plotWidth /
                values.length;

            const gap = Math.max(
                1,
                barWidth * 0.2,
            );

            const barW = Math.max(
                1,
                barWidth - gap,
            );

            for (
                let index = 0;
                index <
                values.length;
                index++
            ) {
                const value =
                    values[index]!;

                const barH = Math.max(
                    2,
                    value * bandHeight,
                );

                const x =
                    margin +
                    index * barWidth;

                const played =
                    x + barW <=
                    playX;

                ctx.fillStyle = played
                    ? "rgba(96, 165, 250, 0.85)"
                    : "rgba(148, 163, 184, 0.22)";

                ctx.fillRect(
                    x,
                    midY - barH / 2,
                    barW,
                    barH,
                );
            }

            // Playhead.
            ctx.save();

            ctx.shadowColor =
                "rgba(59, 130, 246, 0.9)";
            ctx.shadowBlur = 12;
            ctx.fillStyle =
                "rgba(147, 197, 253, 0.95)";
            ctx.fillRect(
                playX - 1,
                midY -
                    bandHeight / 2 -
                    height * 0.04,
                2,
                bandHeight +
                    height * 0.08,
            );

            ctx.restore();

            frame =
                requestAnimationFrame(
                    draw,
                );
        }

        resize();

        const observer =
            new ResizeObserver(
                resize,
            );

        observer.observe(canvasEl);

        frame =
            requestAnimationFrame(
                draw,
            );

        return () => {
            cancelAnimationFrame(
                frame,
            );

            observer.disconnect();
        };
    }, [peaks, sectionsProp, src]);

    return (
        <canvas
            ref={canvasRef}
            className="absolute inset-0 h-full w-full"
        />
    );
}
