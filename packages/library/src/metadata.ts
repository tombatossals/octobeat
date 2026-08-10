import { z } from "zod";

export const ResourcesSchema = z.object({
    audio: z.string(),

    video: z
        .string()
        .nullish(),
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
            .nullish(),

        year: z
            .number()
            .int()
            .nullish(),

        genres: z.array(
            z.string(),
        ),

        bpm: z.number(),

        duration: z.number(),

        difficulty: z
            .number()
            .int()
            .nullish(),

        tags: z.array(
            z.string(),
        ),

        timeSignature: z
            .string()
            .nullish(),

        timing: TimingProvenanceSchema
            .nullish(),

        youtube: z
            .string()
            .nullish(),

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