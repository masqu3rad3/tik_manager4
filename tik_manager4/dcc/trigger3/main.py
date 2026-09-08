"""Tik Manager's view of tik.trigger (workflow v3), through Trigger's VCS host."""

import logging

from tik_manager4.dcc.main_core import MainCore
from tik_manager4.dcc.trigger3 import extension, extract, ingest, validate
from tik_manager4.dcc.trigger3._host import host, session_file_in

LOG = logging.getLogger(__name__)


class Dcc(MainCore):
    """tik.trigger as a DCC. Every verb forwards to ``tik.trigger.vcs.host``."""

    name = "trigger3"
    formats = [".tr"]
    preview_enabled = False
    validations = validate.classes
    extracts = extract.classes
    ingests = ingest.classes
    extensions = extension.classes

    def post_save(self):
        """Tell Trigger its version control context may have changed."""
        host().refresh()

    def post_publish(self):
        """Tell Trigger its version control context may have changed."""
        host().refresh()

    def save_scene(self):
        """Save the active session over itself."""
        current = host().session_path
        if current:
            host().save_as(current)

    def save_as(self, file_path, **extra_arguments):
        """Save the active session to ``file_path``, returning where it went."""
        return str(host().save_as(file_path)).replace("\\", "/")

    def save_prompt(self):
        """Save the session, asking where when it has never been saved.

        This is only ever called for a session with no file yet -- saving in
        place cannot work, so ask for a path. Returning False on a cancel
        stops the caller, which reads anything falsy as "not saved".
        """
        current = host().session_path
        if not current:
            path = host().feedback.browse_save("Save session", "", (".tr",))
            if not path:
                return False
            host().save_as(path)
            return True
        host().save_as(current)
        return True

    def open(self, file_path, force=True, **extra_arguments):
        """Open the given session: a ``.tr``, or the bundle folder holding one.

        Publish.load_version hands the resolved ``source`` element straight to
        the DCC handler, and for trigger3 that element is the ``SOURCE_``
        bundle folder rather than a file.
        """
        host().open(session_file_in(file_path))

    def is_modified(self):
        """Return True if the session has unsaved changes."""
        return host().is_modified

    def get_scene_file(self):
        """Return the active session file, or an empty string."""
        return host().session_path

    def get_dcc_version(self):
        """Return the Trigger version."""
        from tik.trigger import VERSION

        return VERSION

    def get_main_window(self):
        """Return Maya's main window, or None when there is no UI.

        Asking Maya for its main window from an interpreter that never
        started Maya crashes it outright, so the presence of a QApplication
        -- which every Maya with a UI has and no headless mayapy does --
        gates the question.
        """
        try:
            from tik_manager4.ui.Qt import QtWidgets

            if QtWidgets.QApplication.instance() is None:
                return None
            from tik.shared.ui.qtmaya import get_main_window

            return get_main_window()
        except Exception:  # pylint: disable=broad-except - no Maya, or no Qt
            return None

    def generate_thumbnail(self, file_path, width, height):
        """Stamp a placeholder thumbnail; a session has no viewport."""
        from tik_manager4.dcc.standalone.main import Dcc as Standalone

        Standalone.text_to_image("TR", file_path, width, height)
        return file_path
