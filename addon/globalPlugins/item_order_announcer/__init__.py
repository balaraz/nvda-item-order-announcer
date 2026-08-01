import threading
import time
from collections.abc import Callable

import addonHandler
import api
import globalCommands
import globalPluginHandler
import queueHandler
import tones
import ui
from inputCore import InputGesture
from NVDAObjects import NVDAObject
from scriptHandler import script

addonHandler.initTranslation()


def _guessItemOrder(
	obj: NVDAObject,
	parent: NVDAObject,
	onProgress: Callable[[], None],
	onComplete: Callable[[int | None, int], None],
	cancelEvent: threading.Event,
	progressIntervalSeconds: float = 1.0,
) -> None:
	total = 0
	index = None
	lastAnnounce = time.monotonic()

	for child in parent.children:
		if cancelEvent.is_set():
			return

		if child.role == obj.role:
			total += 1
			if child == obj:
				index = total

		now = time.monotonic()
		if now - lastAnnounce >= progressIntervalSeconds:
			if cancelEvent.is_set():
				return
			onProgress()
			lastAnnounce = now

	if not cancelEvent.is_set():
		onComplete(index, total)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = globalCommands.SCRCAT_FOCUS

	_workerThread: threading.Thread | None = None
	_cancelEvent: threading.Event | None = None
	_currentObj: NVDAObject | None = None

	@script(
		# Translators: Description of a script that reports the order of the current item in a list or tree view.
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
		if not info:
			# Translators: Reported when order information is not available for the focused object.
			ui.message(_("Order not available"))
			return

		index = info.get("indexInGroup")
		total = info.get("similarItemsInGroup")
		level = info.get("level")

		if index is None or total is None:
			# Translators: Reported when order information is not available for the focused object.
			ui.message(_("Order not available"))
			return

		if level is not None:
			# Translators: Reported when pressing the item order gesture, including the nesting level (e.g. in a tree view).
			message = _("{index} of {total}, level {level}").format(
				index=index,
				total=total,
				level=level,
			)
		else:
			# Translators: Reported when pressing the item order gesture.
			message = _("{index} of {total}").format(index=index, total=total)

		ui.message(message)

	@script(
		# Translators: Description of a script that guesses the current item's order when exact info is unavailable.
		description=_("Guesses the current item's order and total count based on sibling objects"),
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

		if self._workerThread is not None and self._workerThread.is_alive():
			if self._currentObj == obj:
				tones.beep(200, 40)
				return
			else:
				if self._cancelEvent is not None:
					self._cancelEvent.set()

		self._cancelEvent = threading.Event()
		self._currentObj = obj

		parent = obj.parent
		if not parent:
			self._currentObj = None
			ui.message(_("No parent object"))
			return

		def onProgress() -> None:
			queueHandler.queueFunction(queueHandler.eventQueue, tones.beep, 500, 50)  # pyright: ignore[reportUnknownMemberType]

		def onComplete(index: int | None, total: int) -> None:
			if self._currentObj == obj:
				self._currentObj = None

			if index is None or total == 0:
				# Translators: Reported when guessed order information could not be determined.
				message = _("Order could not be guessed")
			else:
				# Translators: Reported when pressing the guessed item order gesture.
				message = _("Approximately {index} of {total}").format(index=index, total=total)
			queueHandler.queueFunction(queueHandler.eventQueue, ui.message, message)  # pyright: ignore[reportUnknownMemberType]

		self._workerThread = threading.Thread(
			target=_guessItemOrder,
			args=(obj, parent, onProgress, onComplete, self._cancelEvent),
			daemon=True,
		)
		self._workerThread.start()
