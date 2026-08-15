import { createExercise } from "../../../builder";

// Provisional: [closedroll:LRLR] representa el roll como un evento de
// duración normal; el manifiesto debería distinguir explícitamente la
// duración del roll de la duración de sus strokes internos.
export const line12 = createExercise({
    id: "stick-control-short-roll-review-line-12",

    title: "Line 12",

    notation: `
        [LRLR] [closedroll:LRLR] | [LRLR] [closedroll:LRLR] | [LRLR] [closedroll:LRLR] | [LRLR] [closedroll:LRLR] |
    `,
});
