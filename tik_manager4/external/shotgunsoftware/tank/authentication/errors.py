# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
All custom exceptions that this module emits are defined here.
"""

# @todo - what should ShotgunAuthenticationError derive from? TankError?


class ShotgunAuthenticationError(Exception):
    """
    Base class for all exceptions coming out from this module.
    """


class AuthenticationError(ShotgunAuthenticationError):
    """
    Thrown when credentials are rejected by the server.
    """


class IncompleteCredentials(ShotgunAuthenticationError):
    """
    Thrown when credentials are provided but are incomplete.
    """

    def __init__(self, msg):
        """
        :param str msg: Reason why the credentials are incomplete.
        """
        ShotgunAuthenticationError.__init__(self, "Incomplete credentials: %s" % msg)


class AuthenticationCancelled(ShotgunAuthenticationError):
    """
    Thrown when the user cancels authentication or session renewal.
    """

    def __init__(self):
        ShotgunAuthenticationError.__init__(
            self, "Authentication was cancelled by the user."
        )


class UnresolvableUser(ShotgunAuthenticationError):
    """
    Thrown when Toolkit is not able to resolve a user.
    """

    def __init__(self, nice_user_type, user_type, key_name, key_value):
        super(UnresolvableUser, self).__init__(
            "The {0} named '{3}' could not be resolved. Check if the "
            "permissions for the current user are hiding the field '{1}.{2}'.".format(
                nice_user_type, user_type, key_name, key_value
            )
        )


class UnresolvableHumanUser(UnresolvableUser):
    """
    Thrown when Toolkit is not able to resolve a human user.
    """

    def __init__(self, login):
        """
        :param str login: ``login`` field value of the ``HumanUser`` that could not be resolved.
        """
        super(UnresolvableHumanUser, self).__init__(
            "person", "HumanUser", "login", login
        )


class UnresolvableScriptUser(UnresolvableUser):
    """
    Thrown when Toolkit is not able to resolve a human user.
    """

    def __init__(self, script_name):
        """
        :param str script_name: ``firstname`` field value of the ``ApiUser`` that could not be resolved.
        """
        super(UnresolvableScriptUser, self).__init__(
            "script", "ApiUser", "firstname", script_name
        )


class ConsoleLoginNotSupportedError(ShotgunAuthenticationError):
    """
    Thrown when attempting to use Username/Password pair to login onto
    an SSO-enabled site.
    """

    def __init__(self, url, site_auth_type="Single Sign-On"):
        """
        :param str url: Url of the site where login was attempted.
        :param str site_auth_type: type of authentication, e.g. SSO, Identity.
                                   The default value is for backward compatibility.
        """
        super(ConsoleLoginNotSupportedError, self).__init__(
            "Authentication using username/password is not supported on "
            "the console %s for sites using %s." % (url, site_auth_type)
        )


# For backward compatibility.
ConsoleLoginWithSSONotSupportedError = ConsoleLoginNotSupportedError
