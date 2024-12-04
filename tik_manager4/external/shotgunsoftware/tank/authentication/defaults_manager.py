# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from . import session_cache
from ..util.user_settings import UserSettings
from ..util.system_settings import SystemSettings


class DefaultsManager(object):
    """
    The defaults manager allows a client of the Shotgun Authenticator class
    to customize various behaviors around data storage and settings.

    By default, when you construct a :class:`ShotgunAuthenticator` object, it will be
    instantiated with a standard defaults manager implementation. This will
    work for most cases - user session credentials will be stored in a file
    on disk and the system maintains a concept of a current user and a current
    host.

    If a setting isn't found, the DefaultsManager will fall back to the value stored inside
    ``toolkit.ini`` See :ref:`centralizing_settings` for more information.

    If, however, you want to implement a custom behavior around how defaults
    are managed, simply derive from this class and pass your custom instance
    to the :class:`ShotgunAuthenticator` object when you construct it.

    :param str fixed_host: Allows to specify the host that will be used for authentication.
        Defaults to ``None``.
    """

    def __init__(self, fixed_host=None):
        self._user_settings = UserSettings()
        self._system_settings = SystemSettings()
        self._fixed_host = fixed_host

    def is_host_fixed(self):
        """
        When doing an interactive login, this indicates if the user can decide
        the host to connect to. In its default implementation, the :class:`DefaultsManager`
        will indicate that the host is not fixed, meaning that the user will be
        presented with an option to pick a site at login time, unless a default
        host was provided during initialization. If that is the case, then this
        method will return ``True``.

        With something like Toolkit, where each project already have a specific
        site association, you typically want to override this to return True,
        indicating to the authenticator not to ask the user which site they want
        to log in to.

        :returns: False if the user should be given an option to decide which host
                  to log in to, True if the host is already predetermined and cannot
                  be changed by the user.
        """
        return self._fixed_host is not None

    def get_host(self):
        """
        The default host is used as a useful starting point when doing
        interactive authentication. When the host is not fixed (see the
        :meth:`is_host_fixed` method), the return value of get_host is what is
        used to implement single sign-on between all Toolkit desktop
        applications (at the moment, tank and Flow Production Tracking).

        The default implementation will return the fixed host if one was provided
        during the initialization. If fixed host was provided, the default
        implementation maintains a concept of a "current host" which will be
        presented as a default to users when they are logging in.

        When the host is fixed, this must return a value and this value will
        be used as an absolute rather than a default suggested to the user.

        :returns: A string containing the default host name.
        """
        return (
            self._fixed_host
            or session_cache.get_current_host()
            or self._user_settings.default_site
        )

    def set_host(self, host):
        """
        Called by the authentication system when a new host has been defined.

        :param host: The new default host.
        """
        # Host is fixed, don't update the default host.
        if self.is_host_fixed():
            return
        session_cache.set_current_host(host)

    def get_http_proxy(self):
        """
        Called by the authentication system when it needs to retrieve the
        proxy settings to use for a Shotgun connection.

        .. note:: If the centralized settings do not specify an HTTP proxy, Toolkit will rely on
            Python's `urllib.getproxies <https://docs.python.org/2/library/urllib.html#urllib.getproxies>`_
            to find an HTTP proxy.

            There is a restriction when looking for proxy information from Mac OS X System Configuration or
            Windows Systems Registry: in these cases, Toolkit does not support the use of proxies
            which require authentication (username and password).

        The returned format will be the same as is being used in the Shotgun API.
        For more information, see the `Shotgun API documentation
        <http://developer.shotgridsoftware.com/python-api/reference.html#shotgun>`_.

        :returns: String containing the default http proxy, None by default.
        """
        if self._user_settings.shotgun_proxy is None:
            return self._system_settings.http_proxy
        else:
            return self._user_settings.shotgun_proxy

    def get_login(self):
        """
        Called by the authentication system when it needs to get a
        value for the login. Typically this is used to populate UI
        fields with defaults.

        :returns: Default implementation returns the login for the
                  currently stored user.
        """
        # Make sure there is a current host. There could be none if no-one has
        # logged in with Toolkit yet.
        if self.get_host():
            return (
                session_cache.get_current_user(self.get_host())
                or self._user_settings.default_login
            )
        else:
            return self._user_settings.default_login

    def get_user_credentials(self):
        """
        Called by the authentication system when it requests a default or current user.

        A dictionary with a login and a session token should be returned, which will
        allow the authentication system to authenticate the user.

        The default implementation maintains a concept where it stores the currently
        authenticated user and its session token and tries to return this if possible,
        effectively meaning that the user will be automatically logged in without having
        to be prompted.

        This is typically subclassed if you want to track the notion of a current
        user in an alternative way or maintain a separate notion of the "current" user,
        separate from the default user maintained by the default implementation.

        Toolkit uses the default implementation and will therefore remember the user's
        credentials across all DCCs and tools.

        :returns: A dictionary either with keys login and session_token in the case
                  of a normal Shotgun User, keys api_script and api_key in the case of a Script
                  User or None in case no credentials could be established.
        """
        if self.get_host() and self.get_login():
            return session_cache.get_session_data(self.get_host(), self.get_login())
        else:
            return None

    def set_login(self, login):
        """
        Called by the authentication system when a new user is being logged in.

        The default implementation maintains a concept of a default user
        (returned via the get_user_credentials) and whenever the login is set
        via this method, the default user will change to be this login instead.

        :param login: login as string
        """
        self._login = login
        session_cache.set_current_user(self.get_host(), login)
