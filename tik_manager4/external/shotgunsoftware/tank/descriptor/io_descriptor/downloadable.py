# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import contextlib
import os
import uuid

from .base import IODescriptorBase
from ..errors import TankDescriptorIOError
from ...util import filesystem

from ... import LogManager

log = LogManager.get_logger(__name__)


class IODescriptorDownloadable(IODescriptorBase):
    """
    Base class for descriptors that can be downloaded locally to a path on disk.

    In order to create a Descriptor associated with data that can
    be downloaded locally to disk, it is necessary to derive from this class.
    By default, the AppStore, Git and Shotgun entity descriptors can be downloaded
    to disk and hence are of type :class: `IODescriptorDownloadable`.

    Descriptor data can be downloaded by invoking the :meth: `download_local` on instances
    of such derived classes. These classes are also expected to implement the
    :meth: `_download_local` and optionally, the :meth: `_post_download`.

    A general implementation of such a Descriptor class will be of the form:

    eg. class MyNewDownloadableDescriptor(IODescriptorDownloadable):
            def _download_local(self, destination_path):
                # .. code to download data to destination_path

            def _post_download(self, download_path):
                # .. code that will be executed post download.
    """

    _DOWNLOAD_TRANSACTION_COMPLETE_FILE = "install_complete"

    def download_local(self):
        """
        Downloads the data represented by the descriptor into the primary bundle
        cache path.
        """
        # Return if the descriptor exists locally.
        if self.exists_local():
            return

        with self.open_write_location() as temporary_path:
            # attempt to download the descriptor to the temporary path.
            log.debug(
                "Downloading %s to temporary download path %s." % (self, temporary_path)
            )
            self._download_local(temporary_path)

    @contextlib.contextmanager
    def open_write_location(self):
        """
        Writes a bundle to the primary bundle cache.

        It does so in a two step process. First, it yields a temporary location
        where the caller should write the bundle (typically in a 'tmp/<uuid>' directory
        in the bundle cache path), then, by moving the data to the primary bundle
        cache path for that descriptor. This helps to guard against multiple
        processes attempting to download the same descriptor simultaneously.

        This method should be used with the ``with`` statement:

            with desc.open_write_location() as tmp_dir:
                # Write the bundle information into tmp_dir.

        :returns: Yields the path where the bundle should be written.
        """
        # download it into a unique temporary location
        temporary_path = self._get_temporary_cache_path()

        # compute the location where we eventually want to move into
        target = self._get_primary_cache_path()

        # ensure that the parent directory of the target is present.
        # make sure we guard against multiple processes attempting to create it simultaneously.
        target_parent = os.path.dirname(target)
        try:
            filesystem.ensure_folder_exists(target_parent)
        except Exception as e:
            if not os.path.exists(target_parent):
                log.error("Failed to create directory %s: %s" % (target_parent, e))
                raise TankDescriptorIOError(
                    "Failed to create directory %s: %s" % (target_parent, e)
                )

        try:
            yield temporary_path

            # download completed without issue. Now create settings folder
            metadata_folder = self._get_metadata_folder(temporary_path)
            filesystem.ensure_folder_exists(metadata_folder)
        except Exception as e:
            # something went wrong during the download, remove the temporary files.
            log.error(
                "Failed to download into path %s: %s. Attempting to remove it."
                % (temporary_path, e)
            )
            # note - safe_delete_folder will not raise if something goes wrong, it will just log.
            filesystem.safe_delete_folder(temporary_path)
            raise TankDescriptorIOError(
                "Failed to download into path %s: %s" % (temporary_path, e)
            )

        log.debug(
            "Attempting to move descriptor %s from temporary path %s to target path %s."
            % (self, temporary_path, target)
        )

        move_succeeded = False

        try:
            # atomically rename the directory temporary_path to the target.
            # note: this is so that we don't end up with a partial payload in the target
            # location. All or nothing.
            os.rename(temporary_path, target)
            # write end receipt
            filesystem.touch_file(
                os.path.join(
                    self._get_metadata_folder(target),
                    self._DOWNLOAD_TRANSACTION_COMPLETE_FILE,
                )
            )
            move_succeeded = True
            log.debug(
                "Successfully moved the downloaded descriptor to target path: %s."
                % target
            )

        except Exception as e:

            # if the target path already exists, this means someone else is either
            # moving things right now or have moved it already, so we are ok.
            if not self._exists_local(target):
                # the target path does not exist. so the rename failed for other reasons.

                # if the rename did not work, it may be because the files are locked and
                # cannot be deleted. This can for example happen if an antivirus software
                # (on windows) has been triggered because of the download and has locked on
                # to the files. In this case, we try to copy the files and then remove the
                # temp payload - this is slower, but safer, and we can gracefully fail and
                # continue in case the deletion fails.
                log.warning(
                    "Failed to move descriptor %s from the temporary path %s "
                    "to the bundle cache %s. Will attempt to copy it instead. "
                    "Error: %s" % (self, temporary_path, target, e)
                )

                try:
                    # copy first then delete all files in target.
                    # if deletion fails this will log and gracefully continue.
                    log.debug(
                        "Performing 'copy then delete' style move on %s -> %s"
                        % (temporary_path, target)
                    )

                    # first write out our metadata folder where we store the transaction marker.
                    # this marks the beginning of the 'copy transaction' and will make sure that
                    # the logic in _exists_local() will not think the folder is a legacy format
                    # which doesn't implement transaction handling.
                    metadata_folder = self._get_metadata_folder(target)
                    filesystem.ensure_folder_exists(metadata_folder)

                    filesystem.move_folder(temporary_path, target)
                    # write end receipt
                    filesystem.touch_file(
                        os.path.join(
                            self._get_metadata_folder(target),
                            self._DOWNLOAD_TRANSACTION_COMPLETE_FILE,
                        )
                    )
                    # move_folder leaves all folders in the filesystem
                    # clean out these as well in a graceful way.
                    filesystem.safe_delete_folder(temporary_path)
                    move_succeeded = True

                except Exception as e:
                    # something during the copy went wrong. Attempt to roll back the target
                    # so we aren't left with any corrupt bundle cache items.
                    if os.path.exists(target):
                        log.debug(
                            "Move failed. Attempting to clear out target path '%s'"
                            % target
                        )
                        filesystem.safe_delete_folder(target)

                    # ...and raise an error. Include callstack so we get full visibility here.
                    log.exception(
                        "Failed to copy descriptor %s from the temporary path %s "
                        "to the bundle cache %s. Error: %s"
                        % (self, temporary_path, target, e)
                    )
                    raise TankDescriptorIOError(
                        "Failed to copy descriptor %s from the temporary path %s "
                        "to the bundle cache %s. Error: %s"
                        % (self, temporary_path, target, e)
                    )
            else:
                # note - safe_delete_folder will not raise if something goes wrong, it will just log.
                log.debug("Target location %s already exists." % target)
                log.debug("Removing temporary download %s" % temporary_path)
                filesystem.safe_delete_folder(temporary_path)

        if move_succeeded:
            # download completed ok! Run post processing
            self._post_download(target)

    def _get_temporary_cache_path(self):
        """
        Returns a temporary download cache path for this descriptor.
        """
        return os.path.join(self._bundle_cache_root, "tmp", uuid.uuid4().hex)

    def _download_local(self, destination_path):
        """
        Downloads the data identified by the descriptor to the destination_path.

        :param destination_path: The path on disk to which the descriptor is to
        be downloaded.

        eg. If the `destination_path` is
        /shared/bundle_cache/tmp/2f601ff3d85c43aa97d5811a308d99b3 for a git
        tag descriptor, this method is expected to download data directly to
        into the destination path. Thus the .git folder of the descriptor will have
        a path of /shared/bundle_cache/tmp/2f601ff3d85c43aa97d5811a308d99b3/.git
        """
        raise NotImplementedError

    def _post_download(self, download_path):
        """
        Method executed after a descriptor has been downloaded successfully.

        :param download_path: The path on disk to which the descriptor has been
        downloaded.
        """
        pass

    def _exists_local(self, path):
        """
        Checks is the bundle exists on disk and ensures that it has been completely
        downloaded if possible.

        :param str path: Path to the bundle to test.
        :returns: True if the bundle is deemed completed, False otherwise.
        """
        if not super(IODescriptorDownloadable, self)._exists_local(path):
            return False

        # Now that we are guaranteed there is a folder on disk, we'll attempt to do some integrity
        # checking.

        # The metadata folder is a folder that lives inside the bundle.
        metadata_folder = self._get_metadata_folder(path)

        # If the metadata folder does not exist, this is a bundle that was downloaded with an older
        # core. We will have to assume that it has been unzipped correctly.
        if not os.path.isdir(metadata_folder):
            log.debug(
                "Pre-core-0.18.120 download found at '%s'. Assuming it is complete.",
                path,
            )
            return True

        # Great, we're in the presence of a bundle that was downloaded with integrity check logic.

        # The completed file flag is a file that gets written out after the bundle has been
        # completely unzipped.
        completed_file_flag = os.path.join(
            metadata_folder, self._DOWNLOAD_TRANSACTION_COMPLETE_FILE
        )

        # If the complete file flag is missing, it means the download operation either failed (unlikely)
        # or is currently in progress (possible) so consider it as nonexistent.
        if os.path.exists(completed_file_flag):
            return True
        else:
            log.debug(
                "Note: Missing download complete ticket file '%s'. "
                "This suggests a partial or in-progress download" % completed_file_flag
            )
            return False

    def _get_metadata_folder(self, path):
        """
        Returns the corresponding metadata folder given a path
        """
        # Do not set this as a hidden folder (with a . in front) in case somebody does a
        # rm -rf * or a manual deletion of the files. This will ensure this is treated just like
        # any other file.
        return os.path.join(path, "tk-metadata")
