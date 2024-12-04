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
SSO/SAML2 Exceptions.
"""


class SsoSaml2Error(Exception):
    """
    Top level exception for all saml2_sso level runtime errors
    """


class SsoSaml2MultiSessionNotSupportedError(SsoSaml2Error):
    """
    Exception that indicates the cookies contains sets of tokens from mutliple users.
    """


class SsoSaml2MissingQtModuleError(SsoSaml2Error):
    """
    Exception that indicates that a required Qt component is missing.
    """


class SsoSaml2MissingQtCore(SsoSaml2MissingQtModuleError):
    """
    Exception that indicates that the QtCore component is missing.
    """


class SsoSaml2MissingQtGui(SsoSaml2MissingQtModuleError):
    """
    Exception that indicates that the QtGui component is missing.
    """


class SsoSaml2MissingQtNetwork(SsoSaml2MissingQtModuleError):
    """
    Exception that indicates that the QtNetwork component is missing.
    """


class SsoSaml2MissingQtWebKit(SsoSaml2MissingQtModuleError):
    """
    Exception that indicates that the QtWebKit component is missing.
    """


class SsoSaml2IncompletePySide2(SsoSaml2Error):
    """
    Exception that indicates that the version of PySide2 used is incomplete or obsolete.
    """
