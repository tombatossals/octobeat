export interface KeyboardShortcutsOptions {
    next?: () => void;
    previous?: () => void;
    /**
     * Called whenever a transport shortcut is handled.
     */
    onShortcut?: () => void;
}
export declare function useKeyboardShortcuts({ next, previous, onShortcut, }?: KeyboardShortcutsOptions): void;
