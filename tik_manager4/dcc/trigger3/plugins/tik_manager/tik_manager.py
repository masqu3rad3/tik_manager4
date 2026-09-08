"""Tik Manager as a Trigger version control provider."""

from pathlib import Path

from tik.trigger.vcs import kinds, register_provider
from tik.trigger.vcs.provider import Context, VersionControl

DCC_NAME = "trigger3"

#: The last window ``_launch_window`` opened. Without a parent -- which is what
#: ``get_main_window`` returns outside Maya -- the window would be garbage
#: collected the moment the verb returns.
_WINDOW = None


def _launch_window():
    """Open tik_manager's main window for trigger3, through its own launcher.

    ``ui.main.launch`` initialises tik_manager4 for the DCC, closes any window
    already carrying the same object name, sets ``AA_DontUseNativeMenuBar`` and
    honours a DCC's ``custom_launcher``; doing it by hand stacks a second
    window on every call.
    """
    global _WINDOW  # pylint: disable=global-statement
    from tik_manager4.ui import main

    _WINDOW = main.launch(DCC_NAME)
    return _WINDOW


def _tik():
    """A tik_manager4 main object bound to the trigger3 DCC.

    ``initialize`` sets the global DCC and reloads ``objects.main``, so inside a
    Maya that also runs tik_manager's Maya integration this is re-done before
    every operation, as the old integration did.
    """
    import tik_manager4

    return tik_manager4.initialize(DCC_NAME)


@register_provider("tik_manager")
class TikManagerProvider(VersionControl):
    """Works, versions and publishes of a Tik Manager project."""

    label = "Tik Manager"
    icon = "tik_manager"

    def available(self) -> bool:
        try:
            import tik_manager4  # noqa: F401
        except ImportError:
            return False
        return True

    def context(self, session_path: str):
        if not session_path:
            return None
        tik = _tik()
        work, version = tik.project.find_work_by_absolute_path(session_path)
        if not work:
            return None
        latest = work.versions[-1].version if work.versions else version
        return Context(
            label=f"{work.task_name} / {work.name}",
            version=version,
            is_latest=version == latest,
            detail=work.path,
        )

    def browse(self, kind: str, extensions: list, mode: str) -> str:
        from tik_manager4.dcc.trigger3.picker import TikPickerDialog

        tik = _tik()
        dialog = TikPickerDialog(
            tik, kind, extensions, parent=tik.dcc.get_main_window()
        )
        return dialog.pick()

    def new_version(self, host) -> str:
        tik = _tik()
        work, _version = tik.project.find_work_by_absolute_path(host.session_path)
        if not work:
            host.feedback.pop_error(
                "Tik Manager",
                "The session is not a Tik Manager work.",
                "Save it as a new work from the Tik Manager window first.",
            )
            return ""
        made = work.new_version(file_format=".tr", notes="Saved from Trigger")
        if made == -1:
            return ""
        return host.session_path

    def open(self, host) -> str:
        picked = self.browse(kinds.SESSION, [".tr"], "open")
        if picked:
            host.open(picked)
        return picked

    def publish_file(self, kind: str, path, host) -> None:
        _launch_window().on_save_any_file(file_path=str(Path(path)))

    def launch(self, host) -> None:
        _launch_window()
