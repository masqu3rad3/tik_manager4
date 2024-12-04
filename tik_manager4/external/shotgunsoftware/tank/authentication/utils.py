# Copyright (c) 2023 Autodesk.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


# For Python 2/3 compatibility without a dependency on six, we'll just try
# to import as in Python 2, and fall back to Python 3 locations if the imports
# fail.
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


from .. import LogManager

logger = LogManager.get_logger(__name__)


def sanitize_http_proxy(http_proxy):
    """
    Returns a parsed url (a la urlparse).

    We want to support both the proxy notation expected by
    Shotgun:                      username:password@hostname:port (a.k.a. netloc)
    Qt's QtNetwork.QNetworkProxy: scheme://username:password@hostname:port (a.k.a. scheme://netloc)

    :param http_proxy: URL of the proxy. If the URL does not start with a scheme,
                       'http://' will be automatically appended before being parsed.

    :returns: A 6-tuple of the different URL components. See urlparse.urlparse.
    """
    http_proxy = http_proxy or ""
    http_proxy = http_proxy.lower().strip()

    if http_proxy and not (
        http_proxy.startswith("http://") or http_proxy.startswith("https://")
    ):
        logger.debug("Assuming the proxy to be HTTP")
        alt_http_proxy = "http://%s" % http_proxy
        parsed_url = urlparse.urlparse(alt_http_proxy)
        # We want to ensure that the resulting URL is valid.
        if parsed_url.netloc:
            http_proxy = alt_http_proxy

    return urlparse.urlparse(http_proxy)
