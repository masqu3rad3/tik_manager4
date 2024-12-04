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
SSO/SAML2 Utility functions.
"""

# pylint: disable=unused-import

from .core.utils import (  # noqa
    get_saml_claims_expiration,
    get_session_expiration,
    _decode_cookies,
    _get_shotgun_user_id
)


def has_unified_login_flow_info_in_cookies(encoded_cookies):
    """
    Indicate if the Unified Login Flow is being used from the Shotgun cookies.

    :param encoded_cookies: An encoded string representing the cookie jar.

    :returns: True if there are ULF infos in the cookies.
    """
    return get_session_expiration(encoded_cookies) is not None


def has_sso_info_in_cookies(encoded_cookies):
    """
    Indicate if SSO is being used from the Shotgun cookies.

    :param encoded_cookies: An encoded string representing the cookie jar.

    :returns: True if there are SSO-related infos in the cookies.
    """
    return get_saml_claims_expiration(encoded_cookies) is not None
