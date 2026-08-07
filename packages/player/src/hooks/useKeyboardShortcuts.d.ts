export interface KeyboardShortcutsOptions {
    next?: () => void;
    previous?: () => void;
}
export declare function useKeyboardShortcuts({ next, previous, }?: KeyboardShortcutsOptions): void;
