"""Class for holding Gaffer menu."""

import Gaffer
import GafferUI

class GafferMenu:
    """Class for holding Gaffer menu."""
    menu = None

    @classmethod
    def set_menu(cls, menu):
        """Set the menu."""
        cls.menu = menu

    @property
    def script_window(self):
        """Get the script window."""
        return self.menu.ancestor(GafferUI.ScriptWindow)

    @property
    def script(self):
        """Return the script."""
        script_window = self.menu.ancestor(GafferUI.ScriptWindow)
        return script_window.scriptNode()

    @property
    def application(self):
        """Return the application."""
        return self.script.ancestor(Gaffer.ApplicationRoot)

