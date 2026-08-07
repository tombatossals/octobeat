export function lowerBound<T>(
    items: readonly T[],
    value: number,
    key: (item: T) => number,
): number {
    let low = 0;
    let high = items.length - 1;

    while (low <= high) {
        const mid = (low + high) >> 1;

        // Safe because the binary search invariant guarantees:
        // 0 <= mid < items.length
        const item = items[mid]!;

        if (key(item) <= value) {
            low = mid + 1;
        } else {
            high = mid - 1;
        }
    }

    return Math.max(0, low - 1);
}