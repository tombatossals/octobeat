import { createExercise } from "../../../builder";

// Provisional: [closedroll:RLRL] representa el roll como un evento de
// duración normal; el manifiesto debería distinguir explícitamente la
// duración del roll de la duración de sus strokes internos.
export const line11 = createExercise({
    id: "stick-control-short-roll-review-line-11",

    title: "Line 11",

    notation: `
        [RLRL] [closedroll:RLRL] | [RLRL] [closedroll:RLRL] | [RLRL] [closedroll:RLRL] | [RLRL] [closedroll:RLRL] |
    `,
});
