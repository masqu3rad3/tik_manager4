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
Module to support Web login via a web browser and automated session renewal.
"""

# pylint: disable=line-too-long
# pylint: disable=no-self-use
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-statements

import base64
import os
import sys
import time
import urllib

from .authentication_session_data import AuthenticationSessionData
from .errors import (
    SsoSaml2IncompletePySide2,
    SsoSaml2MissingQtCore,
    SsoSaml2MissingQtGui,
    SsoSaml2MissingQtNetwork,
    SsoSaml2MissingQtWebKit,
)
from .utils import (
    _decode_cookies,
    _encode_cookies,
    get_csrf_key,
    get_csrf_token,
    get_logger,
    get_saml_claims_expiration,
    get_session_id,
    get_user_name,
)
from ...utils import sanitize_http_proxy

try:
    from .username_password_dialog import UsernamePasswordDialog
except ImportError:
    # Silently ignore the import error, as we are likely not in a Qt
    # environment.
    UsernamePasswordDialog = None

from tank_vendor.six.moves.urllib.parse import urlencode

# Error messages for events.
HTTP_CANT_CONNECT_TO_SHOTGUN = "Cannot Connect To PTR site."
HTTP_AUTHENTICATE_REQUIRED = "Valid credentials are required."
HTTP_AUTHENTICATE_SSO_NOT_UPPORTED = "SSO not supported or enabled on that site."
HTTP_CANT_AUTHENTICATE_SSO_TIMEOUT = (
    "Time out attempting to authenticate to SSO service."
)
HTTP_CANT_AUTHENTICATE_SSO_NO_ACCESS = (
    "You have not been granted access to the PTR site."
)

# Timer related values.
# @TODO: parametrize these and add environment variable overload.
WATCHDOG_TIMEOUT_MS = 5000
PREEMPTIVE_RENEWAL_THRESHOLD = 0.9
SHOTGUN_SSO_RENEWAL_INTERVAL = 5000

# Some IdP (Identity Providers) will use JavaScript code which makes use of ES6.
# Our Qt4 environment is unfortunately missing some definitions which we need to
# inject prior to running the IdP code.
# The reference for this code is:
#     https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_objects/Function/bind#Polyfill
#
# The redefinition of Array.prototype.splice was required following an update to
# the Okta Sign-In Widget (version 4.2.0). When Babel checks to see if the method
# needs to be polyfilled, it falls into an infinite loop.
FUNCTION_PROTOTYPE_BIND_POLYFILL = """
    // Yes, it does work with `new funcA.bind(thisArg, args)`
    if (!Function.prototype.bind) (function(){
      var ArrayPrototypeSlice = Array.prototype.slice;
      Function.prototype.bind = function(otherThis) {
        if (typeof this !== 'function') {
          // closest thing possible to the ECMAScript 5
          // internal IsCallable function
          throw new TypeError('Function.prototype.bind - what is trying to be bound is not callable');
        }

        var baseArgs= ArrayPrototypeSlice .call(arguments, 1),
            baseArgsLength = baseArgs.length,
            fToBind = this,
            fNOP    = function() {},
            fBound  = function() {
              baseArgs.length = baseArgsLength; // reset to default base arguments
              baseArgs.push.apply(baseArgs, arguments);
              return fToBind.apply(
                     fNOP.prototype.isPrototypeOf(this) ? this : otherThis, baseArgs
              );
            };

        if (this.prototype) {
          // Function.prototype doesn't have a prototype property
          fNOP.prototype = this.prototype;
        }
        fBound.prototype = new fNOP();

        return fBound;
      };
    })();

    // Simply create an alias of splice.
    // This is to get around a Babel bug.
    Array.prototype.splice_copy = Array.prototype.splice;
    Array.prototype.splice = function() {
        return this.splice_copy.apply(this, arguments);
    }
