## Added
- Interactive filter selection popup menu ("By role" or "All siblings") when guessing item order via `NVDA+Shift+I`.
- Optimized fast O(1) order calculation for classic MSAA controls (e.g., wxWidgets, Poedit) directly via `NVDA+I`.

## Changed
- Automatically cancel ongoing background calculations when triggering a new order calculation command.
- Suppressed redundant focus announcements only when selecting a filter menu item (ensuring focus is announced when cancelling the menu via Escape).
- Updated Ukrainian localization and documentation.
