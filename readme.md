# Item Order Announcer

* **Author:** balaraz <balaraz@tuta.io>
* **NVDA compatibility:** 2019.3 to 2026.2
* **Download:** [GitHub Repository][repo], [releases][rels]

Item Order Announcer is an add-on for the NVDA screen reader that quickly announces the order, total item count, and nesting level of the currently focused object (such as list items, tree view nodes, or menu options).

## Features

* **Instant Order Announcement:** Speaks the current item's index and total count in its group (e.g., "Item 3 of 10").
* **Level Reporting:** Automatically includes the hierarchical nesting level when applicable (e.g., "Item 3 of 10, level 2").

## Key Combinations

| Shortcut | Description |
| --- | --- |
| `NVDA+I` | Announces the index, total item count, and nesting level of the currently focused element. |

> **Note:** You can customize or reassign these shortcuts at any time in **NVDA Menu -> Preferences -> Input Gestures -> System focus**.

## How It Works

When pressing `NVDA+I`:
1. The add-on retrieves the current focus object (`api.getFocusObject()`).
2. It inspects object position metadata (`indexInGroup`, `similarItemsInGroup`, and `level`).
3. If position information is available, NVDA announces:
   - `Item <index> of <total>`
   - If nesting level exists: `, level <level>`
4. If no position information is available or no object is focused, NVDA reports an appropriate message ("Position not available" / "No focus").

## License

Copyright 2026 balaraz.
Distributed under the GNU General Public License v2.0 (GPL 2.0). See [COPYING.txt](COPYING.txt) for details.

## Change Log

### Version 0.1
* Initial release.
* Added `NVDA+I` shortcut to report focus item position and level.


[repo]: https://github.com/balaraz/nvda-item-order-announcer
[rels]: https://github.com/balaraz/nvda-item-order-announcer/releases
