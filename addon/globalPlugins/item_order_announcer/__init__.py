import addonHandler
import api
import globalCommands
import globalPluginHandler
import tones
import ui
from inputCore import InputGesture
from NVDAObjects import NVDAObject
from scriptHandler import script

from .backgroundGuess import BackgroundOrderGuesser, StartResult


addonHandler.initTranslation()


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

	# Class-level (not instance-level) so the background task's state survives
	# a plugin reload (e.g. via the Scratchpad reload shortcut) without a full
	# NVDA restart, avoiding a dangling thread from an orphaned instance.
	_backgroundGuesser = BackgroundOrderGuesser()

	@script(
		# Translators: Description of a script that reports the current item's order and the total
		# number of items in a list or tree view, falling back to an estimate when exact information
		# is unavailable.
		description=_("Reports the current item's order and the total number of items"),
		gesture="kb:NVDA+i",
	)
	def script_reportItemOrder(self, gesture: InputGesture) -> None:
		self._backgroundGuesser.cancel()

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
		obj = api.getFocusObject()
		if not obj:
			# Translators: Reported when there is no focused object.
			ui.message(_("No focus"))
			return

		def onFilter(neighbor: NVDAObject) -> bool:
			return neighbor.role == obj.role

		def onProgress() -> None:
			tones.beep(500, 50)

		def onResult(index: int | None, total: int) -> None:
			if index is None or total == 0:
				# Translators: Reported when guessed order information could not be determined.
				ui.message(_("Order could not be guessed"))
			else:
				# Translators: Reported when pressing the guessed item order gesture.
				ui.message(_("Approximately {index} of {total}").format(index=index, total=total))

		result = self._backgroundGuesser.start(obj, onFilter, onProgress, onResult)

		if result is StartResult.ALREADY_RUNNING:
			tones.beep(200, 40)
		elif result is StartResult.NO_PARENT:
			# Translators: Reported when the focused object has no parent to estimate order from.
			ui.message(_("No parent object"))
