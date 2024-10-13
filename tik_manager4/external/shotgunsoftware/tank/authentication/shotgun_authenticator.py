# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""PTR Authenticator."""

from .sso_saml2 import has_sso_info_in_cookies, has_unified_login_flow_info_in_cookies
from . import interactive_authentication
from . import user
from . import user_impl
from . import session_cache
from .errors import IncompleteCredentials
from .defaults_manager import DefaultsManager
from .. import LogManager

logger = LogManager.get_logger(__name__)


class ShotgunAuthenticator(object):
    """
    The ShotgunAuthenticator is the central object in the Shotgun authentication
    module. It helps you with authentication and login and makes it easy to
    create and maintain a shotgun connection so that it belongs to a given user.
    It also helps store who the current user is, so that users don't have to log
    in over and over again, but only when needed.

    A simple use case scenario would look something like this::

        # create an authenticator
        sa = ShotgunAuthenticator()

        # Get a user object. If the authenticator system has already
        # stored a default user belonging to a default shotgun site,
        # it will simply return this. Otherwise, it will pop up a UI
        # asking the user to log in.
        user = sa.get_user()

        # now the user object can be used to generate an authenticated
        # Shotgun connection.
        sg =  user.create_sg_connection()

        # This connection will automatically monitor itself and in the
        # case the user credentials (session token) that the user object
        # encapsulates expires or become invalid, the shotgun connection
        # instance will automatically pop up a UI, asking the user
        # to type in their password. This typically happens after
        # 24 hours of inactivity.

    In addition to the simple code sample, there are a few more concepts:

    - User objects are serializable, meaning that you can pass one from
      one process to another, allowing you to maintain an experience where
      a user is authenticated across multiple applications. This is useful
      if you for example want to launch RV from Maya or Maya from the
      PTR desktop app.

    - The authenticator maintains the concept of a default user - which
      can be used in order to present good defaults in UIs as well as
      headless script based authentication flows.

    - The API provides methods for authentication where client code
      can request that the user is prompted to log in.

    - On the backend, a defaults manager can be specified which implements
      the logic for how various settings are to be stored. This makes
      it possible to easily customize the behavior of the authenticator
      to work in different scenarios.

    For more information, please see the individual methods below.
    """

    def __init__(self, defaults_manager=None):
        """
        Constructor

        :param defaults_manager: A DefaultsManager object that defines the basic
                                 behavior of this authenticator. If omitted,
                                 the default, built-in DefaultsManager will be
                                 used.
        """
        self._defaults_manager = defaults_manager or DefaultsManager()

    def clear_default_user(self):
        """
        Removes the default user's credentials from disk for the default host. The
        next time the ShotgunAuthenticator.get_default_user() method is called,
        None will be returned.

        :returns: If a user was cleared, the user object is returned, None otherwise.
        """
        try:
            user = self.create_session_user(
                host=self._defaults_manager.get_host(),
                login=self._defaults_manager.get_login(),
                http_proxy=self._defaults_manager.get_http_proxy(),
            )
            session_cache.delete_session_data(user.host, user.login)
            return user
        except IncompleteCredentials:
            # Not all credentials were found, so there is no default user.
            return None

    def get_user_from_prompt(
        self, host=None, login=None, http_proxy=None, is_host_fixed=None
    ):
        """
        Display a UI prompt (QT based UI if possible but may fall back on console)

        The DefaultsManager is called to pre-fill the host, login name, http_proxy and is_host_fixed if not provided.

        :param host: Shotgun host to log in to. If None, the default host will be used.
        :param login: Shotgun user login. If None, the default login will be used.
        :param http_proxy: Shotgun proxy to use. If None, the default http proxy will be used.
        :param is_host_fixed: Weither the host is fixed or not. If None, the default value will be used.

        :raises AuthenticationCancelled: If the user cancels the authentication process,
                                         an AuthenticationCancelled is thrown.

        :returns: The SessionUser based on the login information provided.
        """
        (
            host,
            login,
            session_token,
            session_metadata,
        ) = interactive_authentication.authenticate(
            host or self._defaults_manager.get_host(),
            login or self._defaults_manager.get_login(),
            http_proxy or self._defaults_manager.get_http_proxy(),
            is_host_fixed or self._defaults_manager.is_host_fixed(),
        )
        return self.create_session_user(
            login=login,
            session_token=session_token,
            host=host,
            http_proxy=self._defaults_manager.get_http_proxy(),
            session_metadata=session_metadata,
        )

    def create_session_user(
        self,
        login,
        session_token=None,
        password=None,
        host=None,
        http_proxy=None,
        session_metadata=None,
    ):
        """
        Create a :class:`ShotgunUser` given a set of human user credentials.
        Either a password or session token must be supplied. If a password is supplied,
        a session token will be generated for security reasons.

        :param login: Shotgun user login
        :param session_token: Shotgun session token
        :param password: Shotgun password
        :param host: Shotgun host to log in to. If None, the default host will be used.
        :param http_proxy: Shotgun proxy to use. If None, the default http proxy will be used.
        :param session_metadata: When using Web/SSO, b64encoded browser cookies.

        :returns: A :class:`ShotgunUser` instance.
        """
        # Get the defaults is arguments were None.
        host = host or self._defaults_manager.get_host()
        http_proxy = http_proxy or self._defaults_manager.get_http_proxy()

        # Create a session user
        impl = user_impl.SessionUser(
            host,
            login,
            session_token,
            http_proxy,
            password=password,
            session_metadata=session_metadata,
        )

        # We check for SSO first, because it is possible that we use both the
        # Unified Login Flow and SSO. We specifically want to discriminate a
        # SSO sesssion from others due to the need to renew the claims.
        if session_metadata and has_sso_info_in_cookies(session_metadata):
            return user.ShotgunSamlUser(impl)
        if session_metadata and has_unified_login_flow_info_in_cookies(
            session_metadata
        ):
            return user.ShotgunWebUser(impl)
        return user.ShotgunUser(impl)

    def create_script_user(self, api_script, api_key, host=None, http_proxy=None):
        """
        Create an AuthenticatedUser given a set of script credentials.

        :param api_script: Shotgun script user
        :param api_key: Shotgun script key
        :param host: Shotgun host to log in to. If None, the default host will
                     be used.
        :param http_proxy: Shotgun proxy to use. If None, the default http proxy
                           will be used.

        :returns: A :class:`ShotgunUser` derived instance.
        """
        return user.ShotgunUser(
            user_impl.ScriptUser(
                host or self._defaults_manager.get_host(),
                api_script,
                api_key,
                http_proxy or self._defaults_manager.get_http_proxy(),
            )
        )

    def get_default_host(self):
        """
        Returns the host from the defaults manager.

        :returns: The default host string.
        """
        return self._defaults_manager.get_host()

    def get_default_http_proxy(self):
        """
        Returns the HTTP proxy from the defaults manager.

        :returns: The default http proxy string.
        """
        return self._defaults_manager.get_http_proxy()

    def get_default_user(self):
        """
        Returns the default user from the defaults manager.

        :returns: A :class:`ShotgunUser` derived instance if available, None otherwise.
        """
        # Get the credentials
        credentials = self._defaults_manager.get_user_credentials()

        # There is no default user.
        if not credentials:
            logger.debug("No default user found.")
            return None

        # If this looks like an api user, delegate to create_script_user.
        # If some of the arguments are missing, don't worry, create_script_user
        # will take care of it.
        if "api_script" in credentials or "api_key" in credentials:
            return self.create_script_user(
                api_script=credentials.get("api_script"),
                api_key=credentials.get("api_key"),
                host=credentials.get("host"),
                http_proxy=credentials.get("http_proxy"),
            )
        # If this looks like a session user, delegate to create_session_user.
        # If some of the arguments are missing, don't worry, create_session_user
        # will take care of it.
        elif (
            "login" in credentials
            or "password" in credentials
            or "session_token" in credentials
        ):
            return self.create_session_user(
                login=credentials.get("login"),
                password=credentials.get("password"),
                session_token=credentials.get("session_token"),
                host=credentials.get("host"),
                http_proxy=credentials.get("http_proxy"),
                session_metadata=credentials.get("session_metadata"),
            )
        # We don't know what this is, abort!
        else:
            raise IncompleteCredentials(
                "unknown credentials configuration: %s" % credentials
            )

    def get_user(self):
        """
        This method will always return a valid user. It will first ask for the
        default user to the defaults manager. If none is found, the user will
        be prompted on the command line or from a dialog for their credentials.
        Once the user has entered valid credentials, the default user will be
        updated with these.

        :returns: A :class:`ShotgunUser` derived instance matching the credentials
                  provided.

        :raises: :class:`AuthenticationCancelled` is raised
                 if the user cancelled the authentication.
        """
        # Make sure we don't already have a user logged in through single
        # sign-on or provided by a DefaultsManager-derived instance.
        user = self.get_default_user()
        if user:
            return user

        # Prompt the client for user credentials and connection information
        user = self.get_user_from_prompt()

        # Remember that this user and host are the last settings used for
        # authentication in order to provide single sign-on.
        self._defaults_manager.set_host(user.host)
        self._defaults_manager.set_login(user.login)

        return user
