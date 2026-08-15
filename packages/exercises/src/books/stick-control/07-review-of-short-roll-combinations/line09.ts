import { createExercise } from "../../../builder";

// Provisional: [closedroll:RLRL] representa el roll como un evento de
// duración normal; el manifiesto debería distinguir explícitamente la
// duración del roll de la duración de sus strokes internos.
export const line09 = createExercise({
    id: "stick-control-short-roll-review-line-9",

    title: "Line 9",

    notation: `
        [RLRL] [closedroll:RLRL] | [RLRL] [closedroll:RLRL] | [RLRL] [closedroll:RLRL] | [RLRL] [closedroll:RLRL] |
    `,
});
