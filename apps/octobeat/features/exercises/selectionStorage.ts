import {
    DIFFICULTY_ORDER,
    books,
} from "@octobeat/exercises";

const STORAGE_KEY =
    "octobeat.exercise-selection";

export interface ExerciseSelection {
    /**
     * Id del libro seleccionado.
     */
    bookId: string;

    /**
     * Id de la sección seleccionada dentro del libro.
     */
    setId: string;
}

function booksByDifficulty() {
    return Object.values(books).sort(
        (a, b) =>
            DIFFICULTY_ORDER.indexOf(
                a.difficulty,
            ) -
            DIFFICULTY_ORDER.indexOf(
                b.difficulty,
            ),
    );
}

/**
 * Selección por defecto: el primer libro por dificultad y su primera
 * sección.
 */
export function defaultSelection(): ExerciseSelection {
    const book = booksByDifficulty()[0]!;

    return {
        bookId: book.id,
        setId: Object.values(
            book.sets,
        )[0]!.id,
    };
}

/**
 * Devuelve el id de la primera sección del libro indicado. Si el libro
 * no existe, la sección de la selección por defecto.
 */
export function firstSetId(
    bookId: string,
): string {
    const book = Object.values(
        books,
    ).find(
        (candidate) =>
            candidate.id === bookId,
    );

    return book
        ? Object.values(
              book.sets,
          )[0]!.id
        : defaultSelection().setId;
}

/**
 * Valida una selección persistida contra el catálogo actual: si el
 * libro o la sección ya no existen, se resuelve a la selección por
 * defecto (o a la primera sección del libro guardado).
 */
function validSelection(
    bookId: unknown,
    setId: unknown,
): ExerciseSelection {
    if (typeof bookId !== "string") {
        return defaultSelection();
    }

    const book = Object.values(
        books,
    ).find(
        (candidate) =>
            candidate.id === bookId,
    );

    if (!book) {
        return defaultSelection();
    }

    const validSet = Object.values(
        book.sets,
    ).some(
        (set) => set.id === setId,
    );

    return {
        bookId: book.id,
        setId: validSet
            ? (setId as string)
            : Object.values(
                  book.sets,
              )[0]!.id,
    };
}

function hasStorage(): boolean {
    return typeof window !== "undefined";
}

/**
 * Loads the book/section selection from localStorage. Falls back to the
 * default selection when the stored value is missing, invalid or refers
 * to a book/section that no longer exists.
 */
export function loadSelection(): ExerciseSelection {
    if (!hasStorage()) {
        return defaultSelection();
    }

    const raw =
        window.localStorage.getItem(
            STORAGE_KEY,
        );

    if (!raw) {
        return defaultSelection();
    }

    try {
        const parsed =
            JSON.parse(raw) as Partial<ExerciseSelection>;

        return validSelection(
            parsed.bookId,
            parsed.setId,
        );
    } catch {
        return defaultSelection();
    }
}

/**
 * Persists the book/section selection to localStorage.
 */
export function saveSelection(
    selection: ExerciseSelection,
): void {
    if (!hasStorage()) {
        return;
    }

    window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(selection),
    );
}
