# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
from tank_vendor.six.moves import urllib
from . import filesystem
from .platforms import is_linux, is_macos, is_windows
from .. import LogManager
from ..errors import TankError
from tank_vendor.shotgun_api3.lib import sgsix

log = LogManager.get_logger(__name__)


class LocalFileStorageManager(object):
    """
    Class that encapsulates logic for resolving local storage paths.

    Toolkit needs to store cache data, logs and other items at runtime.
    Some of this data is global, other is per site or per configuration.

    This class provides a consistent and centralized interface for resolving
    such paths and also handles compatibility across generations of path
    standards if and when these change between releases.

    .. note:: All paths returned by this class are local to the currently running
              user and typically private or with limited access settings for other users.

              If the current user's home directory is not an appropriate location to store
              your user files, you can use the ``SHOTGUN_HOME`` environment variable to
              override the root location of the files. In that case, the location for the
              user files on each platform will be:

              - Logging:     ``$SHOTGUN_HOME/logs``
              - Cache:       ``$SHOTGUN_HOME``
              - Persistent:  ``$SHOTGUN_HOME/data``
              - Preferences: ``$SHOTGUN_HOME/preferences``


    :constant CORE_V17: Indicates compatibility with Core 0.17 or earlier
    :constant CORE_V18: Indicates compatibility with Core 0.18 or later

    :constant LOGGING:     Indicates a path suitable for storing logs, useful for debugging
    :constant CACHE:       Indicates a path suitable for storing cache data that can be deleted
                           without any loss of functionality or state.
    :constant PERSISTENT:  Indicates a path suitable for storing data that needs
                           to be retained between sessions.
    :constant PREFERENCES: Indicates a path that suitable for storing settings files and preferences.
    """

    # generation of path structures
    (CORE_V17, CORE_V18) = range(2)

    # supported types of paths
    (LOGGING, CACHE, PERSISTENT, PREFERENCES) = range(4)

    @classmethod
    def get_global_root(cls, path_type, generation=CORE_V18):
        """
        Returns a generic Shotgun storage root.

        The following paths will be used:

            - On the mac, paths will point into ``~/Library/PATH_TYPE/Shotgun``, where PATH_TYPE
              is controlled by the path_type property.
            - On Windows, paths will created below a ``%APPDATA%/Shotgun`` root point.
            - On Linux, paths will be created below a ``~/.shotgun`` root point.

        .. note:: This method does not ensure that the folder exists.

        :param path_type: Type of path to return. One of ``LocalFileStorageManager.LOGGING``,
                          ``LocalFileStorageManager.CACHE``, ``LocalFileStorageManager.PERSISTENT``, where
                          logging is a path where log- and debug related data should be stored,
                          cache is a location intended for cache data, e.g. data that can be deleted
                          without affecting the state of execution, and persistent is a location intended
                          for data that is meant to be persist. This includes things like settings and
                          preferences.
        :param generation: Path standard generation to use. Defaults to ``LocalFileStorageManager.CORE_V18``,
                           which is the current generation of paths.
        :return: Path as string
        """

        # If SHOTGUN_HOME is set, the intent is to not use any of official locations and instead use
        # a sandbox.
        #
        # If we still allowed the LocalFileStorageManager to return paths outside of SHOTGUN_HOME,
        # it would mean that data from outside SHOTGUN_HOME could leak into it and that a user
        # couldn't be confident that the sandbox was self-contained.

        # If the environment variable is available and set to an actual value.
        shotgun_home_override = os.environ.get("SHOTGUN_HOME")
        if generation == cls.CORE_V18 or shotgun_home_override:
            if shotgun_home_override:
                # Make sure environment variables and ~ are evaluated.
                shotgun_home_override = os.path.expanduser(
                    os.path.expandvars(shotgun_home_override)
                )
                # Make sure the path is an absolute path.
                shotgun_home_override = os.path.abspath(shotgun_home_override)
                # Root everything inside that custom path.
                if path_type == cls.CACHE:
                    return shotgun_home_override
                elif path_type == cls.PERSISTENT:
                    return os.path.join(shotgun_home_override, "data")
                elif path_type == cls.PREFERENCES:
                    return os.path.join(shotgun_home_override, "preferences")
                elif path_type == cls.LOGGING:
                    return os.path.join(shotgun_home_override, "logs")
                else:
                    raise ValueError("Unsupported path type!")
            # current generation of paths
            elif is_macos():
                if path_type == cls.CACHE:
                    return os.path.expanduser("~/Library/Caches/Shotgun")
                elif path_type == cls.PERSISTENT:
                    return os.path.expanduser("~/Library/Application Support/Shotgun")
                elif path_type == cls.PREFERENCES:
                    return os.path.expanduser("~/Library/Preferences/Shotgun")
                elif path_type == cls.LOGGING:
                    return os.path.expanduser("~/Library/Logs/Shotgun")
                else:
                    raise ValueError("Unsupported path type!")

            elif is_windows():
                app_data = os.environ.get("APPDATA", "APPDATA_NOT_SET")
                if path_type == cls.CACHE:
                    return os.path.join(app_data, "Shotgun")
                elif path_type == cls.PERSISTENT:
                    return os.path.join(app_data, "Shotgun", "Data")
                elif path_type == cls.PREFERENCES:
                    return os.path.join(app_data, "Shotgun", "Preferences")
                elif path_type == cls.LOGGING:
                    return os.path.join(app_data, "Shotgun", "Logs")
                else:
                    raise ValueError("Unsupported path type!")

            elif is_linux():
                if path_type == cls.CACHE:
                    return os.path.expanduser("~/.shotgun")
                elif path_type == cls.PERSISTENT:
                    return os.path.expanduser("~/.shotgun/data")
                elif path_type == cls.PREFERENCES:
                    return os.path.expanduser("~/.shotgun/preferences")
                elif path_type == cls.LOGGING:
                    return os.path.expanduser("~/.shotgun/logs")
                else:
                    raise ValueError("Unsupported path type!")

            else:
                raise ValueError("Unknown platform: %s" % sgsix.platform)

        if generation == cls.CORE_V17:

            # previous generation of paths
            if is_macos():
                if path_type == cls.CACHE:
                    return os.path.expanduser("~/Library/Caches/Shotgun")
                elif path_type == cls.PERSISTENT:
                    return os.path.expanduser("~/Library/Application Support/Shotgun")
                elif path_type == cls.LOGGING:
                    return os.path.expanduser("~/Library/Logs/Shotgun")
                else:
                    raise ValueError("Unsupported path type!")

            elif is_windows():
                if path_type == cls.CACHE:
                    return os.path.join(
                        os.environ.get("APPDATA", "APPDATA_NOT_SET"), "Shotgun"
                    )
                elif path_type == cls.PERSISTENT:
                    return os.path.join(
                        os.environ.get("APPDATA", "APPDATA_NOT_SET"), "Shotgun"
                    )
                elif path_type == cls.LOGGING:
                    return os.path.join(
                        os.environ.get("APPDATA", "APPDATA_NOT_SET"), "Shotgun"
                    )
                else:
                    raise ValueError("Unsupported path type!")

            elif is_linux():
                if path_type == cls.CACHE:
                    return os.path.expanduser("~/.shotgun")
                elif path_type == cls.PERSISTENT:
                    return os.path.expanduser("~/.shotgun")
                elif path_type == cls.LOGGING:
                    return os.path.expanduser("~/.shotgun")
                else:
                    raise ValueError("Unsupported path type!")

            else:
                raise ValueError("Unknown platform: %s" % sgsix.platform)

    @classmethod
    def get_site_root(cls, hostname, path_type, generation=CORE_V18):
        """
        Returns a cache root where items can be stored on a per site basis.

        For more details, see :meth:`LocalFileStorageManager.get_global_root`.

        .. note:: This method does not ensure that the folder exists.

        :param hostname: Shotgun hostname as string, e.g. 'https://foo.shotgunstudio.com'
        :param path_type: Type of path to return. One of ``LocalFileStorageManager.LOGGING``,
                          ``LocalFileStorageManager.CACHE``, ``LocalFileStorageManager.PERSISTENT``, where
                          logging is a path where log- and debug related data should be stored,
                          cache is a location intended for cache data, e.g. data that can be deleted
                          without affecting the state of execution, and persistent is a location intended
                          for data that is meant to be persist. This includes things like settings and
                          preferences.
        :param generation: Path standard generation to use. Defaults to ``LocalFileStorageManager.CORE_V18``,
                           which is the current generation of paths.
        :return: Path as string
        """
        if hostname is None:
            raise TankError(
                "Cannot compute path for local site specific storage - no PTR hostname specified!"
            )

        # get site only; https://www.FOO.com:8080 -> www.foo.com
        base_url = urllib.parse.urlparse(hostname).netloc.split(":")[0].lower()

        if generation > cls.CORE_V17:
            # for 0.18, in order to apply further shortcuts to avoid hitting
            # MAX_PATH on windows, strip shotgunstudio.com from all
            # hosted sites
            #
            # mysite.shotgunstudio.com -> mysite
            # shotgun.internal.int     -> shotgun.internal.int
            #
            base_url = base_url.replace(".shotgunstudio.com", "").replace(
                ".shotgrid.autodesk.com", ""
            )

        return os.path.join(cls.get_global_root(path_type, generation), base_url)

    @classmethod
    def get_configuration_root(
        cls,
        hostname,
        project_id,
        plugin_id,
        pipeline_config_id,
        path_type,
        generation=CORE_V18,
    ):
        """
        Returns the storage root for any data that is project and config specific.

        - A well defined project id should always be passed. Passing None as the project
          id indicates that the *site* configuration, a special toolkit configuration
          that represents the non-project state in Shotgun.

        - Configurations that have a pipeline configuration in Shotgun should pass in
          a pipeline configuration id. When a pipeline configuration is not registered
          in Shotgun, this value should be None.

        - If the configuration has been bootstrapped or has a known plugin id, this
          should be specified via the plugin id parameter.

        For more details, see :meth:`LocalFileStorageManager.get_global_root`.

        Examples of paths that will be generated:

        - Site config: ``ROOT/shotgunsite/p0``
        - Project 123, config 33: ``ROOT/shotgunsite/p123c33``
        - project 123, no config, plugin id review.rv: ``ROOT/shotgunsite/p123.review.rv``

        .. note:: This method does not ensure that the folder exists.

        :param hostname: Shotgun hostname as string, e.g. 'https://foo.shotgunstudio.com'
        :param project_id: Shotgun project id as integer. For the site config, this should be None.
        :param plugin_id: Plugin id string to identify the scope for a particular plugin
                          or integration. For more information,
                          see :meth:`~sgtk.bootstrap.ToolkitManager.plugin_id`. For
                          non-plugin based toolkit projects, this value is None.
        :param pipeline_config_id: Shotgun pipeline config id. None for bootstraped configs.
        :param path_type: Type of path to return. One of ``LocalFileStorageManager.LOGGING``,
                          ``LocalFileStorageManager.CACHE``, ``LocalFileStorageManager.PERSISTENT``, where
                          logging is a path where log- and debug related data should be stored,
                          cache is a location intended for cache data, e.g. data that can be deleted
                          without affecting the state of execution, and persistent is a location intended
                          for data that is meant to be persist. This includes things like settings and
                          preferences.
        :param generation: Path standard generation to use. Defaults to ``LocalFileStorageManager.CORE_V18``,
                           which is the current generation of paths.
        :return: Path as string
        """
        if generation == cls.CORE_V17:
            # in order to be backwards compatible with pre-0.18 cache locations,
            # handle the site configuration (e.g. when project id is None)
            # as project id zero.
            if project_id is None:
                project_id = 0

            # older paths are of the form root/mysite.shotgunstudio.com/project_123/config_123
            return os.path.join(
                cls.get_site_root(hostname, path_type, generation),
                "project_%s" % project_id,
                "config_%s" % pipeline_config_id,
            )

        else:

            # new paths are on the form
            # project 123, config 33:       root/mysite/p123c33
            # project 123 with plugin id:   root/mysite/p123.review.rv
            # site project:                 root/mysite/site

            pc_suffix = ""
            if pipeline_config_id and not plugin_id:
                # a config that has a shotgun counterpart
                pc_suffix = "c%d" % pipeline_config_id
            elif plugin_id and not pipeline_config_id:
                # no pc id but instead an plugin id string
                pc_suffix = ".%s" % filesystem.create_valid_filename(plugin_id)
            elif plugin_id and pipeline_config_id:
                pc_suffix = "c%d.%s" % (
                    pipeline_config_id,
                    filesystem.create_valid_filename(plugin_id),
                )
            else:
                # No pipeline config id nor plugin id which is possible for caching
                # at the site level.
                pc_suffix = ""

            if project_id is None:
                # site config
                project_config_folder = "site%s" % pc_suffix
            else:
                project_config_folder = "p%d%s" % (project_id, pc_suffix)

            return os.path.join(
                cls.get_site_root(hostname, path_type, generation),
                project_config_folder,
            )
