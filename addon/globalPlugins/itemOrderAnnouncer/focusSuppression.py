# A part of the nvda-item-order-announcer add-on for NVDA
# Copyright (C) 2026 balaraz
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

import time


class FocusEventSuppressor:
	"""
	Tracks whether the next foreground/gainFocus event should be swallowed.

	Used when the plugin itself triggers a real OS foreground switch (e.g.
	showing a wx popup owned by NVDA's own invisible frame) and doesn't want
	the resulting focus-restore event to be spoken, since nothing actually
	changed from the user's perspective.
	"""

	_SUPPRESS_TIME_WINDOW_SECONDS = 0.5

	def __init__(self) -> None:
		super().__init__()
		self._suppressUntil: float | None = None

	def suppressNext(self) -> None:
		self._suppressUntil = time.monotonic() + self._SUPPRESS_TIME_WINDOW_SECONDS

	def shouldSuppress(self) -> bool:
		if self._suppressUntil is None:
			return False
		if time.monotonic() < self._suppressUntil:
			return True
		self._suppressUntil = None
		return False
