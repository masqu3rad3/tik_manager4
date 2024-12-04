# Copyright (c) 2023 Autodesk.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import json
import os
import platform
import random
import sys
import time

import tank
from tank_vendor import six
from tank_vendor.six.moves import http_client, urllib

from . import errors
from .. import platform as sgtk_platform
from ..util.shotgun import connection

from .. import LogManager

logger = LogManager.get_logger(__name__)

PRODUCT_DEFAULT = "Flow Production Tracking Toolkit"
PRODUCT_DESKTOP = "FPTR desktop app"


class AuthenticationError(errors.AuthenticationError):
    def __init__(self, msg, asl_errno=None, payload=None, parent_exception=None):
        errors.AuthenticationError.__init__(self, msg)
        self.asl_errno = asl_errno
        self.payload = payload
        self.parent_exception = parent_exception

    def format(self):
        """
        Provide a STR format of all given parameters
        """

        info = []
        if self.asl_errno:
            info.append("errno: {}".format(self.asl_errno))

        if self.payload:
            info.append("payload: {}".format(self.payload))

        if self.parent_exception:
            info.append("parent: {}".format(self.parent_exception))

        message = str(self)
        if info:
            message += " ({})".format("; ".join(info))

        return message


def process(
    sg_url,
    browser_open_callback,
    http_proxy=None,
    product=None,
    keep_waiting_callback=lambda: True,
):
    sg_url = connection.sanitize_url(sg_url)
    logger.debug("Trigger Authentication on {url}".format(url=sg_url))

    if product is None:
        product = get_product_name()

    assert product
    assert callable(browser_open_callback)
    assert callable(keep_waiting_callback)

    url_handlers = [urllib.request.HTTPHandler]
    if http_proxy:
        proxy_addr = _build_proxy_addr(http_proxy)
        sg_url_parsed = urllib.parse.urlparse(sg_url)

        logger.debug(
            "Set HTTP Proxy handler for {scheme} to {url}".format(
                url=proxy_addr,
                scheme=sg_url_parsed.scheme,
            )
        )

        url_handlers.append(
            urllib.request.ProxyHandler(
                {
                    sg_url_parsed.scheme: proxy_addr,
                }
            )
        )

    url_opener = urllib.request.build_opener(*url_handlers)

    user_agent = build_user_agent().encode(errors="ignore")

    request = urllib.request.Request(
        urllib.parse.urljoin(sg_url, "/internal_api/app_session_request"),
        # method="POST", # see below
        data=urllib.parse.urlencode(
            {
                "appName": product,
                "machineId": platform.node(),
            }
        ).encode(),
        headers={
            "User-Agent": user_agent,
        },
    )

    # Hook for Python 2
    request.get_method = lambda: "POST"

    response = http_request(url_opener, request)
    logger.debug(
        "Initial network request returned HTTP code {code}".format(
            code=response.code,
        )
    )

    response_code_major = response.code // 100
    if response_code_major == 5:
        raise AuthenticationError(
            "Unable to establish a stable communication with the Flow Production Tracking site",
            payload=getattr(response, "json", response),
            parent_exception=getattr(response, "exception", None),
        )

    elif response_code_major == 4:
        if response.code == http_client.FORBIDDEN and hasattr(response, "json"):
            logger.debug(
                "HTTP response Forbidden: {data}".format(data=response.json),
                exc_info=getattr(response, "exception", None),
            )
            raise AuthenticationError(
                "Unable to create an authentication request. The feature does "
                "not seem to be enabled on the Flow Production Tracking site",
                parent_exception=getattr(response, "exception", None),
                payload=response.json,
            )

        raise AuthenticationError(
            "Unable to create an authentication request",
            parent_exception=response.exception,
        )

    elif response.code != http_client.OK:
        raise AuthenticationError(
            "Unexpected response from the Flow Production Tracking site",
            payload=getattr(response, "json", response),
            parent_exception=getattr(response, "exception", None),
        )

    elif not isinstance(getattr(response, "json", None), dict):
        logger.error(
            "Unexpected response from the Flow Production Tracking site. Expecting a JSON dict"
        )
        raise AuthenticationError(
            "Unexpected response from the Flow Production Tracking site"
        )

    session_id = response.json.get("sessionRequestId")
    if not session_id:
        logger.error(
            "Unexpected response from the Flow Production Tracking site. Expecting a sessionRequestId item"
        )
        raise AuthenticationError(
            "Unexpected response from the Flow Production Tracking site"
        )

    browser_url = response.json.get("url")
    if not browser_url:
        logger.error(
            "Unexpected response from the Flow Production Tracking site. Expecting a url item"
        )
        raise AuthenticationError(
            "Unexpected response from the Flow Production Tracking site"
        )

    logger.debug(
        "Authentication Request ID: {session_id}".format(session_id=session_id)
    )

    ret = browser_open_callback(browser_url)
    if not ret:
        raise AuthenticationError("Unable to open local browser")

    logger.debug("Awaiting request approval from the browser...")

    sleep_time = 2
    request_timeout = 180  # 5 minutes
    request_url = urllib.parse.urljoin(
        sg_url,
        "/internal_api/app_session_request/{session_id}".format(
            session_id=session_id,
        ),
    )

    approved = False
    t0 = time.time()
    while (
        approved is False
        and keep_waiting_callback()
        and time.time() - t0 < request_timeout
    ):
        time.sleep(sleep_time)

        request = urllib.request.Request(
            request_url,
            # method="PUT", # see below
            headers={
                "User-Agent": user_agent,
            },
        )

        # Hook for Python 2
        request.get_method = lambda: "PUT"

        response = http_request(url_opener, request)

        response_code_major = response.code // 100
        if response_code_major == 5:
            logger.debug(
                "HTTP response {code}: {data}".format(
                    code=response.code,
                    data=getattr(response, "json", response),
                ),
                exc_info=getattr(response, "exception", None),
            )

            raise AuthenticationError(
                "Unable to establish a stable communication with the Flow Production Tracking site",
                payload=getattr(response, "json", response),
                parent_exception=getattr(response, "exception", None),
            )

        elif response_code_major == 3:
            location = response.headers.get("location", None)

            logger.debug("Request redirected: http code: {code}; redirect to: {location}".format(
                code=response.code,
                location=location,
            ))

            raise AuthenticationError(
                "Request redirected",
                payload="HTTP Redirect to {}".format(location),
                parent_exception=getattr(response, "exception", None),
            )

        elif response_code_major == 4:
            logger.debug(
                "HTTP response {code}: {data}".format(
                    code=response.code,
                    data=getattr(response, "json", response),
                ),
                exc_info=getattr(response, "exception", None),
            )

            if response.code == http_client.NOT_FOUND and hasattr(response, "json"):
                raise AuthenticationError(
                    "The request has been rejected or has expired."
                )

            raise AuthenticationError(
                "Unexpected response from the Flow Production Tracking site",
                parent_exception=getattr(response, "exception", None),
            )

        elif response.code != http_client.OK:
            logger.debug("Request denied: http code is: {code}".format(
                code=response.code,
            ))
            raise AuthenticationError(
                "Request denied",
                payload=getattr(response, "json", response),
                parent_exception=getattr(response, "exception", None),
            )

        elif not isinstance(getattr(response, "json", None), dict):
            logger.error(
                "Unexpected response from the Flow Production Tracking site. Expecting a JSON dict"
            )
            raise AuthenticationError(
                "Unexpected response from the Flow Production Tracking site"
            )

        approved = response.json.get("approved", False)

    if not approved:
        raise AuthenticationError("The request has never been approved")

    logger.debug("Request approved")
    try:
        assert response.json["sessionToken"]
        assert response.json["userLogin"]
    except (KeyError, AssertionError):
        logger.debug(
            "Unexpected response from the Flow Production Tracking site",
            exc_info=True,
        )
        raise AuthenticationError(
            "Unexpected response from the Flow Production Tracking site"
        )

    logger.debug("Session token: {sessionToken}".format(**response.json))

    return (
        sg_url,
        response.json["userLogin"],
        response.json["sessionToken"],
        None,  # Extra metadata - useless here
    )


