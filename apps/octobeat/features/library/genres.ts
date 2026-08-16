/**
 * Genre taxonomy. The catalog stores dozens of raw genre tags coming from
 * music providers (e.g. Deezer). Instead of exposing every raw tag in the
 * filters, we group similar tags into a set of "big genres".
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
    { key: "hard-rock", label: "Hard Rock" },
    { key: "alternativo", label: "Alternativo / Indie" },
    { key: "punk", label: "Punk / Emo" },
    { key: "clasico", label: "Clásico / Rock & Roll" },
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
    Glam: "rock",
    "Glam Rock": "rock",
    Progressive: "rock",
    Prog: "rock",
    "Progressive Rock": "rock",
    "Instrumental Rock": "rock",
    "Stoner Rock": "rock",
    "Space Rock": "rock",
    "Psychedelic Rock": "rock",
    "Art Rock": "rock",
    "Garage Rock": "rock",
    "Funk Rock": "rock",
    "Mordern Rock": "rock",

    "Hard Rock": "hard-rock",
    "Arena Rock": "hard-rock",

    Alternativo: "alternativo",
    Alternative: "alternativo",
    "Alternative Rock": "alternativo",
    "Indie Rock": "alternativo",
    "Indie Rock/Rock pop": "alternativo",
    "New Wave": "alternativo",
    Grunge: "alternativo",
    "Post-Grunge": "alternativo",
    "Post-grunge": "alternativo",
    "Noise Rock": "alternativo",
    "Post-Punk Revival": "alternativo",
    "Grunge/Instrumental Rock": "alternativo",

    "Punk Rock": "punk",
    Punk: "punk",
    Emo: "punk",
    "Pop Punk": "punk",

    "Classic Rock": "clasico",
    "Southern Rock": "clasico",
    "Rock y Roll/Rockabilly": "clasico",
    Rockabilly: "clasico",

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
