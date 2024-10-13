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
Integration with Shotgun Toolkit API.
"""

# pylint: disable=line-too-long
# pylint: disable=protected-access

from .sso_saml2 import SsoSaml2  # noqa


class SsoSaml2Toolkit(SsoSaml2):
    """
    This class provides a minimal interface to support SSO authentication.
    """

    def get_session_data(self):
        """
        Get a mimimal subset of session data, for the Shotgun Toolkit.

        :returns: A tuple of the hostname, user_id, session_id and cookies.
        """
        return (
            self._core._session.host,
            self._core._session.user_id,
            self._core._session.session_id,
            self._core._session.cookies,
        )