"""

# login paths, used by the Unified Login Flow.
URL_ULF_RENEW_PATH = "/auth/renew"
URL_ULF_LANDING_PATH = "/auth/landing"


def get_renew_path(session, logger):
    """Construct the renew path, leveraging existing environment variables"""
    renew_path = session.host + URL_ULF_RENEW_PATH + "?"
    renew_params = {"product": session.product}
    # When this variable is set, it is passed to Autodesk Identity's login.
    tk_shotgun_default_login = os.getenv("TK_SHOTGRID_DEFAULT_LOGIN")
    # When this variable is set for a SSO domain, skip the initial login page.
    tk_shotgun_sso_domain = sanitize_http_proxy(os.getenv("TK_SHOTGRID_SSO_DOMAIN")).netloc

    # Flow Production Tracking's renew endpoint supports some useful
    # Autodesk Identity params.
    if tk_shotgun_default_login:
        logger.debug("Using default login: %s", tk_shotgun_default_login)
        renew_params["email"] = tk_shotgun_default_login
    if tk_shotgun_sso_domain:
        logger.debug("Using SSO domain: %s", tk_shotgun_sso_domain)
        renew_params["sso_domain"] = tk_shotgun_sso_domain

    renew_path += urlencode(renew_params)
    return renew_path


class SsoSaml2Core(object):
    """Performs PTR Web login and pre-emptive renewal for SSO sessions."""

    def __init__(self, window_title="Web Login", qt_modules=None):
        """
        Create a Web login dialog, using a Web-browser like environment.

        :param window_title: Title to use for the window.
        :param qt_modules:   a dictionnary of required Qt modules.
                             For Qt4/PySide, we require modules QtCore, QtGui, QtNetwork and QtWebKit

        :returns: The SsoSaml2Core oject.
        """
        qt_modules = qt_modules or {}

        self._logger = get_logger()
        self._logger.debug("Constructing SSO dialog: %s", window_title)
        self._developer_mode = False
        if "SHOTGUN_SSO_DEVELOPER_ENABLED" in os.environ:
            self._developer_mode = True

        # pylint: disable=invalid-name
        QtCore = self._QtCore = qt_modules.get("QtCore")  # noqa
        QtGui = self._QtGui = qt_modules.get("QtGui")  # noqa
        QtNetwork = self._QtNetwork = qt_modules.get("QtNetwork")  # noqa
        QtWebKit = self._QtWebKit = qt_modules.get("QtWebKit")  # noqa
        QtWebEngineWidgets = self._QtWebEngineWidgets = qt_modules.get(
            "QtWebEngineWidgets"
        )  # noqa

        if QtCore is None:
            raise SsoSaml2MissingQtCore("The QtCore module is unavailable")

        if QtGui is None:
            raise SsoSaml2MissingQtGui("The QtGui module is unavailable")

        if QtNetwork is None:
            raise SsoSaml2MissingQtNetwork("The QtNetwork module is unavailable")

        if QtWebKit is None and QtWebEngineWidgets is None:
            raise SsoSaml2MissingQtWebKit(
                "The QtWebKit or QtWebEngineWidgets modules are unavailable"
            )

        # If PySide2 is being used, we need to make  extra checks to ensure
        # that needed components are indeed present.
        #
        # The versions of PySide2 are only lightly coupled with the versions
        # of Qt it exposes. It is possible to mix-and-match a very recent Qt5
        # and have a very old version of PySide2. The issue is that it does
        # not necessarily expose to the Python layer all of the classes and
        # methods needed for us to go forward with the Web-based authentication.
        # At the time of this writing, there was these reported situations:
        # - recent and old versions of Flame using PySide2 version '2.0.0~alpha0':
        #     missing the 'cookieStore' method for class QWebEngineProfile
        # - Maya 2017
        #     missing the 'QSslConfiguration' class. Likely compiled without SSL
        #     support.
        if QtWebEngineWidgets and not hasattr(
            QtWebEngineWidgets.QWebEngineProfile, "cookieStore"
        ):
            raise SsoSaml2IncompletePySide2(
                "Missing method QtWebEngineWidgets.QWebEngineProfile.cookieStore()"
            )
        if QtNetwork and not hasattr(QtNetwork, "QSslConfiguration"):
            raise SsoSaml2IncompletePySide2("Missing class QtNetwork.QSslConfiguration")
        class TKWebPageQtWebEngine(QtWebEngineWidgets.QWebEnginePage):
            """
            Wrapper class to better control the behaviour when clicking on links
            in the Qt5 web browser. If we are asked to open a new tab/window, then
            we defer the page to the external browser.
            """

            def __init__(self, profile, parent, developer_mode=False):
                """
                Class Constructor.
                """
                get_logger().debug("TKWebPageQtWebEngine.__init__")
                super(TKWebPageQtWebEngine, self).__init__(profile, parent)
                self._profile = profile
                self._developer_mode = developer_mode

            def __del__(self):
                """
                Class Destructor.
                """
                get_logger().debug("TKWebPageQtWebEngine.__del__")

            def acceptNavigationRequest(self, url, n_type, is_mainframe):
                """
                Overloaded method, to properly control the behaviour of clicking on
                links.
                """
                if self._developer_mode:
                    get_logger().debug(
                        "TKWebPageQtWebEngine.acceptNavigationRequest: %s (%s)",
                        url.toString(),
                        n_type,
                    )

                # A null profile means that a window/tab had to be created to handle
                # this request. So we just farm out the request to the external system
                # browser.
                if self._profile is None:
                    QtGui.QDesktopServices.openUrl(url)
                    return False
                return QtWebEngineWidgets.QWebEnginePage.acceptNavigationRequest(
                    self, url, n_type, is_mainframe
                )

            def createWindow(self, window_type):
                """
                When a link leading to a new window/tab is clicked, this method is
                called.
                """
                get_logger().debug("TKWebPageQtWebEngine.createWindow: %s", window_type)
                # Here we return a new page with no profile, that will be used solely
                # to trigger the call to the external browser.
                return TKWebPageQtWebEngine(None, self.parent())

            def certificateError(self, certificate_error):
                """
                Signal called when the WebEngine detects and incorrect certificate.
                For the time being, we ignore all certificate errors.
                """
                get_logger().debug(
                    "TKWebPageQtWebEngine.certificateError: %s", certificate_error
                )
                return True

        self._event_data = None
        self._sessions_stack = []
        self._session_renewal_active = False

        self._dialog = QtGui.QDialog()
        self._dialog.setWindowTitle(window_title)
        self._dialog.finished.connect(self.on_dialog_closed)

        # This is to ensure that we can resize the window nicely, and that the
        # WebView will follow.
        self._layout = QtGui.QVBoxLayout(self._dialog)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._profile = QtWebEngineWidgets.QWebEngineProfile.defaultProfile()
        self._logger.debug(
            "Initial WebEngineProfile storage location: %s",
            self._profile.persistentStoragePath(),
        )
        self._view = QtWebEngineWidgets.QWebEngineView(self._dialog)
        self._view.setPage(
            TKWebPageQtWebEngine(self._profile, self._dialog, self._developer_mode)
        )
        self._view.page().authenticationRequired.connect(
            self.on_authentication_required
        )

        self._view.urlChanged.connect(self._on_url_changed)
        self._layout.addWidget(self._view)
        self._dialog.resize(800, 600)

        self._logger.debug(
            "We are in a QtWebEngine environment, registering cookie handlers."
        )
        # We want to persist cookies accross sessions.
        # The cookies will be cleared if there are no prior session in
        # method 'update_browser_from_session' if needed.
        self._profile.setPersistentCookiesPolicy(
            QtWebEngineWidgets.QWebEngineProfile.ForcePersistentCookies
        )
        self._cookie_jar = QtNetwork.QNetworkCookieJar()
        self._profile.cookieStore().cookieAdded.connect(self._on_cookie_added)
        self._profile.cookieStore().cookieRemoved.connect(self._on_cookie_deleted)

        # Threshold percentage of the SSO session duration, at which
        # time the pre-emptive renewal operation should be started.
        # @TODO: Make threshold parameter configurable.
        self._sso_preemptive_renewal_threshold = PREEMPTIVE_RENEWAL_THRESHOLD

        # We use the _sso_countdown_timer so that it fires once. Its purpose
        # is to start the other _sso_renew_timer. It fires once at an interval
        # of '0', which means 'whenever there are no event waiting in the
        # queue'. The intent is that it will execute the actual (and costly)
        # renewal at a time when the main event loop is readily available.
        #
        # The _sso_countdown_timer will be re-started in on_renew_sso_session.
        # Thus re-starting the chain of reneal events.
        self._sso_countdown_timer = QtCore.QTimer(self._dialog)
        self._sso_countdown_timer.setSingleShot(True)
        self._sso_countdown_timer.timeout.connect(self.on_schedule_sso_session_renewal)

        self._sso_renew_timer = QtCore.QTimer(self._dialog)
        self._sso_renew_timer.setInterval(0)
        self._sso_renew_timer.setSingleShot(True)
        self._sso_renew_timer.timeout.connect(self.on_renew_sso_session)

        # Watchdog timer to detect abnormal conditions during SSO
        # session renewal.
        # If timeout occurs, then the renewal is considered to have
        # failed, therefore the operation is aborted and recovery
        # by interactive authentication is initiated.
        # @TODO: Make watchdog timer duration configurable.
        self._sso_renew_watchdog_timeout_ms = WATCHDOG_TIMEOUT_MS
        self._sso_renew_watchdog_timer = QtCore.QTimer(self._dialog)
        self._sso_renew_watchdog_timer.setInterval(self._sso_renew_watchdog_timeout_ms)
        self._sso_renew_watchdog_timer.setSingleShot(True)
        self._sso_renew_watchdog_timer.timeout.connect(
            self.on_renew_sso_session_timeout
        )

        # We need a way to trace the current status of our login process.
        self._login_status = 0

        # For debugging purposes
        if self._developer_mode:
            self._logger.debug(
                "To debug the Qt5 WebEngine, use the following environment variables:"
            )
            self._logger.debug("  export QTWEBENGINE_REMOTE_DEBUGGING=8888")
            self._logger.debug("  or")
            self._logger.debug(
                '  export QTWEBENGINE_CHROMIUM_FLAGS="--remote-debugging-port=8888"'
            )
            self._logger.debug(" ")
            self._logger.debug(
                " Then you just need to point a chrome browser to http://127.0.0.1:8888"
            )
            self._logger.debug(
                " In this example, port 8888 is used, but it could be set to another one"
            )

    def __del__(self):
        """Destructor."""
        # We want to track destruction of the dialog in the logs.
        self._logger.debug("Destroying SSO dialog")
        # @TODO: Refactor these calls or figure out why they hang builds on Windows/3.7
        # self._sso_countdown_timer.stop()
        # self._sso_renew_timer.stop()
        # self._sso_renew_watchdog_timer.stop()
        # if self._view:
        #     self._view.urlChanged.disconnect(self._on_url_changed)
        #     self._layout.removeWidget(self._view)
        #     self._view = None
        #     self._layout = None
        #     self._dialog = None

    @property
    def _session(self):
        """
        Getter for the current session.

        Returns the current session, if any. The session provides information
        on the current context (host, user ID, etc.)

        :returns: The current session.
        """
        return self._sessions_stack[-1] if self._sessions_stack else None

    def start_new_session(self, session_data):
        """
        Create a new session, based on the data provided.

        :param session_data: Initial session data to use.
                             A dictionary with a 'event', 'host' and 'cookies' entries.
        """
        self._logger.debug("Starting a new session")
        self._sessions_stack.append(AuthenticationSessionData(session_data))
        self.update_browser_from_session()

    def end_current_session(self):
        """
        Destroy the current session, and resume the previous one, if any.
        """
        self._logger.debug("Ending current session")
        if self._sessions_stack:
            self._sessions_stack.pop()
        self.update_browser_from_session()

    def update_session_from_browser(self):
        """
        Update our session from the browser cookies.
        """
        self._logger.debug("Updating session cookies from browser")

        # In the past, we used SimpleCookie as an interim storage for cookies.
        # This turned out to be a bad decision, since SimpleCookie does not
        # discriminate based on the Domain. With two cookies with the same name
        # but different domains, the second overwrites the first.
        # But the SimpleCookie format is used for storage, thus the need for
        # backward/forward compatibility
        cookies = []
        for cookie in self._cookie_jar.allCookies():
            cookie = cookie.toRawForm().data()

            # In Python3, the data is of class bytes, not string.
            if type(cookie) is not str:
                cookie = cookie.decode()
            cookies.append(cookie)
        encoded_cookies = _encode_cookies("\r\n".join(cookies))

        content = {
            "session_expiration": get_saml_claims_expiration(encoded_cookies),
            "session_id": get_session_id(encoded_cookies),
            "user_id": get_user_name(encoded_cookies),
            "csrf_key": get_csrf_key(encoded_cookies),
            "csrf_value": get_csrf_token(encoded_cookies),
        }

        # To minimize handling, we also keep a snapshot of the browser cookies.
        # We do so for all of them, as some are used by the IdP and we do not
        # want to manage those. Their names may change from IdP version and
        # providers. We figure it is simpler to keep everything.

        # Here, we have a list of cookies in raw text form
        content["cookies"] = encoded_cookies

        self._session.merge_settings(content)

    def update_browser_from_session(self):
        """
        Update/reset the browser cookies with what we have.
        """
        self._logger.debug("Updating browser cookies from session")
        # pylint: disable=invalid-name
        QtNetwork = self._QtNetwork  # noqa

        qt_cookies = []
        if self._session is not None:
            parsed = sanitize_http_proxy(self._session.http_proxy)
            if parsed.netloc:
                self._logger.debug(
                    "Using HTTP proxy: %s://%s", parsed.scheme, parsed.netloc
                )
                proxy = QtNetwork.QNetworkProxy(
                    QtNetwork.QNetworkProxy.HttpProxy,
                    parsed.hostname,
                    parsed.port,
                    parsed.username,
                    parsed.password,
                )
                QtNetwork.QNetworkProxy.setApplicationProxy(proxy)

            # WARNING: The session cookies are serialized using a format that
            # must be readable by SimpleCookie for backward compatibility.
            # See comment in method update_session_from_browser for details.
            cookies = _decode_cookies(self._session.cookies)
            qt_cookies = QtNetwork.QNetworkCookie.parseCookies(cookies.encode())

        # Given that QWebEngineCookieStore's setCookie and deleteCookie are
        # not yet exposed to PySide2/Qt5, we need to rely on the profile for
        # cookie persistency as well as keeping our own copy in the tk-core
        # session. This is in case a PySide/Qt4 application is used later on.
        if not self._QtWebKit and not qt_cookies:
            self._logger.debug("Clearing all of the browser cookies")
            self._profile.cookieStore().deleteAllCookies()
            pass
        self._cookie_jar.setAllCookies(qt_cookies)

    def is_session_renewal_active(self):
        """
        Indicates if the automatic session renewal is used.

        :returns: True if it is, False otherwise.
        """
        return self._session_renewal_active

    def stop_session_renewal(self):
        """
        Stop automatic session renewal.

        This will be needed before opening a connection to a different server.
        We want to avoid confusion as to where the session is created and
        renewed.
        """
        self._logger.debug("Stopping automatic session renewal")

        self._session_renewal_active = False
        self._sso_renew_watchdog_timer.stop()
        self._sso_countdown_timer.stop()
        self._sso_renew_timer.stop()

    def start_sso_renewal(self):
        """
        Start the automated SSO session renewal.

        This will be done in the background, hopefully not impacting any
        ongoing process such as playback.
        """
        self._logger.debug("Starting automatic session renewal")

        self._sso_renew_watchdog_timer.stop()

        # We will need to cause an immediate renewal in order to get an
        # accurate knowledge of the session expiration. 0 is a special value
        # for QTimer intervals, so we use 1ms.
        interval = 1
        if self._session.session_expiration > time.time():
            interval = (
                (self._session.session_expiration - time.time())
                * self._sso_preemptive_renewal_threshold
                * 1000
            )

            # For debugging purposes
            # @TODO: Find a better way than to use this EV
            if self._developer_mode:
                interval = SHOTGUN_SSO_RENEWAL_INTERVAL
        self._logger.debug("Setting session renewal interval to: %s seconds", interval)

        self._sso_countdown_timer.setInterval(interval)
        self._sso_countdown_timer.start()
        self._session_renewal_active = True

    def _on_cookie_added(self, cookie):
        """
        In PySid2/Qt5, we have limited access to query/update the CookieStore. We
        must rely on signals called at each cookie addition and removal. We thus
        keep a cache of the present CookieStore state in our own cookie jar.
        This class existed in PySide/Qt4, but then was used as the actual cookie
        store.
        """
        if self._developer_mode:
            self._logger.debug(
                "_on_cookie_added: %s",
                cookie.toRawForm(self._QtNetwork.QNetworkCookie.NameAndValueOnly),
            )
        self._cookie_jar.insertCookie(cookie)

    def _on_cookie_deleted(self, cookie):
        """
        In PySid2/Qt5, we have limited access to query/update the CookieStore. We
        must rely on signals called at each cookie addition and removal. We thus
        keep a cache of the present CookieStore state in our own cookie jar.
        This class existed in PySide/Qt4, but then was used as the actual cookie
        store.
        """
        if self._developer_mode:
            self._logger.debug(
                "_on_cookie_deleted: %s",
                cookie.toRawForm(self._QtNetwork.QNetworkCookie.NameAndValueOnly),
            )
        self._cookie_jar.deleteCookie(cookie)

    def is_handling_event(self):
        """
        Called to know if an event is currently being handled.
        """
        return self._event_data is not None

    def handle_event(self, event_data):
        """
        Called to start the handling of an event.

        :param event_data: A dictionary with a 'event', 'host' and 'cookies' entries.
        """
        if not self.is_handling_event():
            self._event_data = event_data

            # At this point, we want to stop any background session renewal, as
            # it may impede with our new sesion login.
            self.stop_session_renewal()

            self.start_new_session(event_data)
        else:
            self._logger.error(
                "Calling handle_event while event %s is currently being handled",
                self._event_data["event"],
            )

    def resolve_event(self, end_session=False):
        """
        Called to return the results of the event.

        :param end_session: Boolean, indicating if the session should be ended.
        """
        if self.is_handling_event():
            if end_session:
                self.end_current_session()
            self._event_data = None
        else:
            self._logger.warn("Called resolve_event when no event is being handled.")

    def get_session_error(self):
        """
        Get the session error string.

        :returns: The error string of the last failed operation.
        """
        res = None
        if self._session and self._session.error:
            res = self._session.error
        return res

    ############################################################################
    #
    # QTimer callbacks
    #
    ############################################################################

    def on_schedule_sso_session_renewal(self):
        """
        Called to trigger the session renewal.

        The session renewal, via the off-screen QWebView, will be done at the
        next time the application event loop does not have any pending events.
        """
        self._logger.debug("Schedule SSO session renewal")
        self._sso_renew_timer.start()

    def on_renew_sso_session(self):
        """
        Called to renew the current SSO session.

        The renewal will be done via an off-screen QWebView. The intent is to
        benefit from the saved session cookies to automatically trigger the
        renewal without having the user having to enter any inputs.
        """
        self._logger.debug("Renew SSO session")
        self._sso_renew_watchdog_timer.start()

        # We do not update the page cookies, assuming that they have already
        # have been cleared/updated before.
        url = get_renew_path(self._session, self._logger)
        self._logger.debug("Navigating to %s", url)
        self._view.page().load(url)

    def on_renew_sso_session_timeout(self):
        """
        Called when the SSO session renewal is taking too long to complete.

        The purpose of this callback is to stop the page loading.
        """
        self._logger.debug("Timeout awaiting session renewal")
        self._dialog.reject()

    ############################################################################
    #
    # Qt event handlers
    #
    ############################################################################

    def _polyfill(self):
        """
        Called by Qt when the Web Page has changed and before it is loaded.

        The purpose of this function is to inject JavaScript code in a page
        before any of its code is run. This gives us a way to modify the code's
        environment and define functions which would be required by that code.
        """
        frame = self._view.page().currentFrame()
        frame.runJavascript(FUNCTION_PROTOTYPE_BIND_POLYFILL)
        self._logger.debug(
            "Injected polyfill JavaScript code for Function.prototype.bind and Array.prototype.splice"
        )

    def _on_url_changed(self, succeeded):
        """
        Called by Qt when the URL change.

        The renewal process goes thru a number of redirects. We detect the
        end of the process by checking the page loaded, as we know where we
        expect to land in the end.

        At that point, we stop the process by sending the 'accept' event to
        the dialog. If the process is taking too long, we have a timer
        (_sso_renew_watchdog_timer) which will trigger and attempt to cleanup
        the process.
        """
        url = self._view.page().url().toString()
        # in debug mode, use the title bar to show the url.
        if self._developer_mode:
            self._dialog.setWindowTitle(url)
        self._logger.debug("_on_url_changed %s", url)
        if self._session is not None and url.startswith(
            self._session.host + URL_ULF_LANDING_PATH
        ):
            self._sso_renew_watchdog_timer.stop()
            self.update_session_from_browser()
            if self._session_renewal_active:
                self.start_sso_renewal()

            self._dialog.accept()

        if not succeeded:
            self._logger.error('Loading of page "%s" generated an error.', url)

    def on_authentication_required(self, _reply, authenticator):
        """
        Called when authentication is required to get to a web page.

        This method is required to support NTLM/Kerberos on a Windows machine,
        of if there is a SSO Desktop integration plugin.

        :param reply: Qt reply object. Not used.
        :param authenticator: Qt authenticator object.
        """
        # We take for granted that if we are on Windows, proper NTLM negociation
        # is possible between the machine and the IdP. For other platforms, we
        # pop an authentication dialog.
        if sys.platform != "win32" and UsernamePasswordDialog is not None:
            message = (
                "<p>Your company has configured Single Sign-On (SSO) for the PTR site %s"
                "<p>Please authenticate with your computer login and password to log into Flow Production Tracking."
                "<p>"
            )
            auth_dialog = UsernamePasswordDialog(message=message % self._session.host)
            if auth_dialog.exec_():
                authenticator.setUser(auth_dialog.username)
                authenticator.setPassword(auth_dialog.password)
            else:
                self._logger.debug("User prompted for username/password but canceled")
        else:
            if UsernamePasswordDialog is None:
                self._logger.debug(
                    "Unable to prompt user for username/password, due to missing username_password_dialog module"
                )
            # Setting the user to an empty string tells the QAuthenticator to
            # negotiate the authentication with the user's credentials.
            authenticator.setUser("")

    ############################################################################
    #
    # Events handlers
    #
    ############################################################################

    def on_sso_login_attempt(
        self, event_data=None, use_watchdog=False, profile_location=None
    ):
        """
        Called to attempt a login process with user interaction.

        The user will be presented with the appropriate web pages from their
        IdP in order to log on to Shotgun.

        :returns: 1 if successful, 0 otherwise.
        """
        self._logger.debug("Web login attempt")
        # pylint: disable=invalid-name
        QtCore = self._QtCore  # noqa

        if not self._QtWebKit and profile_location:
            # Having separate Chromium profile persistency location have been proven
            # necessary for a few reasons:
            # - Because all of the cookies are serialized to the user's cache, this makes
            #   the session_metadata property increase in size over time. The PTR desktop app
            #   serializes the user's properties as environment variables when starting
            #   desktop-linked apps. On Windows, there is a maximum length of 32676 bytes
            #   for them.
            # - By splitting Chromium profiles on a per-site basis (as is the case with
            #   the user infos), we reduce the chances of busting that 32767 limit. It is
            #   still possible for a user to reach it (as cookies accumulate). But then
            #   the easy fix is to sign-out of the PTR desktop app (or clear_default_user()).
            # - When a user signs out of a site, that site's user data (and session_metadata)
            #   is cleared. At authentication time, if we see that there are no cookies
            #   present, we clear whatever cookies are present in the local Chromium
            #   profile.
            # - Unfortunately, cookies are more difficult to manage with PySide2 than
            #   with PySide. We cannot inject individual cookies in a Chromium profile
            #   The APIs, QWebEngineCookieStore's setCookie and deleteCookie, while
            #   documented are unfortunately not yet available to PySide2/Qt5. Our only
            #   solution is to have the Chromium profile do the persistency (with our
            #   own cache in case we are called by a PySide/Qt4 application). With
            #   the occasional use of deleteAllCookies() when deemed necessary.
            #
            # While having separate profiles for different sites seems contrary to the
            # use of SSO : in a browser, you could access all the sites behind the same
            # IdP by authenticating once, while with the Toolkit you will likely need
            # to authenticate once per site. But this is the same behaviour as we
            # have in our Qt4 environment.
            profile_path = os.path.join(profile_location, "QWebEngineProfile")
            self._profile.setPersistentStoragePath(profile_path)
            self._logger.debug(
                "Actual WebEngineProfile storage location: %s",
                self._profile.persistentStoragePath(),
            )

        if event_data is not None:
            self.handle_event(event_data)

        if use_watchdog:
            self._logger.debug("Starting watchdog")
            self._sso_renew_watchdog_timer.start()

        # If we do have session cookies, let's attempt a session renewal
        # without presenting any GUI.
        if self._session.cookies:
            self._logger.debug("Attempting a GUI-less renewal")
            loop = QtCore.QEventLoop(self._dialog)
            self._dialog.finished.connect(loop.exit)
            self.on_renew_sso_session()
            status = loop.exec_()
            self._login_status = self._login_status or status
            return self._login_status

        self._view.show()
        self._view.raise_()

        # We append the product code to the GET request.
        url = get_renew_path(self._session, self._logger)
        self._logger.debug("Navigating to %s", url)
        self._view.page().load(url)

        self._dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        status = self._dialog.exec_()
        self._login_status = self._login_status or status
        return self._login_status

    def on_dialog_closed(self, result):
        """
        Called whenever the dialog is dismissed.

        This can be the result of a callback, a timeout or user interaction.

        :param result: Qt result following the closing of the dialog.
                       QtGui.QDialog.Accepted or QtGui.QDialog.Rejected
        """
        self._logger.debug("SSO dialog closed")
        # pylint: disable=invalid-name
        QtGui = self._QtGui  # noqa

        if self.is_handling_event():
            if result == QtGui.QDialog.Rejected and self._session.cookies != "":
                # We got here because of a timeout attempting a GUI-less login.
                # Let's clear the cookies, and force the use of the GUI.
                self._session.cookies = ""
                # Let's have another go, without any cookies this time !
                # This will force the GUI to be shown to the user.
                self._logger.debug(
                    "Unable to login/renew claims automaticall, presenting GUI to user"
                )
                status = self.on_sso_login_attempt()
                self._login_status = self._login_status or status
            else:
                self.resolve_event()
        else:
            # Should we get a rejected dialog, then we have had a timeout.
            if result == QtGui.QDialog.Rejected:
                # @FIXME: Figure out exactly what to do when we have a timeout.
                self._logger.warn(
                    "Our QDialog got canceled outside of an event handling"
                )

        # Clear the web page
        self._view.page().load("about:blank")
