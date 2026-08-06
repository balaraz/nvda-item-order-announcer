import threading
from collections.abc import Callable
from enum import Enum, auto

import queueHandler
import wx
from NVDAObjects import NVDAObject


class StartResult(Enum):
	STARTED = auto()
	ALREADY_RUNNING = auto()
	NO_PARENT = auto()


def _guessItemOrder(
	obj: NVDAObject,
	parent: NVDAObject,
	onFilter: Callable[[NVDAObject], bool],
	onComplete: Callable[[int | None, int], None],
	cancelEvent: threading.Event,
) -> None:
	total = 0
	index = None

	children = parent.children
	for child in children:
		if cancelEvent.is_set():
			return

		if onFilter(child):
			total += 1
			if child == obj:
				index = total

	if not cancelEvent.is_set():
		onComplete(index, total)


class BackgroundOrderGuesser:
	"""
	Manages a single background task that estimates an item's order among its
	siblings by iterating over all of the parent's children.

	This class contains no UI calls (no ui.message, no tones.beep) by design;
	callers are notified purely through the return value of start() and the
	onProgress/onResult callbacks, and are responsible for presenting anything
	to the user.
	"""

	def __init__(self) -> None:
		super().__init__()

		self._workerThread: threading.Thread | None = None
		self._cancelEvent: threading.Event | None = None
		self._currentObj: NVDAObject | None = None

	def cancel(self) -> None:
		if self._cancelEvent is not None:
			self._cancelEvent.set()
		self._workerThread = None
		self._currentObj = None

	def start(
		self,
		obj: NVDAObject,
		onFilter: Callable[[NVDAObject], bool],
		onProgress: Callable[[], None],
		onResult: Callable[[int | None, int], None],
	) -> StartResult:
		if self._currentObj == obj:
			return StartResult.ALREADY_RUNNING

		self.cancel()

		parent = obj.parent
		if not parent:
			return StartResult.NO_PARENT

		cancelEvent = threading.Event()
		self._cancelEvent = cancelEvent
		self._currentObj = obj

		def beepLoop() -> None:
			if cancelEvent.is_set() or not workerThread.is_alive():
				return

			onProgress()
			wx.CallLater(1000, beepLoop)  # pyright: ignore[reportUnusedCallResult]

		def onComplete(index: int | None, total: int) -> None:
			def finish() -> None:
				if self._workerThread is not workerThread:
					return

				self._currentObj = None
				self._workerThread = None
				onResult(index, total)

			queueHandler.queueFunction(queueHandler.eventQueue, finish)  # pyright: ignore[reportUnknownMemberType]

		workerThread = threading.Thread(
			target=_guessItemOrder,
			args=(obj, parent, onFilter, onComplete, cancelEvent),
			daemon=True,
		)
		self._workerThread = workerThread
		workerThread.start()

		wx.CallLater(300, beepLoop)  # pyright: ignore[reportUnusedCallResult]

		return StartResult.STARTED
