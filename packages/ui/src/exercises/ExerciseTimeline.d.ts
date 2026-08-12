import type { JSX } from "react";
import type { Exercise } from "@octobeat/exercises";
export interface ExerciseTimelineProps {
    exercise: Exercise;
    currentBeat: number;
    /**
     * Desactiva el resaltado del beat activo (vista previa).
     */
    preview?: boolean;
    /**
     * Última repetición de la línea: los compases ya superados se
     * atenúan para indicar que no volverán a sonar.
     */
    lastPass?: boolean;
}
export declare function ExerciseTimeline({ exercise, currentBeat, preview, lastPass, }: ExerciseTimelineProps): JSX.Element;
