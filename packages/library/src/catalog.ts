import {
    MetadataSchema,
    type Metadata,
} from "./metadata";

/**
 * Library catalog.
 */
export class Catalog {
    private cache:
        | readonly Metadata[]
        | null = null;

    constructor(
        private readonly baseUrl: string,
    ) { }

    /**
     * Returns all available entries.
     */
    async list(): Promise<
        readonly Metadata[]
    > {
        if (this.cache) {
            return this.cache;
        }

        const response =
            await fetch(
                `${this.baseUrl}/catalog.json`,
            );

        if (!response.ok) {
            throw new Error(
                `Unable to load catalog (${response.status}).`,
            );
        }

        const json =
            await response.json();

        this.cache =
            MetadataSchema.array().parse(
                json,
            );

        return this.cache;
    }

    /**
     * Finds an entry by id.
     */
    async get(
        id: string,
    ): Promise<Metadata | null> {
        const entries =
            await this.list();

        return (
            entries.find(
                (entry) =>
                    entry.id === id,
            ) ?? null
        );
    }

    /**
     * Performs a text search.
     */
    async search(
        text: string,
    ): Promise<
        readonly Metadata[]
    > {
        const query =
            text.toLowerCase();

        const entries =
            await this.list();

        return entries.filter(
            (entry) =>
                entry.title
                    .toLowerCase()
                    .includes(query) ||
                entry.artist
                    .toLowerCase()
                    .includes(query) ||
                entry.genres.some(
                    (genre) =>
                        genre
                            .toLowerCase()
                            .includes(
                                query,
                            ),
                ) ||
                entry.tags.some(
                    (tag) =>
                        tag
                            .toLowerCase()
                            .includes(
                                query,
                            ),
                ),
        );
    }
}