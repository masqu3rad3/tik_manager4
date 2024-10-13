# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Methods for connecting to Shotgun
"""

from __future__ import with_statement

import os
import threading
from tank_vendor.six.moves import urllib

# use api json to cover py 2.5
from tank_vendor import shotgun_api3

from ..errors import UnresolvableCoreConfigurationError
from ...errors import TankError
from ...log import LogManager
from ... import hook
from .. import constants
from .. import yaml_cache

log = LogManager.get_logger(__name__)


def __get_api_core_config_location():
    r"""

    Walk from the location of this file on disk to the config area.
    this operation is guaranteed to work on any valid tank installation

    Pipeline Configuration / Studio Location
       |
       |- Install
       |     \- Core
       |          \- Python
       |                \- tank
       |
       \- Config
             \- Core
    """
    # local import to avoid cyclic references
    from ...pipelineconfig_utils import get_path_to_current_core

    core_api_root = get_path_to_current_core()
    core_cfg = os.path.join(core_api_root, "config", "core")

    if not os.path.exists(core_cfg):
        path_to_file = os.path.abspath(os.path.dirname(__file__))
        path_to_core = os.path.abspath(os.path.join(path_to_file, "..", ".."))
        raise UnresolvableCoreConfigurationError(path_to_core)

    return core_cfg


def __get_sg_config():
    """
    Returns the site sg config yml file for this install

    :returns: full path to to shotgun.yml config file
    """
    core_cfg = __get_api_core_config_location()
    path = os.path.join(core_cfg, "shotgun.yml")
    return path


def get_project_name_studio_hook_location():
    """
    Returns the studio level hook that is used to compute the default project name

    :returns: The path to the studio level project naming hook.
    """

    # NOTE! This code is located here because it needs to be able to run without a project.
    # the natural place would probably have been to put this inside the pipeline configuration
    # class, however this object assumes a project that exists.
    #
    # @todo longterm we should probably establish a place in the code where we define
    # an API or set of functions which can be executed outside the remit of a
    # pipeline configuration/Toolkit project.

    core_cfg = __get_api_core_config_location()
    path = os.path.join(core_cfg, constants.STUDIO_HOOK_PROJECT_NAME)
    return path


def __get_sg_config_data(shotgun_cfg_path, user="default"):
    """
    Returns the shotgun configuration yml parameters given a config file.

    The shotgun.yml may look like:

        host: str
        api_script: str
        api_key: str
        http_proxy: str

        or may now look like:

        <User>:
            host: str
            api_script: str
            api_key: str
            http_proxy: str

        <User>:
            host: str
            api_script: str
            api_key: str
            http_proxy: str

    The optional user param refers to the <User> in the shotgun.yml.
    If a user is not found the old style is attempted.

    :param shotgun_cfg_path: path to config file
    :param user: Optional user to pass when a multi-user config is being read

    :returns: dictionary with key host and optional keys api_script, api_key and http_proxy
    """
    # load the config file
    try:
        file_data = (
            yaml_cache.g_yaml_cache.get(shotgun_cfg_path, deepcopy_data=False) or {}
        )
    except Exception as error:
        raise TankError(
            "Cannot load config file '%s'. Error: %s" % (shotgun_cfg_path, error)
        )

    return _parse_config_data(file_data, user, shotgun_cfg_path)


def __get_sg_config_data_with_script_user(shotgun_cfg_path, user="default"):
    """
    Returns the Shotgun configuration yml parameters given a config file, just like
    __get_sg_config_data, but the script user is expected to be present or an exception will be
    thrown.

    :param shotgun_cfg_path: path to config file
    :param user: Optional user to pass when a multi-user config is being read

    :raises TankError: Raised if the script user is not configured.

    :returns: dictionary with mandatory keys host, api_script, api_key and optionally http_proxy
    """
    config_data = __get_sg_config_data(shotgun_cfg_path, user)
    # If the user is configured, we're happy.
    if config_data.get("api_script") and config_data.get("api_key"):
        return config_data
    else:
        raise TankError(
            "Missing required script user in config '%s'" % shotgun_cfg_path
        )


def _parse_config_data(file_data, user, shotgun_cfg_path):
    """
    Parses configuration data and overrides it with the studio level hook's result if available.
    :param file_data: Dictionary with all the values from the configuration data.
    :param user: Picks the configuration for a specific user in the configuration data.
    :param shotgun_cfg_path: Path the configuration was loaded from.
    :raises: TankError if there are missing fields in the configuration. The accepted configurations are:
            - host
            - host, api_script, api_key
            In both cases, http_proxy is optional.
    :returns: A dictionary holding the configuration data.
    """
    if user in file_data:
        # new config format!
        # we have explicit users defined!
        config_data = file_data[user]
    else:
        # old format - not grouped by user
        config_data = file_data

    # now check if there is a studio level override hook which want to refine these settings
    sg_hook_path = os.path.join(
        __get_api_core_config_location(), constants.STUDIO_HOOK_SG_CONNECTION_SETTINGS
    )

    if os.path.exists(sg_hook_path):
        # custom hook is available!
        config_data = hook.execute_hook(
            sg_hook_path,
            parent=None,
            config_data=config_data,
            user=user,
            cfg_path=shotgun_cfg_path,
        )

    def _raise_missing_key(key):
        raise TankError(
            "Missing required field '%s' in config '%s' for script user authentication."
            % (key, shotgun_cfg_path)
        )

    if not config_data.get("host"):
        _raise_missing_key("host")

    # The script authentication credentials need to be complete in order to work. They can be completely
    # omitted or fully specified, but not halfway configured.
    if config_data.get("api_script") and not config_data.get("api_key"):
        _raise_missing_key("api_key")
    if not config_data.get("api_script") and config_data.get("api_key"):
        _raise_missing_key("api_script")

    # Manage configurations containing environment variables
    for key in config_data:
        if isinstance(config_data.get(key, None), str):
            config_data[key] = os.path.expandvars(config_data[key])

    # If the appstore proxy is set, but the value is falsy.
    if (
        "app_store_http_proxy" in config_data
        and not config_data["app_store_http_proxy"]
    ):
        # Make sure it is None.
        config_data["app_store_http_proxy"] = None

    config_data["host"] = sanitize_url(config_data["host"])

    return config_data


def __sanitize_url(server_url):
    """
    Parses a URL and makes sure it has a scheme and no extra / and path.

    ..note:: Calling this method only once might yield incorrect result. Always call
        the sanitize_url function instead.

    :param str server_url: URL to clean up.

    :returns: The cleaned up URL.
    """

    # The given url https://192.168.1.250:30/path?a=b is parsed such that
    # scheme => https
    # netloc => 192.168.1.250:30
    # path = /path
    # query = a=b

    # As such, when sanitizing a url, we want to keep only the scheme and
    # network location

    # Then break up the url into chunks
    tokens_parsed = urllib.parse.urlparse(server_url)

    # Then extract the good parts from the url
    clean_url_tokens = urllib.parse.ParseResult(
        # We want https when there is no specified scheme.
        scheme=tokens_parsed.scheme or "https",
        # If only a host has been provided, path will be set.
        # If a scheme was set, then use the netloc
        netloc=tokens_parsed.netloc or tokens_parsed.path,
        path="",
        params="",
        query="",
        fragment="",
    )

    return urllib.parse.urlunparse(clean_url_tokens)


def sanitize_url(server_url):
    """
    Cleans up a url to that only scheme, host and optional port number remains.

    For example::
        host.com => https://host.com
        host.com:8080 => https://host.com:8080
        https://host.com => https://host.com
        http://host.com => http://host.com
        https://host.com/ => https://host.com
        https://host.com/path => https://host.com

    :returns: The cleaned up URL.
    """

    # FIXME: Python 2.6.x has difficulty parsing a URL that doesn't start with a scheme when there
    # is already a port number. Python 2.7 doesn't have this issue. Ignore this bug for now since it
    # is very unlikely Shotgun will be running off a custom port.
    first_pass = __sanitize_url(server_url.strip())
    # We have to do two passes here. The reason is that if you use a slash in your URL but provide
    # no scheme, the urlparse/unparse calls will recreate the URL as is. Fortunately, when the
    # scheme is missing we're adding in https://. At that point the url is not ambiguous anymore for
    # urlparse/urlparse and it can split the url correctly into
    # - https (scheme)
    # - test.shogunstudio.com (network location)
    # - /... (path)
    #
    # We also lowercase the entire url. This will allow us to reliably compare site addresses
    # against each other elsewhere in the code and not have to worry about STUDIO.shotgunstudio.com
    # and studio.shotgunstudio.com not matching when they should be considered the same site.
    return __sanitize_url(first_pass).lower()


def get_associated_sg_base_url():
    """
    Returns the shotgun url which is associated with this Toolkit setup.
    This is an optimization, allowing code to get the Shotgun site URL
    without having to create a shotgun connection and then inspecting
    the base_url property.

    This method is equivalent to calling:

    create_sg_connection().base_url

    :returns: The base url for the associated Shotgun site
    """
    # Avoids cyclic imports.
    from ... import api

    sg_user = api.get_authenticated_user()

    if sg_user:
        return sg_user.host
    else:
        # look up in core/shotgun.yml
        return get_associated_sg_config_data()["host"]


def get_associated_sg_config_data():
    """
    Returns the shotgun configuration which is associated with this Toolkit setup.
    :returns: The configuration data dictionary with keys host and optional entries
              api_script, api_key and http_proxy.
    """
    cfg = __get_sg_config()
    return __get_sg_config_data(cfg)


def get_deferred_sg_connection():
    """
    Returns a shotgun API instance that is lazily initialized.
    This is a method intended only to support certain legacy cases
    where some operations in Toolkit are not fully authenticated.
    When descriptor objects are constructed, they are associated with a
    PTR API handle. This handle is not necessary for basic operations such
    as path resolution. By passing a deferred connection object to
    descriptors, authentication is essentially deferred until the need
    for more complex operations arises, allowing for simple, *legacy*
    non-authenticated pathways.

    :return: Proxied PTR API handle
    """

    class DeferredInitShotgunProxy(object):
        def __init__(self):
            self._sg = None

        def __getattr__(self, key):
            if self._sg is None:
                self._sg = get_sg_connection()
            return getattr(self._sg, key)

    return DeferredInitShotgunProxy()


_g_sg_cached_connections = threading.local()


def get_sg_connection():
    """
    Returns a shotgun connection and maintains a global cache of connections
    so that only one API instance is ever returned per thread, no matter how many
    times this call is made.

        .. note:: Because Shotgun API instances are not safe to share across
                  threads, this method caches PTR Instances per-thread.

    :return: PTR API handle
    """
    global _g_sg_cached_connections
    sg = getattr(_g_sg_cached_connections, "sg", None)

    if sg is None:
        sg = create_sg_connection()
        _g_sg_cached_connections.sg = sg

    return sg


@LogManager.log_timing
def create_sg_connection(user="default"):
    """
    Creates a standard tank shotgun connection.

    Note! This method returns *a brand new sg API instance*. It is slow.
    Always consider using tk.shotgun and if you don't have a tk instance,
    consider using get_sg_connection().

    Whenever a Shotgun API instance is created, it pings the server to check that
    it is running the right versions etc. This is slow and inefficient and means that
    there will be a delay every time create_sg_connection is called.

    :param user: Optional shotgun config user to use when connecting to shotgun,
                 as defined in shotgun.yml. This is a deprecated flag and should not
                 be used.
    :returns: PTR API instance
    """

    # Avoids cyclic imports.
    from ... import api

    sg_user = api.get_authenticated_user()

    # If there is no user, that's probably because we're running in an old script that doesn't use
    # the authenticated user concept. In that case, we'll do what we've always been doing in the
    # past, which is read shotgun.yml and expect there to be a script user.
    if sg_user is None:
        log.debug(
            "This tk session has no associated authenticated user. Falling back to "
            "creating a PTR API instance based on script based credentials in the "
            "shotgun.yml configuration file."
        )

        # try to find the shotgun.yml path
        try:
            config_file_path = __get_sg_config()
        except TankError as e:
            log.error(
                "Trying to create a PTR connection but this tk session does not have "
                "an associated authenticated user. Therefore attempted to fall back on "
                "a legacy authentication method where script based credentials are "
                "located in a file relative to the location of the core API code. This "
                "lookup in turn failed. No credentials can be determined and no connection "
                "to PTR can be made. Details: %s" % e
            )
            raise TankError(
                "Cannot connect to PTR - this tk session does not have "
                "an associated user and attempts to determine a valid PTR "
                "via legacy configuration files failed. Details: %s" % e
            )

        log.debug("Creating PTR connection based on details in %s" % config_file_path)
        config_data = __get_sg_config_data_with_script_user(config_file_path, user)

        # Credentials were passed in, so let's run the legacy authentication
        # mechanism for script user.
        api_handle = shotgun_api3.Shotgun(
            config_data["host"],
            script_name=config_data["api_script"],
            api_key=config_data["api_key"],
            http_proxy=config_data.get("http_proxy"),
            connect=False,
        )

    else:
        # Otherwise use the authenticated user to create the connection.
        log.debug("Creating PTR connection from %r..." % sg_user)
        api_handle = sg_user.create_sg_connection()

    # bolt on our custom user agent manager so that we can
    # send basic version metrics back via http headers.
    api_handle.tk_user_agent_handler = ToolkitUserAgentHandler(api_handle)

    return api_handle


#################################################################################################
# wrappers around the shotgun API's http header API methods


class ToolkitUserAgentHandler(object):
    """
    Convenience wrapper to handle the user agent management
    """

    def __init__(self, sg):
        self._sg = sg

        self._app = None
        self._framework = None
        self._engine = None

        self._core_version = None

    def __clear_bundles(self):
        """
        Resets the currently active bundle.
        """
        self._app = None
        self._framework = None
        self._engine = None

    def set_current_app(self, name, version, engine_name, engine_version):
        """
        Update the user agent headers for the currently active app
        """
        # first clear out the other bundle settings - there can only
        # be one active bundle at a time
        self.__clear_bundles()

        # populate the currently running bundle data
        self._app = (name, version)
        self._engine = (engine_name, engine_version)

        # push to shotgun
        self.__update()

    def set_current_framework(self, name, version, engine_name, engine_version):
        """
        Update the user agent headers for the currently active framework
        """
        # first clear out the other bundle settings - there can only
        # be one active bundle at a time
        self.__clear_bundles()

        # populate the currently running bundle data
        self._framework = (name, version)
        self._engine = (engine_name, engine_version)

        # push to shotgun
        self.__update()

    def set_current_engine(self, name, version):
        """
        Update the user agent headers for the currently active engine
        """
        # first clear out the other bundle settings - there can only
        # be one active bundle at a time
        self.__clear_bundles()

        # populate the currently running bundle data
        self._engine = (name, version)

        # push to shotgun
        self.__update()

    def set_current_core(self, core_version):
        """
        Update the user agent headers for the currently active core
        """
        self._core_version = core_version
        self.__update()

    def __update(self):
        """
        Perform changes to the Shotgun API
        """
        # note that because of shortcomings in the API,
        # we have to reference the member variable directly.
        #
        # sg._user_agents is a list of strings. By default,
        # its value is [ "shotgun-json (1.2.3)" ]

        # First, remove any old Toolkit settings
        new_agents = []
        for x in self._sg._user_agents:
            if (
                x.startswith("tk-core")
                or x.startswith("tk-app")
                or x.startswith("tk-engine")
                or x.startswith("tk-fw")
            ):
                continue
            new_agents.append(x)

        # Add new Toolkit settings
        if self._core_version:
            new_agents.append("tk-core (%s)" % self._core_version)

        if self._engine:
            new_agents.append("tk-engine (%s %s)" % self._engine)

        if self._app:
            new_agents.append("tk-app (%s %s)" % self._app)

        if self._framework:
            new_agents.append("tk-fw (%s %s)" % self._framework)

        # and update shotgun
        self._sg._user_agents = new_agents