def get_product_name():
    if "TK_AUTH_PRODUCT" in os.environ:
        return os.environ["TK_AUTH_PRODUCT"]

    try:
        engine = sgtk_platform.current_engine()
        product = engine.host_info["name"]
        assert product and isinstance(product, str)
    except (AttributeError, TypeError, KeyError, AssertionError):
        logger.debug("Unable to retrieve the host_info from the current_engine")
        # Most likely because the engine is not initialized yet
    else:
        if product.lower() == "desktop":
            product = PRODUCT_DESKTOP

        if engine.host_info.get("version", "unknown") != "unknown":
            product += " {version}".format(**engine.host_info)

        return product

    # current_engine is not set in SGD at login time...
    if os.path.splitext(os.path.basename(sys.argv[0]))[0].lower() == "shotgun":
        return PRODUCT_DESKTOP

    # Flame
    if (
        "SHOTGUN_FLAME_CONFIGPATH" in os.environ
        and "SHOTGUN_FLAME_VERSION" in os.environ
    ):
        return "Flame {SHOTGUN_FLAME_VERSION}".format(**os.environ)

    # Fallback to default/worst case value
    return PRODUCT_DEFAULT


def _get_content_type(headers):
    if six.PY2:
        value = headers.get("content-type", "text/plain")
        return value.split(";", 1)[0].lower()
    else:
        return headers.get_content_type()


