import { shortRollCombinations } from "./04-short-roll-combinations";
import { shortRollCombinationsDouble } from "./05-short-roll-combinations-double";
import { shortRollCombinationsIii } from "./06-short-roll-combinations-iii";
import { reviewOfShortRollCombinations } from "./07-review-of-short-roll-combinations";
import { singleBeatCombinations } from "./01-single-beat-combinations";
import { tripletsIi } from "./03-triplets-ii";
import { triplets } from "./02-triplets";

import type { ExerciseBook } from "../../types";

export const stickControl: ExerciseBook = {
    id: "stick-control",

    title: "Stick Control",

    difficulty: "easy",

    sets: {
        singleBeatCombinations,
        triplets,
        tripletsIi,
        shortRollCombinations,
        shortRollCombinationsDouble,
        shortRollCombinationsIii,
        reviewOfShortRollCombinations,
    },
};
