"use client";

import type { CSSProperties, JSX } from "react";
import { Menu } from "@base-ui/react/menu";
import { Check, ChevronDown } from "lucide-react";

import {
    DIFFICULTY_ORDER,
    books,
} from "@octobeat/exercises";
import type {
    ExerciseBook,
    ExerciseSet,
} from "@octobeat/exercises";

import { useExerciseSelectionStore } from "../selectionStore";

const titleColor =
    "var(--title-color)";

const titleWeight =
    "var(--title-weight)";

const titleShadow =
    "1px 1px 0 var(--title-outline), -1px -1px 0 var(--title-outline), 1px -1px 0 var(--title-outline), -1px 1px 0 var(--title-outline), 1px 0 0 var(--title-outline), -1px 0 0 var(--title-outline), 0 1px 0 var(--title-outline), 0 -1px 0 var(--title-outline)";

const titleStyle: CSSProperties = {
    color: titleColor,
    fontWeight: titleWeight,
    textShadow: titleShadow,
};

const triggerClassName =
    "pointer-events-auto inline-flex cursor-pointer select-none appearance-none items-center gap-0.5 rounded border-0 bg-transparent px-0.5 py-0 font-mono text-xs uppercase tracking-wider outline-none transition-opacity hover:opacity-80 focus-visible:opacity-80 data-popup-open:opacity-80";

const popupClassName =
    "max-h-72 w-64 overflow-y-auto rounded-lg border border-border bg-popover p-1 text-popover-foreground shadow-lg";

const itemClassName =
    "flex cursor-pointer select-none items-center gap-2 rounded-md px-2 py-1.5 text-sm outline-none data-highlighted:bg-accent data-highlighted:text-accent-foreground";

interface ExerciseHeaderProps {
    /**
     * Libro al que pertenece la línea activa.
     */
    book: ExerciseBook;

    /**
     * Sección a la que pertenece la línea activa.
     */
    set: ExerciseSet;
}

function bookMenuOptions() {
    return Object.values(books)
        .sort(
            (a, b) =>
                DIFFICULTY_ORDER.indexOf(
                    a.difficulty,
                ) -
                DIFFICULTY_ORDER.indexOf(
                    b.difficulty,
                ),
        )
        .map((book) => ({
            value: book.id,
            label: book.title,
        }));
}

function MenuPopup({
    value,
    onValueChange,
    options,
}: {
    value: string;

    onValueChange(value: string): void;

    options: ReadonlyArray<{
        value: string;
        label: string;
    }>;
}) {
    return (
        <Menu.Portal>
            <Menu.Positioner className="z-[95]">
                <Menu.Popup className={popupClassName}>
                    <Menu.RadioGroup
                        value={value}
                        onValueChange={(next) =>
                            onValueChange(
                                next as string,
                            )
                        }
                    >
                        {options.map((option) => (
                            <Menu.RadioItem
                                key={option.value}
                                value={option.value}
                                closeOnClick
                                className={itemClassName}
                            >
                                <Menu.RadioItemIndicator className="shrink-0 text-primary">
                                    <Check className="size-4" />
                                </Menu.RadioItemIndicator>

                                {option.label}
                            </Menu.RadioItem>
                        ))}
                    </Menu.RadioGroup>
                </Menu.Popup>
            </Menu.Positioner>
        </Menu.Portal>
    );
}

export function ExerciseHeader({
    book,
    set,
}: ExerciseHeaderProps): JSX.Element {
    const bookId =
        useExerciseSelectionStore(
            (state) => state.bookId,
        );

    const setId =
        useExerciseSelectionStore(
            (state) => state.setId,
        );

    const setBook =
        useExerciseSelectionStore(
            (state) => state.setBook,
        );

    const setSet =
        useExerciseSelectionStore(
            (state) => state.setSet,
        );

    const selectedBook = Object.values(
        books,
    ).find(
        (candidate) =>
            candidate.id === bookId,
    );

    const setMenuOptions = selectedBook
        ? Object.values(
              selectedBook.sets,
          ).map((entry) => ({
              value: entry.id,
              label: entry.title,
          }))
        : [];

    return (
        <>
            <Menu.Root>
                <Menu.Trigger
                    className={triggerClassName}
                    style={titleStyle}
                >
                    {book.title}

                    <ChevronDown className="size-3 opacity-70" />
                </Menu.Trigger>

                <MenuPopup
                    value={bookId}
                    onValueChange={setBook}
                    options={bookMenuOptions()}
                />
            </Menu.Root>

            <span style={titleStyle}>
                ·
            </span>

            <Menu.Root>
                <Menu.Trigger
                    className={triggerClassName}
                    style={titleStyle}
                >
                    {set.title}

                    <ChevronDown className="size-3 opacity-70" />
                </Menu.Trigger>

                <MenuPopup
                    value={setId}
                    onValueChange={setSet}
                    options={setMenuOptions}
                />
            </Menu.Root>
        </>
    );
}
