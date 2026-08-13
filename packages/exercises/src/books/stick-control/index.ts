import { shortRollCombinations } from "./short-roll-combinations";
import { shortRollCombinationsDouble } from "./short-roll-combinations-double";
import { singleBeatCombinations } from "./single-beat-combinations";
import { triplets } from "./triplets";

import type { ExerciseBook } from "../../types";

export const stickControl: ExerciseBook = {
    id: "stick-control",

    title: "Stick Control",

    sets: {
        singleBeatCombinations,
        triplets,
        shortRollCombinations,
        shortRollCombinationsDouble,
    },
};
