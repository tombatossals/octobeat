import type { JSX } from "react";
import type { Exercise } from "@octobeat/exercises";
export interface ExerciseTimelineProps {
    exercise: Exercise;
    currentBeat: number;
}
export declare function ExerciseTimeline({ exercise, currentBeat, }: ExerciseTimelineProps): JSX.Element;
