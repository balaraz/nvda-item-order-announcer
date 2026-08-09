from collections.abc import Callable
from typing import Final

import addonHandler
import api
import globalCommands
import globalPluginHandler
import tones
import ui
from inputCore import InputGesture
from NVDAObjects import NVDAObject
from scriptHandler import script
from logHandler import log

from .backgroundGuess import BackgroundOrderGuesser, StartResult
from .positionInfo import getExactPosition, guessPositionViaIAccessible
from .filterMenu import showFilterMenu
from .focusSuppression import FocusEventSuppressor


addonHandler.initTranslation()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = globalCommands.SCRCAT_FOCUS

	# Class-level (not instance-level) so the background task's state survives
	# a plugin reload (e.g. via the Scratchpad reload shortcut) without a full
	# NVDA restart, avoiding a dangling thread from an orphaned instance.
	_backgroundGuesser: Final = BackgroundOrderGuesser()
	_focusSuppressor: Final = FocusEventSuppressor()

	def event_foreground(self, obj: NVDAObject, nextHandler: Callable[[], None]) -> None:
		flag = self._focusSuppressor.shouldSuppress()
		log.debug("event_foreground called, suppressForeground flag was set: %r", flag)
		if flag:
			log.debug("event_foreground SUPPRESSED")
			return
		nextHandler()

	def event_gainFocus(self, obj: NVDAObject, nextHandler: Callable[[], None]) -> None:
		flag = self._focusSuppressor.shouldSuppress()
		log.debug("event_gainFocus called, suppressFocus flag was set: %r", flag)
		if flag:
			log.debug("event_gainFocus SUPPRESSED")
			return
		nextHandler()

	def event_focusEntered(self, obj: NVDAObject, nextHandler: Callable[[], None]) -> None:
		flag = self._focusSuppressor.shouldSuppress()
		log.debug("event_focusEntered called, suppressFocus flag was set: %r", flag)
		if flag:
			return
		nextHandler()

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

		exact = getExactPosition(obj)
		if exact:
			index, total, level = exact
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

		guessed = guessPositionViaIAccessible(obj)
		if not guessed:
			# Translators: Reported when order information could not be determined, even by estimation.
			ui.message(_("Order could not be guessed"))
			return

		index, total = guessed
		# Translators: Reported when pressing the item order gesture and falling back to an estimate.
		ui.message(_("Approximately {index} of {total}").format(index=index, total=total))

	@script(
		# Translators: Description of a script that guesses the current item's order when exact info is unavailable.
		description=_("Guesses the current item's order and total count based on sibling objects (thorough)"),
		gesture="kb:NVDA+control+i",
	)
	def script_guessItemOrder(self, gesture: InputGesture) -> None:
		obj = api.getFocusObject()
		if not obj:
			# Translators: Reported when there is no focused object.
			ui.message(_("No focus"))
			return

		def onProgress() -> None:
			tones.beep(500, 50)

		def onResult(index: int | None, total: int) -> None:
			if index is None or total == 0:
				# Translators: Reported when guessed order information could not be determined.
				ui.message(_("Order could not be guessed"))
			else:
				# Translators: Reported when pressing the guessed item order gesture.
				ui.message(_("Approximately {index} of {total}").format(index=index, total=total))

		def onFilterChosen(onFilter: Callable[[NVDAObject], bool]) -> None:
			result = self._backgroundGuesser.start(obj, onFilter, onProgress, onResult)

			match result:
				case StartResult.STARTED:
					pass
				case StartResult.ALREADY_RUNNING:
					tones.beep(200, 40)
				case StartResult.NO_PARENT:
					# Translators: Reported when the focused object has no parent to estimate order from.
					ui.message(_("No parent object"))

		showFilterMenu(onFilterChosen, obj, self._focusSuppressor.suppressNext)
