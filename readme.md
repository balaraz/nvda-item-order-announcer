# Item Order Announcer

* **Author:** balaraz <balaraz@tuta.io>
* **NVDA compatibility:** 2024.1 to 2026
* **Download:** [GitHub Repository][repo], [releases][rels]

This add-on for the NVDA screen reader quickly announces the order, total item count, and nesting level of the current navigator object (which follows the focus by default, such as list items, tree view nodes, or menu options).

## Features

* **Instant Order Announcement:** Speaks the current item's index and total count in its group (e.g., "3 of 10").
* **Fast MSAA Lookup:** Instantly resolves item order for classic MSAA applications (such as wxWidgets or Poedit) without background calculation.
* **Level Reporting:** Automatically includes the hierarchical nesting level when applicable (e.g., "3 of 10, level 2").
* **Fallback Order Guessing with Filtering:** Allows guessing element position by counting sibling objects, with a choice to filter by role or count all siblings.
* **Configurable Shortcuts:** All shortcuts are customizable in NVDA's Input Gestures dialog.

## Key Combinations

| Shortcut | Description |
| --- | --- |
| `NVDA+I` | Announces the index, total item count, and nesting level of the current navigator object. |
| `NVDA+Control+I` | Opens a popup menu to select a filter strategy ("By role" or "All siblings") and guesses the item's position based on sibling objects. |

> **Note:** You can customize or reassign these shortcuts at any time in **NVDA Menu -> Preferences -> Input Gestures -> Object navigation**.

## How It Works

* **Exact Position:**
  1. The add-on retrieves the current navigator object.
  2. It checks native position metadata for the item and its group, including fast direct position lookups for classic MSAA controls.
  3. If position information is available, NVDA announces:
     - `<index> of <total>`
     - If nesting level exists: `, level <level>`
  4. If position metadata is missing, NVDA reports "Order not available".

* **Guessed Position:**
  1. If exact position metadata is unavailable, invoking the shortcut prompts with a popup menu to select a filtering strategy:
     - **By role:** counts only sibling objects sharing the same accessibility role as the current element.
     - **All siblings:** counts all sibling objects in the container regardless of role.
  2. The add-on inspects the current object's parent container and calculates position asynchronously in a background thread.
  3. If successful, NVDA announces: `Approximately <index> of <total>`.
  4. If position cannot be determined, NVDA reports "Order could not be guessed".
  5. Starting a new calculation or moving focus automatically cancels any active background calculation. Focus announcement is suppressed only when selecting a menu item (and announced normally when cancelling the menu via Escape).

## License

Copyright 2026 balaraz.
Distributed under the GNU General Public License v2.0 (GPL 2.0). See [COPYING.txt](COPYING.txt) for details.

## Change Log

### Version 2.1
- Changed default shortcut for guessing item order to `NVDA+Control+I` to avoid collision with NVDA built-in gestures.

### Version 2.0
- Added interactive filter selection popup menu ("By role" or "All siblings") when guessing item order via `NVDA+Shift+I`.
- Added optimized fast O(1) order calculation for classic MSAA controls (e.g., wxWidgets, Poedit) directly via `NVDA+I`.
- Automatically cancel ongoing background calculations when triggering a new order calculation command.
- Suppressed redundant focus announcements only when selecting a filter menu item (ensuring focus is announced when cancelling the menu via Escape).
- Updated Ukrainian localization and documentation.

### Version 1.1
- Removed the word "Item" ("Елемент") from announcement messages for a more concise output (e.g., "3 of 10" instead of "Item 3 of 10").
- Updated minimum NVDA version to 2024.1 due to Python 3.10+ syntax requirements (older NVDA versions use Python 3.7, while NVDA 2024.1 updated to Python 3.11).
- Made fallback item order guessing asynchronous by running calculation in a background thread with periodic audio progress feedback (sound signal) to avoid freezing NVDA during long container traversals.
- Delayed progress audio feedback to prevent unnecessary beeps on fast lists.
- Automatically cancel background item order calculation when focus moves to another object.
- Updated Ukrainian localization and documentation.

### Version 1.0
* Added script to report focused item order, total count, and nesting level.
* Added fallback script to guess item order and total count based on sibling objects when native position info is unavailable.
* Assigned default keyboard shortcuts (`NVDA+I` and `NVDA+Shift+I`) to the scripts.


[repo]: https://github.com/balaraz/nvda-item-order-announcer
[rels]: https://github.com/balaraz/nvda-item-order-announcer/releases
