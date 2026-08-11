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

export const TempoSegmentSchema = z.object({
    time: z.number(),
    bpm: z.number(),
});

export const TimingSchema = z.object({
    bpm: z.number(),

    offset: z.number(),

    timeSignature: z.string(),

    confidence: z.number(),

    tempoMap: z
        .array(TempoSegmentSchema)
        .optional(),

    source: z
        .string()
        .optional(),

    countInStart: z
        .number()
        .optional(),

    songStart: z
        .number()
        .optional(),

    countInClicks: z
        .array(z.number())
        .optional(),
});

export const SectionSchema = z.object({
    index: z.number().int(),

    name: z.string(),

    startBeat: z.number().int(),

    startTime: z.number(),

    sourceName: z
        .string()
        .optional(),
});

export const SourceSchema = z.object({
    type: z.string(),
    id: z.string(),
});

export const SongMetadataSchema = z.object({
    title: z.string(),

    duration: z.number(),

    source: SourceSchema,
});

export const SongMapSchema = z.object({
    version: z.literal(1),

    schema: z.literal("songmap/v1"),

    generatedBy: z.string(),

    createdAt: z.string(),

    metadata: SongMetadataSchema,

    timing: TimingSchema,

    beats: z.array(BeatSchema),

    bars: z.array(BarSchema),

    lyrics: z
        .array(LyricLineSchema)
        .optional(),

    sections: z
        .array(SectionSchema)
        .optional(),
});

export type Beat = z.infer<typeof BeatSchema>;

export type Bar = z.infer<typeof BarSchema>;

export type LyricLine = z.infer<
    typeof LyricLineSchema
>;

export type TempoSegment = z.infer<
    typeof TempoSegmentSchema
>;

export type Timing = z.infer<typeof TimingSchema>;

export type Section = z.infer<typeof SectionSchema>;

export type SongMap = z.infer<typeof SongMapSchema>;

export function parseSongMap(
    json: unknown,
): SongMap {
    return SongMapSchema.parse(json);
}