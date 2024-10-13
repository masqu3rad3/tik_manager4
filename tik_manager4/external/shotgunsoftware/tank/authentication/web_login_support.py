"""
Web-based login is required when the target Shotgun site uses SSO or Autodesk
Identity for authentication.

This flag will control if the Unified Login Flow is to be used or not. By
default, it will not be used.

Unfortunately, not all DCCs/Scripts/Applications that use the Toolkit have all
the required dependencies to fully support Web-based authentication and renewal.
This can be a problem for programs not started by the PTR desktop app or if
the PTR desktop app is closed after. When the program attemps to authenticate
or renew a session against a Shotgun site that uses SSO/Autodesk Identity, it
will fail to do so and will not provide meaningful feedback to the user.

The requirements are:
- Full support for WebKit/WebEngine with access to the cookie store,
- SSL support
- TLS v1.2 support
- NTLM patch

Some of these could be checked at run-time, but others (TLS v1.2 support,
NTLM patch) are more difficult to detect.

Unless this flag is explicitely set to True by the enclosing program, we
will take for granted that the full web login flow is not supported.

WARNING: while SSO login has been supported since tk-core 0.18.151/Shotgun
Desktop 1.5.3, it was possible for a DCC to be unable to authenticate or renew
a session. This flag will not change that behaviour.

At this time, only the PTR desktop app and Create app fully support the
Web based authentication.
"""

# This global variable is meant to affect the way the authentication is
# handled by the toolkit-using application.
# Initially, the only clients that will modify this value will be the
# PTR desktop app and Shotgun Create.
# This is the way for an application to clearly state: yes I support the ULF.
# This value will properly be propagated across a core swap if the new core
# also defines this variable.
shotgun_authenticator_support_web_login = False


def set_shotgun_authenticator_support_web_login(enable):
    """
    Setting this flag to True indicates that the DCC/Script/Application is
    able to fully support the Unified Login Flow.

    :param enable: Bool indicating if the Unified Login Flow is supported.
    """
    global shotgun_authenticator_support_web_login
    shotgun_authenticator_support_web_login = enable


def get_shotgun_authenticator_support_web_login():
    """
    Indicates the support for the Unified Login Flow.

    :returns: Bool indicating support for the Unified Login Flow.
    """
    global shotgun_authenticator_support_web_login
    return shotgun_authenticator_support_web_login
