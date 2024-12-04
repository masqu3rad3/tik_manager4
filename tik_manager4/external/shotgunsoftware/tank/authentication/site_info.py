# Copyright (c) 2023 Autodesk.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


import time

from . import utils

from tank_vendor import shotgun_api3

from .. import LogManager

logger = LogManager.get_logger(__name__)


# Cache the servers infos for 30 seconds.
INFOS_CACHE_TIMEOUT = 30
# This is a global state variable. It is used to cache information about the Shotgun servers we
# are interacting with. This is purely to avoid making multiple calls to the servers which would
# yield back the same information. (That info is relatively constant on a given server)
# Should this variable be cleared when doing a Python Core swap, it is not an issue.
# The side effect would be an additional call to the Shotgun site.
INFOS_CACHE = {}


def _get_site_infos(url, http_proxy=None):
    """
    Get and cache the desired site infos.

    :param url:            Url of the site to query.
    :param http_proxy:     HTTP proxy to use, if any.

    :returns:   A dictionary with the site infos.
    """

    # Checks if the information is in the cache, is missing or out of date.
    if url not in INFOS_CACHE or (
        (time.time() - INFOS_CACHE[url][0]) > INFOS_CACHE_TIMEOUT
    ):
        # Temporary shotgun instance, used only for the purpose of checking
        # the site infos.
        #
        # The constructor of Shotgun requires either a username/login or
        # key/scriptname pair or a session_token. The token is only used in
        # calls which need to be authenticated. The 'info' call does not
        # require authentication.
        http_proxy = utils.sanitize_http_proxy(http_proxy).netloc
        if http_proxy:
            logger.debug("Using HTTP proxy to connect to the PTR server: %s", http_proxy)

        logger.info("Infos for site '%s' not in cache or expired", url)
        sg = shotgun_api3.Shotgun(
            url, session_token="dummy", connect=False, http_proxy=http_proxy
        )
        # Remove delay between attempts at getting the site info.  Since
        # this is called in situations where blocking during multiple
        # attempts can make UIs less responsive, we'll avoid sleeping.
        # This change was introduced after delayed retries were added in
        # python-api v3.0.41
        sg.config.rpc_attempt_interval = 0
        infos = sg.info()

        INFOS_CACHE[url] = (time.time(), infos)
    else:
        logger.info("Infos for site '%s' found in cache", url)

    return INFOS_CACHE[url][1]


class SiteInfo(object):
    def __init__(self):
        self._url = None
        self._infos = {}

    def reload(self, url, http_proxy=None):
        """
        Load the site information into the instance.

        We want this method to fail as quickly as possible if there are any
        issues. Failure is not considered critical, thus known exceptions are
        silently ignored. At the moment this method used by the GUI show/hide
        some of the input fields and by the console authentication to select the
        appropriate authentication method.

        :param url:            Url of the site to query.
        :param http_proxy:     HTTP proxy to use, if any.
        """
        # Check for valid URL
        url_items = utils.urlparse.urlparse(url)
        if (
            not url_items.netloc
            or url_items.netloc in "https"
            or url_items.scheme not in ["http", "https"]
        ):
            logger.debug("Invalid Flow Production Tracking URL %s" % url)
            return

        infos = {}
        try:
            infos = _get_site_infos(url, http_proxy)
        # pylint: disable=broad-except
        except Exception as exc:
            # Silently ignore exceptions
            logger.debug("Unable to connect with %s, got exception '%s'", url, exc)
            return

        self._url = url
        self._infos = infos

        logger.debug("Site info for {url}".format(url=self._url))
        logger.debug(
            "  user_authentication_method: {value}".format(
                value=self.user_authentication_method,
            )
        )
        logger.debug(
            "  unified_login_flow_enabled: {value}".format(
                value=self.unified_login_flow_enabled,
            )
        )
        logger.debug(
            "  authentication_app_session_launcher_enabled: {value}".format(
                value=self.app_session_launcher_enabled,
            )
        )

    @property
    def user_authentication_method(self):
        """
        Get the user authentication method for site.

        :returns:   A string, such as 'default', 'ldap', 'saml' or 'oxygen',
                    indicating the mode used.
                    None is returned when the information is unavailable or we
                    could not reach the site.
        """

        return self._infos.get("user_authentication_method")

    @property
    def autodesk_identity_enabled(self):
        """
        Check to see if the web site uses Autodesk Identity.

        :returns:   A boolean indicating if Autodesk Identity has been enabled or not.
        """
        return self.user_authentication_method == "oxygen"

    @property
    def sso_enabled(self):
        """
        Check to see if the web site uses sso.

        :returns:   A boolean indicating if SSO has been enabled or not.
        """
        return self.user_authentication_method == "saml2"

    @property
    def unified_login_flow_enabled(self):
        """
        Check to see if the web site uses the unified login flow.

        This setting appeared in the Shotgun 7.X serie, being rarely enabled.
        It became enabled by default starting at Shotgun 8.0

        :returns:   A boolean indicating if the unified login flow is enabled or not.
        """

        return self._infos.get("unified_login_flow_enabled", False)

    @property
    def app_session_launcher_enabled(self):
        """
        Check to see if the PTR site has the App Session Launcher authentication
        enabled.

        This setting appeared in the Shotgun 8.50 serie, being rarely disabled.

        :returns:   A boolean indicating if the App Session Launcher is enabled
                    or not.
        """

        return self._infos.get("authentication_app_session_launcher_enabled", False)
