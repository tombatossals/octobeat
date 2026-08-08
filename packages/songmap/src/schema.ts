import { z } from "zod";

export const BeatSchema = z.object({
    index: z.number().int(),
    time: z.number(),
});

export const BarSchema = z.object({
    index: z.number().int(),
    firstBeat: z.number().int(),
});

export const LyricLineSchema = z.object({
    time: z.number(),
    text: z.string(),
});

export const TimingSchema = z.object({
    bpm: z.number(),

    offset: z.number(),

    timeSignature: z.string(),

    confidence: z.number(),
});

export const SongMapSchema = z.object({
    version: z.literal(1),

    schema: z.literal("songmap/v1"),

    generatedBy: z.string(),

    createdAt: z.string(),

    timing: TimingSchema,

    beats: z.array(BeatSchema),

    bars: z.array(BarSchema),

    lyrics: z
        .array(LyricLineSchema)
        .optional(),
});

export type Beat = z.infer<typeof BeatSchema>;

export type Bar = z.infer<typeof BarSchema>;

export type LyricLine = z.infer<
    typeof LyricLineSchema
>;

export type Timing = z.infer<typeof TimingSchema>;

export type SongMap = z.infer<typeof SongMapSchema>;

export function parseSongMap(
    json: unknown,
): SongMap {
    return SongMapSchema.parse(json);
}