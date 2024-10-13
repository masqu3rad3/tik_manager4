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
SSO/SAML2 Core utility functions.
"""

# pylint: disable=line-too-long

import sys
import base64
import binascii
import logging
import urllib

# For Python 2/3 compatibility without a dependency on six, we'll just try
# to import as in Python 2, and fall back to Python 3 locations if the imports
# fail.
try:
    from urllib import unquote_plus
except ImportError:
    from urllib.parse import unquote_plus
try:
    from http.cookies import SimpleCookie
except ImportError:
    from Cookie import SimpleCookie


from .errors import SsoSaml2MultiSessionNotSupportedError


def get_logger():
    """
    Obtain the logger for this module.

    :returns: The logger instance for this module.
    """
    return logging.getLogger(__name__)


def set_logger_parent(logger_parent):
    """
    Set the logger parent to this module's logger.

    Some client code may want to re-parent this module's logger in order to
    influence the output.

    :param logger_parent: New logger parent.
    """
    logger = get_logger()
    logger.parent = logger_parent


def _decode_cookies(encoded_cookies):
    """
    Extract the cookies from a base64 encoded string.

    :param encoded_cookies: An encoded string representing the cookie jar.

    :returns: A string containing all the cookies.
    """
    decoded_cookies = ""
    if encoded_cookies:
        try:
            decoded_cookies = base64.b64decode(encoded_cookies)
            if not isinstance(decoded_cookies, str):
                # If decoded_cookies is not a string, it's likely we're on
                # Python3, and decoded_cookies is binary.  Try to decode it.
                decoded_cookies = decoded_cookies.decode()
        except (TypeError, binascii.Error) as e:
            # In Python 2 this raises a TypeError, while in 3 it will raise a
            # binascii.Error.  Catch either and handle them the same.
            get_logger().error("Unable to decode the cookies: %s", str(e))
    # Should the decoded cookies be used with SimpleCookie, we strip out the
    # 'Set-Cookie: ' prefix to maintain Python2 and Python3 compatibility.
    # It turns out that the regex to parse cookies has change in SimpleCookie
    # in Python3, causing problems when the prefix was present.
    decoded_cookies = decoded_cookies.replace("Set-Cookie: ", "")
    return decoded_cookies


def _encode_cookies(cookies):
    """
    Extract the cookies from a base64 encoded string.

    :param cookies: A string representing the serialized cookie jar.

    :returns: An encoded string representing the cookie jar.
    """
    PY3 = sys.version_info[0] == 3
    if PY3 and isinstance(cookies, str):
        # On Python 3, encode str to binary before passing it to b64encode.
        cookies = cookies.encode()
    encoded_cookies = base64.b64encode(cookies)
    if PY3:
        # On Python 3, b64encode returns a bytes object that we'll want to
        # decode to a string for compatibility between Python 2 and 3.
        encoded_cookies = encoded_cookies.decode()
    return encoded_cookies


def _get_shotgun_user_id(cookies):
    """
    Returns the id of the user in the shotgun instance, based on the cookies.

    :param cookies: A Cookie.SimpleCookie instance representing the cookie jar.

    :returns: A string user id value, or None.
    """
    user_id = None
    user_domain = None
    for cookie in cookies:
        if cookie.startswith("csrf_token_u"):
            # Shotgun appends the unique numerical ID of the user to the cookie name:
            # ex: csrf_token_u78
            if user_id is not None:
                # For backward compatibility, we support both the old SAML cookies
                # and the new Unified Login Flow cookies. Some information may
                # be present in both formats, under a different cookie name.
                if user_domain == cookies[cookie]["domain"]:
                    continue
                # Should we find multiple cookies with the same prefix, it means
                # that we are using cookies from a multi-session environment. We
                # have no way to identify the proper user id in the lot.
                message = "The cookies for this user seem to come from two different PTR sites: '%s' and '%s'"
                raise SsoSaml2MultiSessionNotSupportedError(
                    message % (user_domain, cookies[cookie]["domain"])
                )
            user_id = cookie[12:]
            user_domain = cookies[cookie]["domain"]
    return user_id


def _get_cookie(encoded_cookies, cookie_name):
    """
    Returns a cookie value based on its name.

    :param encoded_cookies: An encoded string representing the cookie jar.
    :param cookie_name:     The name of the cookie.

    :returns: A string of the cookie value, or None.
    """
    value = None
    cookies = SimpleCookie()
    cookies.load(_decode_cookies(encoded_cookies))
    if cookie_name in cookies:
        value = cookies[cookie_name].value
    return value


def _get_cookie_from_prefix(encoded_cookies, cookie_prefix):
    """
    Returns a cookie value based on a prefix to which we will append the user id.

    :param encoded_cookies: An encoded string representing the cookie jar.
    :param cookie_prefix:   The prefix of the cookie name.

    :returns: A string of the cookie value, or None.
    """
    value = None
    cookies = SimpleCookie()
    cookies.load(_decode_cookies(encoded_cookies))
    key = "%s%s" % (cookie_prefix, _get_shotgun_user_id(cookies))
    if key in cookies:
        value = cookies[key].value
    return value


def get_saml_claims_expiration(encoded_cookies):
    """
    Obtain the expiration time of the saml claims from the Shotgun cookies.

    :param encoded_cookies: An encoded string representing the cookie jar.

    :returns: An int with the time in seconds since January 1st 1970 UTC, or None
    """
    # Shotgun appends the unique numerical ID of the user to the cookie name:
    # ex: shotgun_sso_session_expiration_u78
    saml_claims_expiration = _get_cookie(
        encoded_cookies, "shotgun_current_user_sso_claims_expiration"
    ) or _get_cookie_from_prefix(encoded_cookies, "shotgun_sso_session_expiration_u")
    if saml_claims_expiration is not None:
        saml_claims_expiration = int(saml_claims_expiration)
    return saml_claims_expiration


def get_session_expiration(encoded_cookies):
    """
    Obtain the expiration time of the Shotgun session from the Shotgun cookies.

    :param encoded_cookies: An encoded string representing the cookie jar.

    :returns: An int with the time in seconds since January 1st 1970 UTC, or None if the cookie
              'shotgun_current_session_expiration' is not defined.
    """
    session_expiration = _get_cookie(
        encoded_cookies, "shotgun_current_session_expiration"
    )
    if session_expiration is not None:
        session_expiration = int(session_expiration)
    return session_expiration


def get_user_name(encoded_cookies):
    """
    Obtain the user name from the Shotgun cookies.

    :param encoded_cookies: An encoded string representing the cookie jar.

    :returns: A string with the user name, or None
    """
    # Shotgun appends the unique numerical ID of the user to the cookie name:
    # ex: shotgun_sso_session_userid_u78
    user_name = _get_cookie(
        encoded_cookies, "shotgun_current_user_login"
    ) or _get_cookie_from_prefix(encoded_cookies, "shotgun_sso_session_userid_u")
    if user_name is not None:
        user_name = unquote_plus(user_name)
    return user_name


def get_session_id(encoded_cookies):
    """
    Obtain the session id from the Shotgun cookies.

    :param encoded_cookies: An encoded string representing the cookie jar.

    :returns: A string with the session id, or None
    """
    session_id = None
    cookies = SimpleCookie()
    cookies.load(_decode_cookies(encoded_cookies))
    key = "_session_id"
    if key in cookies:
        session_id = cookies[key].value
    return session_id


def get_csrf_token(encoded_cookies):
    """
    Obtain the csrf token from the Shotgun cookies.

    :param encoded_cookies: An encoded string representing the cookie jar.

    :returns: A string with the csrf token, or None
    """
    # Shotgun appends the unique numerical ID of the user to the cookie name:
    # ex: csrf_token_u78
    return _get_cookie_from_prefix(encoded_cookies, "csrf_token_u")


def get_csrf_key(encoded_cookies):
    """
    Obtain the csrf token name from the Shotgun cookies.

    :param encoded_cookies: An encoded string representing the cookie jar.

    :returns: A string with the csrf token name
    """
    cookies = SimpleCookie()
    cookies.load(_decode_cookies(encoded_cookies))
    # Shotgun appends the unique numerical ID of the user to the cookie name:
    # ex: csrf_token_u78
    return "csrf_token_u%s" % _get_shotgun_user_id(cookies)
