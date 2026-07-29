import addonHandler
import globalPluginHandler
import globalCommands
import api
import ui
from inputCore import InputGesture
from scriptHandler import script


addonHandler.initTranslation()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = (globalCommands.SCRCAT_FOCUS,)

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
			message = _("Item {index} of {total}, level {level}").format(
				index=index,
				total=total,
				level=level,
			)
		else:
			# Translators: Reported when pressing the item order gesture.
			message = _("Item {index} of {total}").format(index=index, total=total)

		ui.message(message)
