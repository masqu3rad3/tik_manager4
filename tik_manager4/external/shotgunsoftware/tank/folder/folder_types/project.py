# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from ...errors import TankError
from .entity import Entity
from ... import constants
from ...log import LogManager

log = LogManager.get_logger(__name__)


class Project(Entity):
    """
    The root point. Represents a shotgun project.
    """

    @classmethod
    def create(cls, tk, schema_config_project_folder, metadata):
        """
        Factory method for this class

        :param tk: Tk API instance
        :param parent: Parent :class:`Folder` object.
        :param full_path: Full path to the configuration file
        :param metadata: Contents of configuration file.
        :returns: :class:`Entity` instance.
        """
        # execute default_storage_root hook to modify the metadata storage root 'root_name'
        # if there's any Project custom field in PTR overriding the default storage root.
        try:
            tk.execute_core_hook_method(
                constants.DEFAULT_STORAGE_ROOT_HOOK_NAME,
                "execute",
                storage_roots=tk.pipeline_configuration._storage_roots,
                project_id=tk.pipeline_configuration.get_project_id(),
                metadata=metadata,
            )
        except Exception as e:
            # Catch errors to not kill our thread, log them for debug purpose.
            log.debug(
                "%s hook failed with %s" % (constants.DEFAULT_STORAGE_ROOT_HOOK_NAME, e)
            )
        storage_name = metadata.get("root_name", None)
        if storage_name is None:
            raise TankError(
                "Missing or invalid value for 'root_name' in metadata: %s"
                % schema_config_project_folder
            )

        # now resolve the disk location for the storage specified in the project config
        local_roots = tk.pipeline_configuration.get_local_storage_roots()

        if storage_name not in local_roots:
            raise TankError(
                "The storage '%s' specified in the folder configuration %s.yml does not exist "
                "in the storage configuration!"
                % (storage_name, schema_config_project_folder)
            )

        storage_root_path = local_roots[storage_name]

        return Project(tk, schema_config_project_folder, metadata, storage_root_path)

    def __init__(self, tk, schema_config_project_folder, metadata, storage_root_path):
        """
        constructor
        """

        no_filters = {"logical_operator": "and", "conditions": []}

        self._tk = tk
        self._storage_root_path = storage_root_path

        Entity.__init__(
            self,
            tk,
            None,
            schema_config_project_folder,
            metadata,
            "Project",
            "tank_name",
            no_filters,
            create_with_parent=False,
        )

    def get_storage_root(self):
        """
        Local storages are defined in the Shotgun preferences.
        This method returns the local OS path that is associated with the
        local storage that this project node is associated with.
        (By default, this is the primary storage, but if you have a multi
        root config, there may be more than one project node.)
        """
        return self._storage_root_path
