// apps/octobeat/lib/library.ts

import { Library } from "@octobeat/library";

import { useSettingsStore } from "@/features/settings/store";

const CATALOG_FILE = "catalog.json";

/**
 * The catalog package appends "/catalog.json" to the base URL, so if the
 * configured URL already points at the file we strip it to avoid
 * ".../catalog.json/catalog.json".
 */
function catalogBaseUrl(
    catalogUrl: string,
): string {
    if (
        catalogUrl.endsWith(
            `/${CATALOG_FILE}`,
        )
    ) {
        return catalogUrl.slice(
            0,
            -CATALOG_FILE.length - 1,
        );
    }

    return catalogUrl;
}

/**
 * Builds a Library pointed at the configured catalog.
 */
export function getLibrary(): Library {
    const { catalogUrl } =
        useSettingsStore.getState()
            .settings;

    return new Library(
        catalogBaseUrl(catalogUrl),
    );
}
