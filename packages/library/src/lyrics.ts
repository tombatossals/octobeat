import { z } from "zod";

/**
 * Synced lyrics dataset resource (`lyrics.json`).
 *
 * A top-level array of lyric lines, each optionally carrying
 * per-syllable timestamps for karaoke-style highlighting.
 */
export const LyricSyllableSchema = z.object({
    text: z.string(),

    startTime: z.number(),
});

export const LyricLineSchema = z.object({
    index: z.number().int(),

    text: z.string(),

    startTime: z.number(),

    endTime: z
        .number()
        .optional(),

    syllables: z
        .array(LyricSyllableSchema)
        .optional(),
});

export type LyricSyllable = z.infer<
    typeof LyricSyllableSchema
>;

export type LyricLine = z.infer<typeof LyricLineSchema>;

export const LyricsSchema = z.array(LyricLineSchema);

export function parseLyrics(
    json: unknown,
): LyricLine[] {
    return LyricsSchema.parse(json);
}
