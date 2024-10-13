# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
from sgtk import hook
from sgtk import LogManager

log = LogManager.get_logger(__name__)


class BundleDownloader(object):
    """
    Utility class that allows to download a bundle through the bootstrap hook.

    It is written as a separate file that cab be reimported by the bootstrapper
    after the core swap.
    """

    def __init__(self, connection, pipeline_config_id, descriptor):
        """
        :param connection: Connection to Shotgun.
        :param pipeline_config_id: Id of the pipeline configuration that was selected.
        :param descriptor: Descriptor of the configuration that we're running.
        """
        super(BundleDownloader, self).__init__()

        # First put our base hook implementation into the array.
        base_class_path = os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),  # ./python/tank/bootstrap
                "..",  # ./python/tank
                "..",  # ./python
                "..",  # ./
                "hooks",  # ./hooks
                "bootstrap.py",  # ./hooks/bootstrap.py
            )
        )
        hook_inheritance_chain = [base_class_path]
        # Then, check if there is a config-level override.
        hook_path = os.path.join(
            descriptor.get_config_folder(), "core", "hooks", "bootstrap.py"
        )
        if os.path.isfile(hook_path):
            hook_inheritance_chain.append(hook_path)

        self._hook_instance = hook.create_hook_instance(
            hook_inheritance_chain, parent=None
        )
        self._hook_instance.init(connection, pipeline_config_id, descriptor)

    def download_bundle(self, descriptor):
        """
        Downloads a bundle referenced by a descriptor.

        If the bootstrap hook's ``can_cache_bundle`` method returns True, the bundle will be
        downloaded through the hook.

        :param descriptor: Descriptor of the bundle to download.
        """
        if self._hook_instance.can_cache_bundle(descriptor):
            with descriptor._io_descriptor.open_write_location() as temporary_folder:
                self._hook_instance.populate_bundle_cache_entry(
                    temporary_folder, descriptor
                )
        else:
            descriptor.download_local()
