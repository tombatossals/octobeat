import { z } from "zod";

export const ResourcesSchema = z.object({
    audio: z.string(),

    video: z
        .string()
        .optional(),
});

export const TimingProvenanceSchema =
    z.object({
        source: z.string(),

        confidence: z.number(),
    });

export const MetadataSchema =
    z.object({
        id: z.string(),

        title: z.string(),

        artist: z.string(),

        album: z
            .string()
            .optional(),

        year: z
            .number()
            .int()
            .optional(),

        genres: z.array(
            z.string(),
        ),

        bpm: z.number(),

        duration: z.number(),

        difficulty: z
            .number()
            .int()
            .optional(),

        tags: z.array(
            z.string(),
        ),

        timeSignature: z
            .string()
            .optional(),

        timing: TimingProvenanceSchema
            .optional(),

        youtube: z
            .string()
            .optional(),

        resources:
            ResourcesSchema,
    });

export type Metadata =
    z.infer<
        typeof MetadataSchema
    >;

export function parseMetadata(
    json: unknown,
): Metadata {
    return MetadataSchema.parse(
        json,
    );
}