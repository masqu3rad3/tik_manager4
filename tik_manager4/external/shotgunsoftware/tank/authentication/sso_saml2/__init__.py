# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
"""
This module offers different SSO integration warppers for Shotgun.
"""

# Exceptions
from .core.errors import (  # noqa
    SsoSaml2Error,
    SsoSaml2IncompletePySide2,
    SsoSaml2MissingQtCore,
    SsoSaml2MissingQtGui,
    SsoSaml2MissingQtModuleError,
    SsoSaml2MissingQtNetwork,
    SsoSaml2MissingQtWebKit,
    SsoSaml2MultiSessionNotSupportedError,
)

# Classes
from .sso_saml2 import SsoSaml2  # noqa

from .sso_saml2_toolkit import SsoSaml2Toolkit  # noqa

# Functions
from .utils import (  # noqa
    get_saml_claims_expiration,
    has_sso_info_in_cookies,
    has_unified_login_flow_info_in_cookies,
)

from .core.utils import (  # noqa
    get_logger,
    set_logger_parent,
)
