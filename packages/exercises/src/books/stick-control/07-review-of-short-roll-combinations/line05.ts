import { createExercise } from "../../../builder";

// Provisional: la última barra no mantiene exactamente la estructura de
// las anteriores; revisar la partitura a mayor resolución para determinar
// dónde empieza exactamente el último grupo.
export const line05 = createExercise({
    id: "stick-control-short-roll-review-line-5",

    title: "Line 5",

    notation: `
        [RLRL] [2:RRLLRRLL] [2:RRLLRRLL] | [RLRL] [2:RRLLRRLL] [2:RRLLRRLL] | [RLRL] [2:RRLLRRLL] [2:RRLLRRLL] | [2:RRLLRRLL] [2:RRLLRRLL] |
    `,
});
