import { Catalog } from "./catalog";
import { Loader } from "./loader";

import type {
    Dataset,
    Metadata,
} from "./types";

/**
 * VideoStick library.
 */
export class Library {
    private readonly catalog: Catalog;

    private readonly loader: Loader;

    constructor(
        private readonly baseUrl: string,
    ) {
        this.catalog = new Catalog(
            baseUrl,
        );

        this.loader = new Loader(
            baseUrl,
        );
    }

    /**
     * Returns every song in the library.
     */
    list(): Promise<
        readonly Metadata[]
    > {
        return this.catalog.list();
    }

    /**
     * Returns a single song metadata.
     */
    get(
        id: string,
    ): Promise<Metadata | null> {
        return this.catalog.get(id);
    }

    /**
     * Searches the catalog.
     */
    search(
        text: string,
    ): Promise<
        readonly Metadata[]
    > {
        return this.catalog.search(
            text,
        );
    }

    /**
     * Loads a complete dataset.
     */
    async load(
        id: string,
    ): Promise<Dataset> {
        const metadata =
            await this.catalog.get(id);

        if (!metadata) {
            throw new Error(
                `Dataset "${id}" not found.`,
            );
        }

        return this.loader.load(
            metadata,
        );
    }
}