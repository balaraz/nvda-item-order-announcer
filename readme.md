# Item Order Announcer

* **Author:** balaraz <balaraz@tuta.io>
* **NVDA compatibility:** 2019.3 to 2026.2
* **Download:** [GitHub Repository][repo], [releases][rels]

This add-on for the NVDA screen reader quickly announces the order, total item count, and nesting level of the currently focused object (such as list items, tree view nodes, or menu options).

## Features

* **Instant Order Announcement:** Speaks the current item's index and total count in its group (e.g., "3 of 10").
* **Level Reporting:** Automatically includes the hierarchical nesting level when applicable (e.g., "3 of 10, level 2").
* **Fallback Order Guessing:** Allows guessing the order of an element by counting sibling objects when exact order info is unavailable.
* **Configurable Shortcuts:** All shortcuts are customizable in NVDA's Input Gestures dialog.

## Key Combinations

| Shortcut | Description |
| --- | --- |
| `NVDA+I` | Announces the index, total item count, and nesting level of the currently focused element. |
| `NVDA+Shift+I` | Guesses the current item's position and total count based on sibling objects with the same role. |

> **Note:** You can customize or reassign these shortcuts at any time in **NVDA Menu -> Preferences -> Input Gestures -> System focus**.

## How It Works

* **Exact Position:**
  1. The add-on retrieves the currently focused object.
  2. It checks native position metadata for the item and its group.
  3. If position information is available, NVDA announces:
     - `<index> of <total>`
     - If nesting level exists: `, level <level>`
  4. If position metadata is missing, NVDA reports "Order not available".

* **Guessed Position:**
  1. If exact position metadata is unavailable, the script inspects the focused object's parent container.
  2. It counts all sibling objects sharing the same accessibility role as the focused element.
  3. If successful, NVDA announces: `Approximately <index> of <total>`.
  4. If position cannot be determined, NVDA reports "Order could not be guessed".

## License

Copyright 2026 balaraz.
Distributed under the GNU General Public License v2.0 (GPL 2.0). See [COPYING.txt](COPYING.txt) for details.

## Change Log

### Version 1.0
* Added script to report focused item order, total count, and nesting level.
* Added fallback script to guess item order and total count based on sibling objects when native position info is unavailable.
* Assigned default keyboard shortcuts (`NVDA+I` and `NVDA+Shift+I`) to the scripts.


[repo]: https://github.com/balaraz/nvda-item-order-announcer
[rels]: https://github.com/balaraz/nvda-item-order-announcer/releases
