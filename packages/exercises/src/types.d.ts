export type Hand = "R" | "L";
export interface ExerciseBeat {
    hand: Hand;
}
export interface Exercise {
    id: string;
    title: string;
    beatsPerBar: number;
    beatUnit: number;
    beats: ExerciseBeat[];
}
export interface ExerciseBook {
    id: string;
    title: string;
    exercises: Record<string, Exercise>;
}
