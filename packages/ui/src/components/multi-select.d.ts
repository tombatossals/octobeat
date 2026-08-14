import type { ReactNode } from "react";
interface MultiSelectOption {
    value: string;
    label: ReactNode;
}
interface MultiSelectProps {
    value: string[];
    onValueChange: (value: string[]) => void;
    options: ReadonlyArray<MultiSelectOption>;
    placeholder?: string;
    countLabel?: (count: number) => ReactNode;
    className?: string;
    popupClassName?: string;
}
declare function MultiSelect({ value, onValueChange, options, placeholder, countLabel, className, popupClassName, }: MultiSelectProps): import("react").JSX.Element;
export { MultiSelect };
