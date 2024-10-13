# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Methods for downloading things from Shotgun
"""
from __future__ import with_statement

import os
import sys
import uuid
from tank_vendor.six.moves import urllib
import time
import tempfile
import zipfile

from ..errors import ShotgunAttachmentDownloadError
from ...errors import TankError
from ...log import LogManager
from ..zip import unzip_file
from .. import filesystem

log = LogManager.get_logger(__name__)


@LogManager.log_timing
def download_url(sg, url, location, use_url_extension=False, headers=None):
    """
    Convenience method that downloads a file from a given url.
    This method will take into account any proxy settings which have
    been defined in the Shotgun connection parameters.

    In some cases, the target content of the url is not known beforehand.
    For example, the url ``https://my-site.shotgunstudio.com/thumbnail/full/Asset/1227``
    may redirect into ``https://some-site/path/to/a/thumbnail.png``. In
    such cases, you can set the optional use_url_extension parameter to True - this
    will cause the method to append the file extension of the resolved url to
    the filename passed in via the location parameter. So for the urls given
    above, you would get the following results:

    - location="/path/to/file" and use_url_extension=False would return "/path/to/file"
    - location="/path/to/file" and use_url_extension=True would return "/path/to/file.png"

    :param sg: Shotgun API instance to get proxy connection settings from
    :param url: url to download
    :param location: path on disk where the payload should be written.
                     this path needs to exists and the current user needs
                     to have write permissions
    :param bool use_url_extension: Optionally append the file extension of the
                                   resolved URL's path to the input ``location``
                                   to construct the full path name to the downloaded
                                   contents. The newly constructed full path name
                                   will be returned.

    :returns: Full filepath to the downloaded file. This may have been altered from
              the input ``location`` if ``use_url_extension`` is True and a file extension
              could be determined from the resolved url.
    :raises: :class:`TankError` on failure.
    """
    # We only need to set the auth cookie for downloads from Shotgun server,
    # input URLs like: https://my-site.shotgunstudio.com/thumbnail/full/Asset/1227
    if sg.config.server in url:
        # this method also handles proxy server settings from the shotgun API
        __setup_sg_auth_and_proxy(sg)
    elif sg.config.proxy_handler:
        # These input URLs have generally already been authenticated and are
        # in the form: https://sg-media-staging-usor-01.s3.amazonaws.com/9d93f...
        # %3D&response-content-disposition=filename%3D%22jackpot_icon.png%22.
        # Grab proxy server settings from the shotgun API
        opener = urllib.request.build_opener(sg.config.proxy_handler)

        urllib.request.install_opener(opener)

    # inherit the timeout value from the sg API
    timeout = sg.config.timeout_secs

    # download the given url
    try:
        request = urllib.request.Request(url, headers=headers or {})
        if timeout and sys.version_info >= (2, 6):
            # timeout parameter only available in python 2.6+
            response = urllib.request.urlopen(request, timeout=timeout)
        else:
            # use system default
            response = urllib.request.urlopen(request)

        if use_url_extension:
            # Make sure the disk location has the same extension as the url path.
            # Would be nice to see this functionality moved to back into Shotgun
            # API and removed from here.
            url_ext = os.path.splitext(urllib.parse.urlparse(response.geturl()).path)[
                -1
            ]
            if url_ext:
                location = "%s%s" % (location, url_ext)

        f = open(location, "wb")
        try:
            f.write(response.read())
        finally:
            f.close()
    except Exception as e:
        raise TankError(
            "Could not download contents of url '%s'. Error reported: %s" % (url, e)
        )

    return location


def __setup_sg_auth_and_proxy(sg):
    """
    Borrowed from the Shotgun Python API, setup urllib2 with a cookie for authentication on
    Shotgun instance.

    Looks up session token and sets that in a cookie in the :mod:`urllib2` handler. This is
    used internally for downloading attachments from the Shotgun server.

    :param sg: Shotgun API instance
    """
    # Importing this module locally to reduce clutter and facilitate clean up when/if this
    # functionality gets ported back into the Shotgun API.
    from tank_vendor.six.moves import http_cookiejar

    sid = sg.get_session_token()
    cj = http_cookiejar.LWPCookieJar()
    c = http_cookiejar.Cookie(
        "0",
        "_session_id",
        sid,
        None,
        False,
        sg.config.server,
        False,
        False,
        "/",
        True,
        False,
        None,
        True,
        None,
        None,
        {},
    )
    cj.set_cookie(c)
    cookie_handler = urllib.request.HTTPCookieProcessor(cj)
    if sg.config.proxy_handler:
        opener = urllib.request.build_opener(sg.config.proxy_handler, cookie_handler)
    else:
        opener = urllib.request.build_opener(cookie_handler)
    urllib.request.install_opener(opener)


def download_and_unpack_attachment(
    sg, attachment_id, target, retries=5, auto_detect_bundle=False
):
    """
    Downloads the given attachment from Shotgun, assumes it is a zip file
    and attempts to unpack it into the given location.

    :param sg: Shotgun API instance
    :param attachment_id: Attachment to download
    :param target: Folder to unpack zip to. if not created, the method will
                   try to create it.
    :param retries: Number of times to retry before giving up
    :param auto_detect_bundle: Hints that the attachment contains a toolkit bundle
        (config, app, engine, framework) and that this should be attempted to be
        detected and unpacked intelligently. For example, if the zip file contains
        the bundle in a subfolder, this should be correctly unfolded.
    :raises: ShotgunAttachmentDownloadError on failure
    """
    # NOTE Downloading by attachment ID is deprecated in the Shotgun API.
    # We should avoid using this where possible.
    return _download_and_unpack(
        sg, target, retries, auto_detect_bundle, attachment_id=attachment_id
    )


def download_and_unpack_url(sg, url, target, retries=5, auto_detect_bundle=False, headers=None):
    """
    Downloads the content from the provided url, assumes it is a zip file
    and attempts to unpack it into the given location.

    :param sg: Shotgun API instance
    :param url: The url to download from
    :param target: Folder to unpack zip to. if not created, the method will
                   try to create it.
    :param retries: Number of times to retry before giving up
    :param auto_detect_bundle: Hints that the attachment contains a toolkit bundle
        (config, app, engine, framework) and that this should be attempted to be
        detected and unpacked intelligently. For example, if the zip file contains
        the bundle in a subfolder, this should be correctly unfolded.
    :raises: ShotgunAttachmentDownloadError on failure
    """
    return _download_and_unpack(sg, target, retries, auto_detect_bundle, url=url, headers=headers or {})


@LogManager.log_timing
def _download_and_unpack(
    sg, target, retries, auto_detect_bundle, attachment_id=None, url=None, headers=None
):
    """
    Downloads the given attachment from Shotgun if an attachment ID is provided,
    otherwise downloads the content from the provided url.  Assumes the downloaded
    file is a zip file and attempts to unpack it into the given location.

    :param sg: Shotgun API instance
    :param target: Folder to unpack zip to. if not created, the method will
                   try to create it.
    :param retries: Number of times to retry before giving up
    :param auto_detect_bundle: Hints that the attachment contains a toolkit bundle
        (config, app, engine, framework) and that this should be attempted to be
        detected and unpacked intelligently. For example, if the zip file contains
        the bundle in a subfolder, this should be correctly unfolded.
    :param attachment_id: Attachment to download
    :param url: The url to download from
    :raises: ShotgunAttachmentDownloadError on failure
    """
    # @todo: progress feedback here - when the PTR api supports it!
    # sometimes people report that this download fails (because of flaky connections etc)
    # engines can often be 30-50MiB - as a quick fix, just retry the download if it fails

    attempt = 0
    done = False
    invalid_zip_file = False

    while not invalid_zip_file and not done and attempt < retries:

        zip_tmp = os.path.join(tempfile.gettempdir(), "%s_tank.zip" % uuid.uuid4().hex)
        try:
            time_before = time.time()
            if attachment_id:
                log.debug("Downloading attachment id %s..." % attachment_id)
                bundle_content = sg.download_attachment(attachment_id)
                log.debug("Download complete. Saving into %s" % zip_tmp)
                with open(zip_tmp, "wb") as fh:
                    fh.write(bundle_content)
            elif url:
                log.debug("Downloading content of url %s..." % url)
                download_url(sg, url, zip_tmp, headers=headers or {})
            else:
                raise ValueError(
                    "A value is required for one of kwargs `url` or `attachment_id`"
                )

            file_size = os.path.getsize(zip_tmp)

            # log connection speed
            time_to_download = time.time() - time_before
            if time_to_download:
                # In downloads from localhost (including during unit tests)
                # downloads can be immediate.  In this case, we won't try to log
                # download speed.
                broadband_speed_bps = file_size * 8.0 / time_to_download
                broadband_speed_mibps = broadband_speed_bps / (1024 * 1024)
                log.debug("Download speed: %4f Mbit/s" % broadband_speed_mibps)

            log.debug("Unpacking %s bytes to %s..." % (file_size, target))
            filesystem.ensure_folder_exists(target)
            try:
                unzip_file(zip_tmp, target, auto_detect_bundle)
            except zipfile.BadZipfile:
                invalid_zip_file = True

        except Exception as e:
            if attachment_id:
                log.warning(
                    "Attempt %s: Attachment download of id %s from %s failed: %s"
                    % (attempt, attachment_id, sg.base_url, e)
                )
            elif url:
                log.warning(
                    "Attempt %s: Download of content of url %s failed: %s"
                    % (attempt, url, e)
                )
            else:
                raise
            attempt += 1
            # sleep 500ms before we retry
            time.sleep(0.5)
        else:
            done = True
        finally:
            # remove zip file
            filesystem.safe_delete_file(zip_tmp)

    if invalid_zip_file:
        # the attachment in shotgun could not be unpacked
        if attachment_id:
            raise ShotgunAttachmentDownloadError(
                "PTR attachment with id %s is not a zip file!" % attachment_id
            )
        else:
            raise ShotgunAttachmentDownloadError(
                "Content of url %s is not a zip file!" % url
            )
    elif not done:
        # we couldn't download for some reason
        raise ShotgunAttachmentDownloadError(
            "Failed to download from '%s' after %s retries. See error log for details."
            % (sg.base_url, retries)
        )

    else:
        log.debug("Attachment download and unpack complete.")
