"""A version picker for Trigger: the main window's four trees, one Use button."""

from pathlib import Path

from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui.mcv.category_mcv import TikCategoryWidget
from tik_manager4.ui.mcv.subproject_mcv import TikSubProjectWidget
from tik_manager4.ui.mcv.task_mcv import TikTaskWidget
from tik_manager4.ui.mcv.version_mcv import TikVersionWidget


class TikPickerDialog(QtWidgets.QDialog):
    """Pick a work or publish version; ``pick()`` returns its file path."""

    #: the version widget's buttons that act on the scene rather than pick a
    #: path. ``on_load`` opens the version through the DCC handler, which for
    #: trigger3 is ``host.open`` -- browsing for a field path must never
    #: replace Trigger's active session. The Use button is the only exit.
    ACTION_BUTTONS = ("import_btn", "bundle_ingest_btn", "load_btn", "reference_btn")

    def __init__(self, tik, kind, extensions, parent=None):
        super().__init__(parent)
        self.tik = tik
        self.kind = kind
        self.extensions = [
            ext if ext.startswith(".") else f".{ext}" for ext in extensions
        ]
        self.setWindowTitle(f"Tik Manager - pick {kind}")
        self.resize(1100, 600)
        self._chosen = ""
        layout = QtWidgets.QVBoxLayout(self)
        trees = QtWidgets.QHBoxLayout()
        layout.addLayout(trees, 1)
        self.subprojects = TikSubProjectWidget(tik.project, parent=self)
        self.tasks = TikTaskWidget()
        self.tasks.task_view.hide_columns(["id", "path"])
        self.categories = TikCategoryWidget()
        self.categories.work_tree_view.hide_columns(["id", "path"])
        self.versions = TikVersionWidget(tik.project, parent=self)
        for widget in (self.subprojects, self.tasks, self.categories, self.versions):
            trees.addWidget(widget)
        self.subprojects.sub_view.item_selected.connect(self.tasks.task_view.set_tasks)
        self.subprojects.sub_view.add_item.connect(self.tasks.task_view.add_tasks)
        self.tasks.task_view.refresh_requested.connect(
            self.subprojects.sub_view.get_tasks
        )
        self.tasks.task_view.item_selected.connect(self.categories.set_task)
        self.categories.work_tree_view.item_selected.connect(self.versions.set_base)
        self.categories.work_tree_view.item_selected.connect(lambda _b: self._refresh())
        self.versions.version.combo.currentIndexChanged.connect(
            lambda _i: self._refresh()
        )
        self.versions.element.element_combo.currentIndexChanged.connect(
            lambda _i: self._refresh()
        )
        buttons = QtWidgets.QHBoxLayout()
        layout.addLayout(buttons)
        self.path_label = QtWidgets.QLabel("")
        buttons.addWidget(self.path_label, 1)
        self.use_button = QtWidgets.QPushButton("Use")
        self.use_button.setEnabled(False)
        self.use_button.clicked.connect(self._accept)
        cancel = QtWidgets.QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        buttons.addWidget(self.use_button)
        buttons.addWidget(cancel)
        for name in self.ACTION_BUTTONS:
            getattr(self.versions.buttons, name).clicked.disconnect()
        self._disarm_action_buttons()
        self.subprojects.refresh()

    def _disarm_action_buttons(self):
        """Hide and disable the version widget's scene-acting buttons.

        ``TikVersionWidget.button_states`` flips ``import_btn`` and
        ``bundle_ingest_btn`` back on with every ``set_base``, so this runs
        again after every refresh.
        """
        for name in self.ACTION_BUTTONS:
            button = getattr(self.versions.buttons, name)
            button.setVisible(False)
            button.setEnabled(False)

    # ------------------------------------------------------------ seams
    def select_work(self, base):
        """Point the version widget at ``base`` (a Work or Publish) directly."""
        self.versions.set_base(base)
        self._refresh()

    # ------------------------------------------------------- resolution
    def _base(self):
        item = self.categories.work_tree_view.get_selected_item()
        tik_obj = getattr(item, "tik_obj", None)
        if tik_obj is not None:
            return tik_obj
        return getattr(self.versions, "base", None)

    def chosen_path(self) -> str:
        base = self._base()
        version = self.versions.get_selected_version()
        if base is None or version is None:
            return ""
        if hasattr(version, "scene_path"):  # a work version
            path = Path(base.get_abs_project_path(version.scene_path))
        else:  # a publish version
            element = self.versions.get_selected_element_type() or "source"
            relative = version.get_element_path(element)
            if not relative:
                return ""
            path = Path(version.get_resolved_path(relative))
            if path.is_dir():
                inside = sorted(
                    child
                    for child in path.iterdir()
                    if not self.extensions or child.suffix in self.extensions
                )
                if not inside:
                    return ""
                path = inside[0]
        return path.as_posix()

    def _acceptable(self, path: str) -> bool:
        if not path or not Path(path).exists():
            return False
        return not self.extensions or Path(path).suffix in self.extensions

    def _refresh(self):
        self._disarm_action_buttons()
        path = self.chosen_path()
        self.path_label.setText(path)
        self.use_button.setEnabled(self._acceptable(path))

    def _accept(self):
        self._chosen = self.chosen_path()
        self.accept()

    def pick(self) -> str:
        """Show the dialog; the chosen path or ``""``."""
        self._chosen = ""
        self.exec_()
        return self._chosen
