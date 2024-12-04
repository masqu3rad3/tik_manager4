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
import zipfile
from . import filesystem
from .. import LogManager

log = LogManager.get_logger(__name__)

SYSTEM_FILE_ITEMS = set(["__MACOSX", ".DS_Store"])


@filesystem.with_cleared_umask
def unzip_file(src_zip_file, target_folder, auto_detect_bundle=False):
    """
    Unzips the given file into the given folder.

    Does the following command, but in a way which works with
    Python 2.5 and Python2.6.2::

        z = zipfile.ZipFile(zip_file, "r")
        z.extractall(target_folder)

    Works around http://bugs.python.org/issue6050

    :param src_zip_file: Path to zip file to uncompress
    :param target_folder: Folder to extract into
    :param auto_detect_bundle: Hints that the attachment contains a toolkit bundle
        (config, app, engine, framework) and that this should be attempted to be
        detected and unpacked intelligently. For example, if the zip file contains
        the bundle in a subfolder, this should be correctly unfolded.
    """
    log.debug("Unpacking %s into %s" % (src_zip_file, target_folder))
    zip_obj = zipfile.ZipFile(src_zip_file, "r")

    extraction_done = False

    if auto_detect_bundle:
        # enable additional flexibility in order to auto detect a bundle structure
        # within the zip. Support the following alternative formats:
        # - files are extracted according to the structure in the zip (default case)
        # - if the zip contains a single folder with all content inside,
        #   assume the bundle is contained inside this structure. This is
        #   a common scenario if a user has created a zip by right clicking on it
        #   and selected 'create archive' or 'send to zip'.

        # compute number of unique root folders
        # note: zip module uses forward slash on all operating systems
        root_items = set(
            [item.split("/")[0] for item in zip_obj.namelist() if "/" in item]
        )
        # remove certain system items
        root_items -= SYSTEM_FILE_ITEMS

        if len(root_items) == 1:
            root_to_omit = root_items.pop()

            log.debug(
                "Zip file contains a single folder '%s' and auto_detect_bundle flag is set. "
                "Will extract content out of the folder." % root_to_omit
            )

            for x in zip_obj.namelist():
                if x.startswith(root_to_omit):
                    _process_item(zip_obj, x, target_folder, root_to_omit)

            extraction_done = True

    # loosely based on:
    # http://forums.devshed.com/python-programming-11/unzipping-a-zip-file-having-folders-and-subfolders-534487.html
    #
    # make sure we are using consistent permissions
    # get list of file names contained in archive
    if not extraction_done:
        for x in zip_obj.namelist():
            # process them one by one
            _process_item(zip_obj, x, target_folder)


@filesystem.with_cleared_umask
def zip_file(source_folder, target_zip_file):
    """
    Zips the contents of a folder.

    :param source_folder: Folder to process
    :param target_zip_file: Path to zip file to create
    """
    log.debug("Zipping contents of %s to %s" % (source_folder, target_zip_file))
    zf = zipfile.ZipFile(target_zip_file, "w", zipfile.ZIP_DEFLATED)
    for root, ignored, files in os.walk(source_folder):
        for fname in files:
            fspath = os.path.join(root, fname)
            arcpath = os.path.join(root, fname)[len(source_folder) + 1 :]
            zf.write(fspath, arcpath)
    zf.close()
    log.debug("Zip complete. Size: %s" % os.path.getsize(target_zip_file))


def _process_item(zip_obj, item_path, target_path, root_to_omit=None):
    """
    Helper method used by unzip_file()

    Modified version of _extract_member in
    http://hg.python.org/cpython/file/538f4e774c18/Lib/zipfile.py

    :param zip_obj: Zipfile object to extract from
    :param item_path: XZip file object to unpack
    :param target_path: Path to unpack into
    :param root_to_omit:
    :returns: Full path to the unpacked file or folder
    """
    # build the destination pathname, replacing
    # forward slashes to platform specific separators.
    # Strip trailing path separator, unless it represents the root.
    if (
        target_path[-1:] in (os.path.sep, os.path.altsep)
        and len(os.path.splitdrive(target_path)[1]) > 1
    ):
        target_path = target_path[:-1]

    # see if we need to omit a root_folder
    # e.g.
    # target_path = '/tmp', item_path = 'test/foo/bar.png', root_to_omit='test'
    # ==>
    # /tmp/foo/bar.png
    #
    if root_to_omit and item_path.startswith(root_to_omit):
        processed_item_path = item_path[len(root_to_omit) + 1 :]
    else:
        processed_item_path = item_path

    # don't include leading "/" from file name if present
    if item_path[0] == "/":
        target_path = os.path.join(target_path, processed_item_path[1:])
    else:
        target_path = os.path.join(target_path, processed_item_path)

    target_path = os.path.normpath(target_path)

    # Create all upper directories if necessary.
    upperdirs = os.path.dirname(target_path)
    if upperdirs and not os.path.exists(upperdirs):
        os.makedirs(upperdirs, 0o777)

    if item_path[-1] == "/":
        # this is a directory!
        if not os.path.isdir(target_path):
            os.mkdir(target_path, 0o777)

    else:
        # this is a file! - write it in a way which is compatible
        # with py25 zipfile library interface
        target_obj = open(target_path, "wb")
        target_obj.write(zip_obj.read(item_path))
        target_obj.close()
        # Restore permissions on the extracted file
        # Took bits and bobs from here :
        # http://bugs.python.org/file34893/issue15795_test_and_doc_fixes.patch
        zip_info = zip_obj.getinfo(item_path)
        # Only preserve execution bits: --x--x--x
        # That is binary 001001001 = 0x49
        # External attr seems to be 4 bytes long
        # permissions being stored in 2 top most bytes, hence the 16 shift
        # See : http://unix.stackexchange.com/questions/14705/the-zip-formats-external-file-attribute
        # If one execution bit is set, give execution rights to everyone
        mode = zip_info.external_attr >> 16 & 0x49
        if mode:
            os.chmod(target_path, 0o777)

    return target_path
