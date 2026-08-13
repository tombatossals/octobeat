import { z } from "zod";

/**
 * Accepts an absolute URL or a local relative path such as "/resources".
 */
function isValidCatalogUrl(
    value: string,
): boolean {
    if (value.startsWith("/")) {
        return true;
    }

    try {
        new URL(value);
        return true;
    } catch {
        return false;
    }
}

export const SettingsSchema = z
    .object({
        catalogUrl: z
            .string()
            .refine(
                isValidCatalogUrl,
                "Enter a valid URL.",
            ),

        repetitionsPerLine: z
            .number()
            .int()
            .min(1),

        theme: z.enum([
            "dark",
            "light",
        ]),
    })
    .strict();

export type SettingsInput =
    z.input<typeof SettingsSchema>;

export function parseSettings(
    json: unknown,
): z.infer<
    typeof SettingsSchema
> {
    return SettingsSchema.parse(json);
}

export function isHttpsUrl(
    url: string,
): boolean {
    return url.startsWith("https://");
}
