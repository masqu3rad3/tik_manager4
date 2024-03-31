"""Collection of utility functions for Mari.

These are essentially methods are both required by the main module and the ingest, extract and/or validate modules.
To prevent circular imports, these methods are collected here.
"""

import configparser

from pathlib import Path

import mari

def get_uuid(mri_backup_path):
    """get the UUID of the project we want to work on."""
    # the uuid is in the corresponding summary file
    summary_file_name = str(Path(mri_backup_path).stem).replace("Project-", "Summary-")
    summary_file_path = Path(mri_backup_path).parent / f"{summary_file_name}.txt"
    config = configparser.ConfigParser()
    config.read(summary_file_path)
    general_section = config["General"]
    uuid = general_section["Uuid"]
    return uuid

def get_project(uuid: str):
    """Get the project by uuid."""
    all_projects = mari.projects.list()
    for project in all_projects:
        if project.uuid() == uuid:
            return project
    return None

def load(file_path, force=False):
    """Load the working file (mri) or exract the archive (mra)."""
    current_project = mari.projects.current()
    if current_project:
        current_project.close(ConfirmIfModified=not force)

    ext = Path(file_path).suffix
    if ext == '.mra':
        # if it's a .mra file, just extract it.
        project_info = mari.projects.extract(file_path)
    elif ext == '.mri':
        # if it's a .mri file, open it.
        uuid = get_uuid(file_path)
        target_project = get_project(uuid)
        if target_project:
            project_info = mari.projects.restoreBackup(file_path, uuid)
        else:
            # if the project is not found, import it from the file
            project_info = mari.projects.restoreBackup(file_path)
    else:
        raise RuntimeError(f"Unsupported file extension: {ext}")
    mari.projects.open(project_info.uuid())

def save_as(file_path):
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