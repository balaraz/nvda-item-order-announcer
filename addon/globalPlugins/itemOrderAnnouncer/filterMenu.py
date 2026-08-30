# A part of the nvda-item-order-announcer add-on for NVDA
# Copyright (C) 2026 balaraz
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

from collections.abc import Callable

import addonHandler
import gui
import wx
from NVDAObjects import NVDAObject


addonHandler.initTranslation()


def filterByRole(obj: NVDAObject) -> Callable[[NVDAObject], bool]:
	"""Only counts siblings that share the same role as obj."""
	return lambda neighbor: neighbor.role == obj.role


def filterAll(neighbor: NVDAObject) -> bool:
	"""Counts every sibling, regardless of role."""
	return True


def showFilterMenu(
	onFilterChosen: Callable[[Callable[[NVDAObject], bool]], None],
	obj: NVDAObject,
	onItemSelected: Callable[[], None],
) -> None:
	"""
	Shows a popup menu letting the user pick how siblings should be counted.

	onFilterChosen is called with the selected filter function only if the
	user actually picks an item; pressing Escape closes the menu with no
	callback invocation, which is the built-in behaviour of wx.Menu/PopupMenu.

	`wx.CallAfter(show)` queues menu display to the wx event loop so it runs
	after the current script execution returns to the main loop. This prevents
	PopupMenu from nesting inside the active queue invocation, avoiding NVDA
	speech loop blocking and allowing screen reader announcements for menu items.
	"""

	def show() -> None:
		menu = wx.Menu()

		# Translators: Menu item to guess item order by matching the sibling role.
		byRoleItem = menu.Append(wx.ID_ANY, _("By role"))  # pyright: ignore[reportUnknownMemberType]
		# Translators: Menu item to guess item order counting all siblings, regardless of role.
		allItem = menu.Append(wx.ID_ANY, _("All siblings"))  # pyright: ignore[reportUnknownMemberType]

		def onByRole(evt: wx.CommandEvent) -> None:
			onItemSelected()
			onFilterChosen(filterByRole(obj))

		def onAll(evt: wx.CommandEvent) -> None:
			onItemSelected()
			onFilterChosen(filterAll)

		menu.Bind(wx.EVT_MENU, onByRole, byRoleItem)  # pyright: ignore[reportUnknownMemberType]
		menu.Bind(wx.EVT_MENU, onAll, allItem)  # pyright: ignore[reportUnknownMemberType]

		assert gui.mainFrame is not None
		gui.mainFrame.prePopup()
		try:
			gui.mainFrame.PopupMenu(menu)  # pyright: ignore[reportUnknownMemberType, reportUnusedCallResult]
		finally:
			gui.mainFrame.postPopup()
		menu.Destroy()  # pyright: ignore[reportUnusedCallResult]

	wx.CallAfter(show)  # pyright: ignore[reportUnknownMemberType]
