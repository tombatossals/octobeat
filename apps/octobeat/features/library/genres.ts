/**
 * Genre taxonomy. The catalog stores dozens of raw genre tags coming from
 * music providers (e.g. Deezer). Instead of exposing every raw tag in the
 * filters, we group similar tags into a small set of "big genres" (8–12).
 *
 * Filter values persist these group keys, so they are stable regardless of
 * the raw tags found in the catalog.
 */

export interface GenreGroup {
    key: string;

    label: string;
}

export const GENRE_GROUPS: ReadonlyArray<GenreGroup> = [
    { key: "rock", label: "Rock" },
    { key: "metal", label: "Metal" },
    { key: "pop", label: "Pop" },
    { key: "rap", label: "Rap / Hip-Hop" },
    { key: "rnb", label: "R&B / Soul" },
    { key: "reggae", label: "Reggae / Ska" },
    { key: "electronic", label: "Electrónica" },
    { key: "country", label: "Country" },
    { key: "folk", label: "Folk / Blues" },
    { key: "latin", label: "Latino" },
    { key: "soundtrack", label: "Bandas sonoras" },
    { key: "other", label: "Otros" },
];

const GENRE_TO_GROUP_KEY: Readonly<Record<string, string>> = {
    Rock: "rock",
    "Hard Rock": "rock",
    "Classic Rock": "rock",
    "Indie Rock": "rock",
    Alternativo: "rock",
    Alternative: "rock",
    "Alternative Rock": "rock",
    "Indie Rock/Rock pop": "rock",
    "Southern Rock": "rock",
    "Punk Rock": "rock",
    Punk: "rock",
    Emo: "rock",
    "Rock y Roll/Rockabilly": "rock",
    Rockabilly: "rock",
    Glam: "rock",
    "Glam Rock": "rock",
    Progressive: "rock",
    Prog: "rock",
    "Progressive Rock": "rock",
    "Instrumental Rock": "rock",
    "New Wave": "rock",
    Grunge: "rock",
    "Post-Grunge": "rock",
    "Post-grunge": "rock",
    "Noise Rock": "rock",
    "Stoner Rock": "rock",
    "Space Rock": "rock",
    "Psychedelic Rock": "rock",
    "Art Rock": "rock",
    "Arena Rock": "rock",
    "Garage Rock": "rock",
    "Grunge/Instrumental Rock": "rock",
    "Funk Rock": "rock",
    "Mordern Rock": "rock",
    "Post-Punk Revival": "rock",

    Metal: "metal",
    "Heavy Metal": "metal",
    "Thrash Metal": "metal",
    "Speed Metal": "metal",
    "Nu Metal": "metal",
    "Nu-Metal": "metal",
    "Progressive Metal": "metal",
    "Industrial Metal": "metal",
    "Death Metal": "metal",
    "Doom Metal": "metal",
    "Glam Metal": "metal",
    "Groove Metal": "metal",
    "Alternative Metal": "metal",
    "Punk-Metal": "metal",
    "Funk Metal": "metal",

    Pop: "pop",
    "Pop internacional": "pop",
    "Pop Rock": "pop",
    "Pop-Rock": "pop",
    "Pop/Rock": "pop",
    "Power Pop": "pop",
    "Pop Punk": "pop",
    "Pop Indie": "pop",
    "Art Pop": "pop",

    "Rap/Hip Hop": "rap",
    "Hip-Hop/Rap": "rap",

    "R&B": "rnb",
    "Soul & Funk": "rnb",

    Reggae: "reggae",
    "Reggae/Ska": "reggae",
    Ska: "reggae",
    "Reggae Rock": "reggae",
    "Reaggae Rock": "reggae",
    Psychobilly: "reggae",

    Electro: "electronic",
    Dance: "electronic",
    Disco: "electronic",
    "Disco/Pop": "electronic",
    "Techno/House": "electronic",
    Synthpop: "electronic",
    "Synth-Pop": "electronic",
    Mashup: "electronic",
    "Pop/Dance/Electronic": "electronic",

    Country: "country",

    Folk: "folk",
    Blues: "folk",
    "Texas Blues": "folk",
    "Singer & Songwriter": "folk",
    "Indie Pop/Folk": "folk",

    Latino: "latin",

    "Películas/Juegos": "soundtrack",
    "Bandas sonoras": "soundtrack",

    Other: "other",
    Various: "other",
    Humor: "other",
    Comedy: "other",
    Novelty: "other",
    Meme: "other",
    Niños: "other",
};

export const GENRE_GROUP_BY_KEY: Readonly<Record<string, GenreGroup>> =
    Object.fromEntries(
        GENRE_GROUPS.map((group) => [
            group.key,
            group,
        ]),
    );

/**
 * Returns the big genre key a raw genre tag belongs to. Unknown tags fall
 * back to the "other" group.
 */
export function genreGroupKey(
    genre: string,
): string {
    return (
        GENRE_TO_GROUP_KEY[genre] ??
        "other"
    );
}

/**
 * Returns the distinct big genre keys covered by the given raw genres.
 */
export function genreGroupKeys(
    genres: readonly string[],
): ReadonlySet<string> {
    const keys = new Set<string>();

    for (const genre of genres) {
        keys.add(
            genreGroupKey(genre),
        );
    }

    return keys;
}