def http_request(opener, req, max_attempts=4):
    attempt = 0
    backoff = 0.75  # Seconds to wait before retry, times the attempt number

    response = None
    while response is None and attempt < max_attempts:
        if attempt:
            time.sleep(float(attempt) * backoff * random.uniform(1, 3))

        attempt += 1
        try:
            response = opener.open(req)
        except urllib.error.HTTPError as exc:
            if attempt < max_attempts and exc.code // 100 == 5:
                logger.debug(
                    "HTTP request returned a {code} code on attempt {attempt}/{max_attempts}".format(
                        attempt=attempt,
                        code=exc.code,
                        max_attempts=max_attempts,
                    ),
                    exc_info=exc,
                )
                continue

            response = exc.fp
            response.exception = exc

        except urllib.error.URLError as exc:
            if attempt < max_attempts and isinstance(exc.reason, ConnectionError):
                logger.debug(
                    "HTTP request failed to reach the server on attempt {attempt}/{max_attempts}".format(
                        attempt=attempt,
                        max_attempts=max_attempts,
                    ),
                    exc_info=exc,
                )
                continue

            raise AuthenticationError(
                "Unable to communicate with the PTR site",
                parent_exception=exc,
            )

        except ConnectionError as exc:
            if attempt < max_attempts:
                logger.debug(
                    "HTTP request failed to reach the server on attempt {attempt}/{max_attempts}".format(
                        attempt=attempt,
                        max_attempts=max_attempts,
                    ),
                    exc_info=exc,
                )
                continue

            raise AuthenticationError(
                "Unable to communicate with the PTR site",
                parent_exception=exc,
            )

    if _get_content_type(response.headers) == "application/json":
        try:
            response.json = json.load(response)
        except json.JSONDecodeError as exc:
            # ideally, we want a warning here. Not an excetpion
            raise AuthenticationError(
                "Unable to decode JSON content",
                parent_exception=exc,
            )

    return response


def _build_proxy_addr(http_proxy):
    # Expected format: foo:bar@123.456.789.012:3456

    proxy_port = 8080

    proxy_user = None
    proxy_pass = None

    # check if we're using authentication. Start from the end since
    # there might be @ in the user's password.
    p = http_proxy.rsplit("@", 1)
    if len(p) > 1:
        proxy_user, proxy_pass = p[0].split(":", 1)
        proxy_server = p[1]
    else:
        proxy_server = http_proxy

    proxy_netloc_list = proxy_server.split(":", 1)
    proxy_server = proxy_netloc_list[0]
    if len(proxy_netloc_list) > 1:
        try:
            proxy_port = int(proxy_netloc_list[1])
        except ValueError:
            raise ValueError(
                'Invalid http_proxy address "{http_proxy}".'
                'Valid format is "123.456.789.012" or "123.456.789.012:3456".'
                "If no port is specified, a default of {proxy_port} will be "
                "used.".format(
                    http_proxy=http_proxy,
                    proxy_port=proxy_port,
                )
            )

    # now populate proxy_handler
    if proxy_user and proxy_pass:
        auth_string = "{proxy_user}:{proxy_pass}@".format(
            proxy_pass=proxy_pass,
            proxy_user=proxy_user,
        )
    else:
        auth_string = ""

    return "http://{auth_string}{proxy_server}:{proxy_port}".format(
        auth_string=auth_string,
        proxy_port=proxy_port,
        proxy_server=proxy_server,
    )


def build_user_agent():
    return "tk-core/{tank_ver} {py_impl}/{py_ver} ({platform})".format(
        platform=platform.platform(),
        py_impl=platform.python_implementation(),
        py_ver=platform.python_version(),
        tank_ver=tank.__version__,
    )


if __name__ == "__main__":
    import argparse
    import logging
    import webbrowser

    lh = logging.StreamHandler()
    lh.setLevel(logging.DEBUG)
    lh.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
    ))

    logger.addHandler(lh)
    print()

    parser = argparse.ArgumentParser()
    parser.add_argument("sg_url", help="Provide a Flow Production Tracking URL")
    parser.add_argument("--http-proxy", "-p", help="Set a proxy URL")
    args = parser.parse_args()

    result = process(
        args.sg_url,
        product="Test Script",
        browser_open_callback=lambda u: webbrowser.open(u),
        http_proxy=args.http_proxy,
    )
    if not result:
        print("The web authentication failed. Please try again.")
        sys.exit(1)

    print("The web authentication succeed, now processing.")
    print()
    print(result)
