## Changed
- Removed the word "Item" ("Елемент") from announcement messages for a more concise output (e.g., "3 of 10" instead of "Item 3 of 10").
- Updated minimum NVDA version to 2024.1 due to Python 3.10+ syntax requirements (older NVDA versions use Python 3.7, while NVDA 2024.1 updated to Python 3.11).
- Made fallback item order guessing asynchronous by running calculation in a background thread with periodic audio progress feedback (sound signal) to avoid freezing NVDA during long container traversals.
