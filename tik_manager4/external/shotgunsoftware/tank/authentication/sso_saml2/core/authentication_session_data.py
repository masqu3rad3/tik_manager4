# Copyright (c) 2017 Autodesk.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
"""
Authentication Session abstraction.
"""

# pylint: disable=too-many-instance-attributes


class AuthenticationSessionData(object):
    """
    Holds session information.

    A session object holds information coming from both the toolkit current session
    and from the QWebView used to login/renew session from our SSO enabled site.

    Attributes:
        cookies:            A string of the base64 encoded json string of raw
                            cookies.
        crsf_value:         A string for the crsf value.
        csrf_key:           A string for the crsf key.
        error:              A string which describe the error encountered.
        host:               A string for the hostname.
        http_proxy:         URL of the proxy.
        product:            A string for the product (used at login).
        session_expitation: An int in seconds for the UTC time of expiration.
        session_id:         A string for the session id.
        user_id:            A string for the user id.
    """

    def __init__(self, settings=None):
        """
        Constructor.

        :param settings: Dictionary of element to add to the settings.
                         Non-used key/value pairs will be silently discarded.
        """
        settings = settings or {}
        self._cookies = None
        self._csrf_key = None
        self._csrf_value = None
        self._error = None
        self._host = None
        self._http_proxy = None
        self._product = None
        self._session_expiration = None
        self._session_id = None
        self._user_id = None
        self.merge_settings(settings)

    def __repr__(self):
        """
        Returns a string reprensentation of the session. For debugging purposes.

        :returns: A string containing all of the session data.
        """
        params = {}
        for key, value in vars(self).items():
            if value is not None:
                params[key] = value

        return "<Session %s>" % params

    def merge_settings(self, settings):
        """
        Merge new settings with existing ones.

        :param settings: Dictionary of element to merge to the settings.
                         Non-used key/value pairs will be silently discarded.
        """
        for key, value in settings.items():
            _key = "_%s" % key
            if _key in vars(self):
                setattr(self, _key, value)

    @property
    def cookies(self):
        """
        Getter for the session cookies.

        :returns: An encoded string describing the session cookies. Not meant
                  for public consumption.
        """
        return str(self._cookies or "")

    @cookies.setter
    def cookies(self, value):
        """
        Setter for the session cookies.

        :param value: An encoded string describing the session cookies.
        """
        self._cookies = value

    @property
    def csrf_key(self):
        """
        Getter for the session csrf_key.

        :returns: The key name of the CRSF token, which will include a unique ID.
                  The ID corresponds to the Shogun user ID.
        """
        return str(self._csrf_key or "")

    @csrf_key.setter
    def csrf_key(self, value):
        """
        Setter for the session csrf_key.

        :param value: The key name of the CRSF token, which will include a unique ID.
                      The ID corresponds to the Shogun user ID.
        """
        self._csrf_key = value

    @property
    def csrf_value(self):
        """
        Getter for the session csrf_value.

        :returns: The value of the Cross-Site Request Forgery token.
        """
        return str(self._csrf_value or "")

    @csrf_value.setter
    def csrf_value(self, value):
        """
        Setter for the session csrf_value.

        :param value: The value of the Cross-Site Request Forgery token.
        """
        self._csrf_value = value

    @property
    def error(self):
        """
        Getter for the session error, if any.

        :returns: The error string if any, an empty string otherwise.
        """
        return str(self._error or "")

    @error.setter
    def error(self, value):
        """
        Setter for the session error.

        :param value: The error string if any, an empty string otherwise.
        """
        self._error = value

    @property
    def host(self):
        """
        Getter for the session hostname.

        :returns: The session hostname.
        """
        return str(self._host or "")

    @host.setter
    def host(self, value):
        """
        Setter for the session hostname.

        :param value: The session hostname.
        """
        self._host = value

    @property
    def http_proxy(self):
        """
        Getter for the session http proxy.

        :returns: The session http proxy.
        """
        return str(self._http_proxy or "")

    @http_proxy.setter
    def http_proxy(self, value):
        """
        Setter for the session http proxy.

        :param value: The session http proxy.
        """
        self._http_proxy = value

    @property
    def product(self):
        """
        Getter for the session product name.

        :returns: The session product name, or "undefined".
        """
        return str(self._product or "undefined")

    @product.setter
    def product(self, value):
        """
        Setter for the session product name.

        :param value: The session product name (e.g. "rv", "shotgun", etc.).
        """
        self._product = value

    @property
    def session_expiration(self):
        """
        Getter for the session expiration.

        :returns: The session expiration, in seconds since January 1st 1970 UTC.
        """
        return int(self._session_expiration or 0)

    @session_expiration.setter
    def session_expiration(self, value):
        """
        Setter for the session expiration.

        :param value: The session expiration, in seconds since January 1st 1970 UTC.
        """
        self._session_expiration = int(value)

    @property
    def session_id(self):
        """
        Getter for the session id.

        :returns: The session unique id.
        """
        return str(self._session_id or "")

    @session_id.setter
    def session_id(self, value):
        """
        Setter for the session id.

        :param value: The session unique id.
        """
        self._session_id = value

    @property
    def user_id(self):
        """
        Getter for the session user id.

        :returns: The session user id.
        """
        return str(self._user_id or "")

    @user_id.setter
    def user_id(self, value):
        """
        Setter for the session user id.

        :param value: The session user id.
        """
        self._user_id = value
