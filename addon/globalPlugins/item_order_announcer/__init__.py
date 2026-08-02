import threading
from collections.abc import Callable

import addonHandler
import api
import globalCommands
import globalPluginHandler
import queueHandler
import tones
import ui
import wx
from inputCore import InputGesture
from NVDAObjects import NVDAObject
from scriptHandler import script

addonHandler.initTranslation()


def _guessItemOrder(
	obj: NVDAObject,
	parent: NVDAObject,
	onComplete: Callable[[int | None, int], None],
	cancelEvent: threading.Event,
) -> None:
	total = 0
	index = None

	children = parent.children
	for child in children:
		if cancelEvent.is_set():
			return

		if child.role == obj.role:
			total += 1
			if child == obj:
				index = total

	if not cancelEvent.is_set():
		onComplete(index, total)


def _iAccessibleGuessItemOrder(obj: NVDAObject) -> tuple[int, int] | None:
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
		return None

	parent = obj.parent
	if not parent:
		return None

	iaObject = getattr(parent, "IAccessibleObject", None)
	if iaObject is None:
		return None

	try:
		total = iaObject.accChildCount
	except Exception:
		return None

	if total <= 0:
		return None

	return childID, total


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = globalCommands.SCRCAT_FOCUS

	_workerThread: threading.Thread | None = None
	_cancelEvent: threading.Event | None = None
	_currentObj: NVDAObject | None = None

	@script(
		# Translators: Description of a script that reports the current item's order and the total
		# number of items in a list or tree view, falling back to an estimate when exact information
		# is unavailable.
		description=_("Reports the current item's order and the total number of items"),
		gesture="kb:NVDA+i",
	)
	def script_reportItemOrder(self, gesture: InputGesture) -> None:
		obj = api.getFocusObject()
		if not obj:
			# Translators: Reported when there is no focused object.
			ui.message(_("No focus"))
			return

		info = getattr(obj, "positionInfo", None)
		index = info.get("indexInGroup") if info else None
		total = info.get("similarItemsInGroup") if info else None
		level = info.get("level") if info else None

		if index is not None and total is not None:
			if level is not None:
				# Translators: Reported when pressing the item order gesture, including the nesting
				# level (e.g. in a tree view).
				message = _("{index} of {total}, level {level}").format(
					index=index,
					total=total,
					level=level,
				)
			else:
				# Translators: Reported when pressing the item order gesture.
				message = _("{index} of {total}").format(index=index, total=total)
			ui.message(message)
			return

		result = _iAccessibleGuessItemOrder(obj)
		if not result:
			# Translators: Reported when order information could not be determined, even by estimation.
			ui.message(_("Order could not be guessed"))
			return

		index, total = result
		# Translators: Reported when pressing the item order gesture and falling back to an estimate.
		ui.message(_("Approximately {index} of {total}").format(index=index, total=total))

	@script(
		# Translators: Description of a script that guesses the current item's order when exact info is unavailable.
		description=_("Guesses the current item's order and total count based on sibling objects (thorough)"),
		gesture="kb:NVDA+shift+i",
	)
	def script_guessItemOrder(self, gesture: InputGesture) -> None:
		"""
		Always runs the counting logic in a background thread, even for small child lists.

		We intentionally do NOT check `len(parent.children)` first to decide whether
		a thread is needed. Fetching `parent.children` is itself the expensive
		accessibility API call we're trying to protect against, so checking its
		length would require paying that cost synchronously first anyway, defeating
		the purpose of using a thread at all. The cost of always spawning a thread
		(a few milliseconds) is negligible compared to the risk of freezing NVDA on
		a slow accessibility backend (e.g. UIA-based apps).
		"""
		obj = api.getFocusObject()
		if not obj:
			ui.message(_("No focus"))
			return

		if self._currentObj == obj:
			tones.beep(200, 40)
			return

		if self._cancelEvent is not None:
			self._cancelEvent.set()

		cancelEvent = threading.Event()
		self._cancelEvent = cancelEvent
		self._currentObj = obj

		parent = obj.parent
		if not parent:
			self._currentObj = None
			ui.message(_("No parent object"))
			return

		def beepLoop() -> None:
			if cancelEvent.is_set() or not workerThread.is_alive():
				return

			tones.beep(500, 50)
			wx.CallLater(1000, beepLoop)  # pyright: ignore[reportUnusedCallResult]

		def onComplete(index: int | None, total: int) -> None:
			def finish() -> None:
				if self._workerThread is not workerThread:
					return

				self._currentObj = None
				self._workerThread = None
				self._cancelEvent = None

				if index is None or total == 0:
					# Translators: Reported when guessed order information could not be determined.
					message = _("Order could not be guessed")
				else:
					# Translators: Reported when pressing the guessed item order gesture.
					message = _("Approximately {index} of {total}").format(index=index, total=total)
				ui.message(message)

			queueHandler.queueFunction(queueHandler.eventQueue, finish)  # pyright: ignore[reportUnknownMemberType]

		workerThread = threading.Thread(
			target=_guessItemOrder,
			args=(obj, parent, onComplete, cancelEvent),
			daemon=True,
		)
		self._workerThread = workerThread
		workerThread.start()

		wx.CallLater(300, beepLoop)  # pyright: ignore[reportUnusedCallResult]
