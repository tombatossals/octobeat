import { createExercise } from "../../../builder";

export const line1 = createExercise({
    id: "stick-control-triplet-line-1",

    title: "Line 1",

    notation: `
        [RLRL] (3:RLR) |
        (3:LRL) [RLRL] (3:RLR) |
        (3:LRL) |
    `,
});
