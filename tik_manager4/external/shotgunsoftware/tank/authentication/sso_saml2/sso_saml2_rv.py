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
Integration with Shotgun RV.
"""

import json

from .sso_saml2 import SsoSaml2  # noqa


class SsoSaml2Rv(SsoSaml2):
    """
    This class provides a minimal interface to support SSO authentication.
    """

    def __init__(self, window_title=None, qt_modules=None):
        """
        Create a SSO login dialog, using a Web-browser like environment.

        :param window_title: Title to use for the window.
        :param qt_modules:   a dictionnary of required Qt modules.
                             For Qt4/PySide, we require modules QtCore, QtGui, QtNetwork and QtWebKit

        :returns: The SsoSaml2 oject.
        """
        super(SsoSaml2Rv, self).__init__(window_title, qt_modules)

    def on_sso_login_cancel(self, event):
        """
        Called to cancel an ongoing login attempt.

        :param event: RV event. Not used.
        """
        self._logger.debug("Cancel SSO login attempt")

        # We only need to cancel if there is login attempt currently being made.
        if self.is_handling_event():
            self.stop_session_renewal()
            self.resolve_event(end_session=True)
        self._dialog.accept()

    def on_sso_enable_renewal(self, event):
        """
        Called when enabling automatic SSO session renewal.

        A new session will be created if there is not already a current one.
        This will be in the case of the automatic (and successful)
        authentication at the startup of the application.

        :param event: Json encoded document describing the RV event.
        """
        self._logger.debug("SSO automatic renewal enabled")

        contents = json.loads(event.contents())

        if self._session is None:
            self.start_new_session(
                {
                    "host": contents["params"]["site_url"],
                    "cookies": contents["params"]["cookies"],
                }
            )
        self.start_sso_renewal()

    def on_sso_disable_renewal(self, event):
        """
        Called to disable automatic session renewal.

        This will be required when switching to a new connection (where the new
        site may not using SSO) or at the close of the application.
        """
        self._logger.debug("SSO automatic renewal disabled")
        self.stop_session_renewal()
