"""Main module for Mari integration."""

from pathlib import Path
import logging
import configparser

import mari

from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.dcc.main_core import MainCore
from tik_manager4.dcc.mari import validate
from tik_manager4.dcc.mari import extract
from tik_manager4.dcc.mari import ingest

LOG = logging.getLogger(__name__)


class Dcc(MainCore):
    """Mari class."""

    name = "mari"
    formats = [".mri"]  # File formats supported by the DCC
    preview_enabled = False  # Whether or not to enable the preview in the UI
    validations = validate.classes
    extracts = extract.classes
    ingests = ingest.classes

    # Override the applicable methods from the MainCore class

    @staticmethod
    def pre_save_issues():
        """Checks to be done before saving a file."""
        project = mari.projects.current()
        if not project:
            return "No Mari project is open. You need to be in a project to save it."

    @staticmethod
    def get_main_window():
        """Get the main window."""
        # Set Mari main window to be in focus.
        mari.app.activateMainWindow()
        # Returns the window that has focus.
        return QtWidgets.QApplication.activeWindow()

    def save_as(self, file_path):
        """Mimic the save as functionality for Mari."""

        # Mari doesn't have a save as functionality. So, we will mimic that with backup.
        project = mari.projects.current()
        folder_path = Path(file_path).parent
        project.setBackupPath(str(folder_path))

        suffix = f"{mari.projects.generateRestoreSuffix()}_tikmanager"

        # make sure the paint buffer is baked
        paint_buffer = mari.canvases.paintBuffer()
        paint_buffer.bake()

        # Trigger backup
        project.save(ForceSave=True, BackupOptions={"Suffix": suffix})
        generated_file_path = folder_path / f"Project{suffix}.mri"

        return str(generated_file_path)

    def open(self, file_path, force=True, **_extra_arguments):
        """Open the file in Mari."""
        uuid = self._get_uuid(file_path)
        current_project = mari.projects.current()
        if current_project:
            current_project.close(ConfirmIfModified=not force)
        # get all projects
        target_project = self._get_project(uuid)
        if target_project:
            project_info = mari.projects.restoreBackup(file_path, uuid)
        else:
            # if the project is not found, import it from the file
            project_info = mari.projects.restoreBackup(file_path)

        mari.projects.open(project_info.uuid())

    def _get_uuid(self, mri_path: str):
        """get the UUID of the project we want to work on."""
        # the uuid is in the corresponding summary file
        summary_file_name = str(Path(mri_path).stem).replace("Project-", "Summary-")
        summary_file_path = Path(mri_path).parent / f"{summary_file_name}.txt"
        config = configparser.ConfigParser()
        config.read(summary_file_path)
        general_section = config["General"]
        uuid = general_section["Uuid"]
        return uuid

    def _get_project(self, uuid: str):
        """Get the project by uuid."""
        all_projects = mari.projects.list()
        for pr in all_projects:
            if pr.uuid() == uuid:
                return pr
        return None

    @staticmethod
    def is_modified():
        """Check if the scene has unsaved changes."""
        project = mari.projects.current()
        if project:
            return project.isModified()
        return False

    @staticmethod
    def get_scene_file():
        """Get the current scene file."""
        project = mari.projects.current()
        if not project:
            return ""
        project_scene_path = project.backupPath()
        # collect all the .mri files in the directory
        all_mri_files = Path(project_scene_path).glob("*.mri")
        # filter the ones that ends with _tikmanager.mri
        tik_files = [f for f in all_mri_files if f.stem.endswith("_tikmanager")]
        # get the latest one
        # TODO is there a way to get the accurate one?
        if tik_files:
            return str(tik_files[-1])
        return ""

    def generate_thumbnail(self, file_path, width, height):
        """Generate a thumbnail for the current scene."""
        project = mari.projects.current()
        if not project:
            return None

        canvas = mari.canvases.current()
        if not canvas:
            return None

        hud_state = canvas.getDisplayProperty("HUD/RenderHud")
        if hud_state:
            canvas.setDisplayProperty("HUD/RenderHud", False)

        capt = canvas.capture(width, height)
        capt.save(file_path)

        if hud_state:
            canvas.setDisplayProperty("HUD/RenderHud", True)

        return file_path

    @staticmethod
    def get_dcc_version():
        """Get the current version of Mari."""
        version = mari.app.version()
        return str(version.major())
