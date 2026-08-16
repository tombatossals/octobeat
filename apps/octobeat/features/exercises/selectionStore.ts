import { create } from "zustand";

import {
    firstSetId,
    loadSelection,
    saveSelection,
} from "./selectionStorage";

interface ExerciseSelectionState {
    /**
     * Id del libro seleccionado.
     */
    bookId: string;

    /**
     * Id de la sección seleccionada dentro del libro.
     */
    setId: string;

    /**
     * Selecciona un libro y reinicia la sección a su primera sección.
     */
    setBook(
        bookId: string,
    ): void;

    /**
     * Selecciona una sección dentro del libro activo.
     */
    setSet(
        setId: string,
    ): void;
}

const initial = loadSelection();

export const useExerciseSelectionStore =
    create<ExerciseSelectionState>(
        (set, get) => ({
            bookId: initial.bookId,

            setId: initial.setId,

            setBook(bookId) {
                const setId =
                    firstSetId(bookId);

                saveSelection({
                    bookId,
                    setId,
                });

                set({
                    bookId,
                    setId,
                });
            },

            setSet(setId) {
                saveSelection({
                    bookId: get().bookId,
                    setId,
                });

                set({
                    setId,
                });
            },
        }),
    );
