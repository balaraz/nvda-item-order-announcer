class FocusEventSuppressor:
	"""
	Tracks whether the next foreground/gainFocus event should be swallowed.

	Used when the plugin itself triggers a real OS foreground switch (e.g.
	showing a wx popup owned by NVDA's own invisible frame) and doesn't want
	the resulting focus-restore event to be spoken, since nothing actually
	changed from the user's perspective.
	"""

	def __init__(self) -> None:
		super().__init__()
		self._suppressForeground = False
		self._suppressFocus = False

	def suppressNext(self) -> None:
		"""Call right before triggering the real foreground/focus change to suppress."""
		self._suppressForeground = True
		self._suppressFocus = True

	def shouldSuppressForeground(self) -> bool:
		if self._suppressForeground:
			self._suppressForeground = False
			return True
		return False

	def shouldSuppressFocus(self) -> bool:
		if self._suppressFocus:
			self._suppressFocus = False
			return True
		return False
