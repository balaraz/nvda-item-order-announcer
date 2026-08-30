# A part of the nvda-item-order-announcer add-on for NVDA
# Copyright (C) 2026 balaraz
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

from NVDAObjects import NVDAObject


def getExactPosition(obj: NVDAObject) -> tuple[int, int, int | None] | None:
	"""
	Returns (index, total, level) from the object's own positionInfo, or None
	if exact position information isn't available for this object.
	"""
	info = getattr(obj, "positionInfo", None)
	if not info:
		return

	index = info.get("indexInGroup")
	total = info.get("similarItemsInGroup")
	level = info.get("level")

	if index is None or total is None:
		return

	return index, total, level


def guessPositionViaIAccessible(obj: NVDAObject) -> tuple[int, int] | None:
	"""
	Estimates the object's order among its siblings without exact positionInfo.

	This mirrors NVDA core's own fallback approach (used when the
	"Guess object position information when unavailable" setting is enabled):
	the object's own IAccessibleChildID is already a 1-based index assigned by
	the accessibility server, and the parent's accChildCount is a single COM
	property giving the total count. No iteration over children is needed,
	which is why this is instant even for containers with thousands of items.

	This only works for classic MSAA/IAccessible objects; UIA objects don't
	expose IAccessibleChildID, so this returns None for those.
	"""
	childID = getattr(obj, "IAccessibleChildID", None)
	if not childID:
		return

	parent = obj.parent
	if not parent:
		return

	iaObject = getattr(parent, "IAccessibleObject", None)
	if iaObject is None:
		return

	try:
		total = iaObject.accChildCount
	except Exception:
		return

	if total <= 0:
		return

	return childID, total
