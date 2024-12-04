# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Environment Settings Object and access.

"""

import os
import sys
import copy

from tank_vendor import yaml
from .bundle import resolve_default_value
from . import constants
from . import environment_includes
from ..errors import TankError, TankUnreadableFileError
from .errors import TankMissingEnvironmentFile

from ..util.yaml_cache import g_yaml_cache
from .. import LogManager
from tank_vendor import six
from tank_vendor.shotgun_api3.lib import sgsix

logger = LogManager.get_logger(__name__)


class Environment(object):
    """
    This class encapsulates an environment file and provides a set of methods
    for quick and easy extraction of data from the environment and metadata
    about the different parts of the configuration (by pulling the info.yml
    files from the various apps and engines referenced in the environment file)

    This class contains immutable methods only, e.g. you can only read from
    the yaml file. If you want to modify the yaml content, create a
    WritableEnvironment instance instead.
    """

    def __init__(self, env_path, context=None):
        """
        :param env_path: Path to the environment file
        :param context: Optional context object. If this is omitted,
                        context-based include file resolve will be
                        skipped.
        """
        self._env_path = env_path
        self._env_data = None

        self.__engine_locations = {}
        self.__app_locations = {}
        self.__framework_locations = {}
        self.__context = context

        # validate and populate config
        self._refresh()

    def __repr__(self):
        return "<Sgtk Environment %s>" % self._env_path

    def __str__(self):
        return "Environment %s" % os.path.basename(self._env_path)

    def _refresh(self):
        """Refreshes the environment data from disk
        """
        data = self.__load_environment_data()

        self._env_data = environment_includes.process_includes(
            self._env_path, data, self.__context
        )

        if not self._env_data:
            raise TankError("No data in env file: %s" % (self._env_path))

        if "engines" not in self._env_data:
            raise TankError("No 'engines' section in env file: %s" % (self._env_path))

        # now organize the data in dictionaries

        # framework settings are keyed by fw name
        self.__framework_settings = {}
        # engine settings are keyed by engine name
        self.__engine_settings = {}
        # app settings are keyed by tuple (engine_name, app_name)
        self.__app_settings = {}

        # populate the above data structures
        # pass a copy of the data since process is destructive
        d = copy.deepcopy(self._env_data)
        self.__process_engines(d.get("engines"))

        if "frameworks" in self._env_data:
            # there are frameworks defined! Process them
            self.__process_frameworks(d.get("frameworks"))

        # now extract the location key for all the configs
        # these two dicts are keyed in the same way as the settings dicts
        self.__engine_locations = {}
        self.__app_locations = {}
        self.__framework_locations = {}
        self.__extract_locations()

    def __validate_settings(self, name, settings):
        """
        Validates the engine/app/framework settings dictionary
        """

        # Make sure the settings dict is not empty
        if not settings:
            raise TankError(
                'No settings found for "{}" in {}'.format(name, self.disk_location)
            )

        # Make sure the required keys exist and have values
        required_keys = [constants.ENVIRONMENT_LOCATION_KEY]
        for key in required_keys:
            if key not in settings:
                raise TankError(
                    '"{}" key missing in the definition of "{}" in file {}'.format(
                        key, name, self.disk_location
                    )
                )
            if settings[key] is None:
                raise TankError(
                    '"{}" key of "{}" has an empty definition in file {}'.format(
                        key, name, self.disk_location
                    )
                )

    def __is_item_disabled(self, settings):
        """
        handles the checks to see if an item is disabled
        """
        # TODO: This should be redesigned to use the descriptor API disabled and disabled_platforms properties to help
        #       better encapsulate the feature?
        descriptor_dict = settings.get(constants.ENVIRONMENT_LOCATION_KEY)

        # Check for disabled and deny_platforms
        is_disabled = descriptor_dict.get("disabled", False)
        if is_disabled:
            return True

        # now check if the current platform is disabled
        deny_platforms = descriptor_dict.get("deny_platforms", [])
        # current os: linux/mac/windows
        nice_system_name = {"linux2": "linux", "darwin": "mac", "win32": "windows"}[
            sgsix.platform
        ]
        if nice_system_name in deny_platforms:
            return True

        return False

    def __process_apps(self, engine, data):
        """
        Populates the __app_settings dict
        """
        if data is None:
            return
        # iterate over the apps dict
        for app, app_settings in data.items():
            self.__validate_settings(app, app_settings)
            if not self.__is_item_disabled(app_settings):
                self.__app_settings[(engine, app)] = app_settings

    def __process_engines(self, engines):
        """
        Populates the __engine_settings dict
        """
        if engines is None:
            return
        # iterate over the engine dict
        for engine, engine_settings in engines.items():
            self.__validate_settings(engine, engine_settings)
            # Check for engine disabled
            if not self.__is_item_disabled(engine_settings):
                engine_apps = engine_settings.pop("apps")
                self.__process_apps(engine, engine_apps)
                self.__engine_settings[engine] = engine_settings

    def __process_frameworks(self, frameworks):
        """
        Populates the __frameworks_settings dict
        """
        if frameworks is None:
            return

        for fw, fw_settings in frameworks.items():
            self.__validate_settings(fw, fw_settings)
            # Check for framework disabled
            if not self.__is_item_disabled(fw_settings):
                self.__framework_settings[fw] = fw_settings

    def __extract_locations(self):
        """
        Extract (remove from settings) the location key into the two separate structures
        self.__engine_locations
        self.__app_locations
        self.__framework_locations
        """

        for fw in self.__framework_settings:
            descriptor_dict = self.__framework_settings[fw].get(
                constants.ENVIRONMENT_LOCATION_KEY
            )
            if descriptor_dict is None:
                raise TankError(
                    "The environment %s does not have a valid location "
                    "key for framework %s" % (self._env_path, fw)
                )
            # remove location from dict
            self.__framework_locations[fw] = self.__framework_settings[fw].pop(
                constants.ENVIRONMENT_LOCATION_KEY
            )

        for eng in self.__engine_settings:
            descriptor_dict = self.__engine_settings[eng].get(
                constants.ENVIRONMENT_LOCATION_KEY
            )
            if descriptor_dict is None:
                raise TankError(
                    "The environment %s does not have a valid location "
                    "key for engine %s" % (self._env_path, eng)
                )
            # remove location from dict
            self.__engine_locations[eng] = self.__engine_settings[eng].pop(
                constants.ENVIRONMENT_LOCATION_KEY
            )

        for (eng, app) in self.__app_settings:
            descriptor_dict = self.__app_settings[(eng, app)].get(
                constants.ENVIRONMENT_LOCATION_KEY
            )
            if descriptor_dict is None:
                raise TankError(
                    "The environment %s does not have a valid location "
                    "key for app %s.%s" % (self._env_path, eng, app)
                )
            # remove location from dict
            self.__engine_locations[(eng, app)] = self.__app_settings[(eng, app)].pop(
                constants.ENVIRONMENT_LOCATION_KEY
            )

    def __load_data(self, path):
        """
        loads the main data from disk, raw form
        """
        logger.debug("Loading environment data from path: %s", path)
        return g_yaml_cache.get(path) or {}

    def __load_environment_data(self):
        """
        Loads the main environment data file.

        :returns: Dictionary of the data.

        :raises TankMissingEnvironmentFile: Raised if the environment file does not exist on disk.
        """
        try:
            return self.__load_data(self._env_path)
        except TankUnreadableFileError:
            logger.exception("Missing environment file:")
            raise TankMissingEnvironmentFile(
                "Missing environment file: %s" % self._env_path
            )

    ##########################################################################################
    # Properties

    @property
    def name(self):
        """
        returns the environment name, e.g. the file name of the environment file
        without its extension
        """
        file_name_with_ext = os.path.basename(self._env_path)
        (file_name, ext) = os.path.splitext(file_name_with_ext)
        return file_name

    @property
    def description(self):
        """
        Returns a description of this environment
        """
        return self._env_data.get("description", "No description found.")

    @property
    def disk_location(self):
        """
        Returns a path to this environment
        """
        return self._env_path

    ##########################################################################################
    # Public methods - data retrieval

    def get_engines(self):
        """
        Returns all the engines contained in this environment file
        """
        return list(self.__engine_settings.keys())

    def get_frameworks(self):
        """
        Returns all the frameworks contained in this environment file
        """
        return list(self.__framework_settings.keys())

    def get_apps(self, engine):
        """
        Returns all apps for an engine contained in this environment file
        """
        if engine not in self.get_engines():
            raise TankError(
                "Engine '%s' is not part of environment %s" % (engine, self._env_path)
            )

        apps = []
        engine_app_tuples = list(self.__app_settings.keys())
        for (engine_name, app_name) in engine_app_tuples:
            if engine_name == engine:
                apps.append(app_name)
        return apps

    def get_framework_settings(self, framework):
        """
        Returns the settings for a framework
        """
        d = self.__framework_settings.get(framework)
        if d is None:
            raise TankError(
                "Framework '%s' is not part of environment %s"
                % (framework, self._env_path)
            )
        return d

    def get_engine_settings(self, engine):
        """
        Returns the settings for an engine
        """
        d = self.__engine_settings.get(engine)
        if d is None:
            raise TankError(
                "Engine '%s' is not part of environment %s" % (engine, self._env_path)
            )
        return d

    def get_app_settings(self, engine, app):
        """
        Returns the settings for an app
        """
        key = (engine, app)
        d = self.__app_settings.get(key)
        if d is None:
            raise TankError(
                "App '%s.%s' is not part of environment %s"
                % (engine, app, self._env_path)
            )
        return d

    ##########################################################################################
    # Public methods - data update

    def get_framework_descriptor_dict(self, framework_name):
        """
        Returns the descriptor dictionary for a framework.

        :param framework_name: Name of framework instance
        :returns: descriptor dictionary or uri
        """
        descriptor_dict = self.__framework_locations.get(framework_name)
        if descriptor_dict is None:
            raise TankError(
                "The framework %s does not have a valid location "
                "key for engine %s" % (self._env_path, framework_name)
            )
        return descriptor_dict

    def get_engine_descriptor_dict(self, engine_name):
        """
        Returns the descriptor dictionary for an engine.

        :param engine_name: Name of engine instance
        :returns: descriptor dictionary or uri
        """
        descriptor_dict = self.__engine_locations.get(engine_name)
        if descriptor_dict is None:
            raise TankError(
                "The environment %s does not have a valid location "
                "key for engine %s" % (self._env_path, engine_name)
            )
        return descriptor_dict

    def get_app_descriptor_dict(self, engine_name, app_name):
        """
        Returns the descriptor dictionary for an app.

        :param engine_name: Name of engine instance
        :param app_name: Name of app instance
        :returns: descriptor dictionary or uri
        """
        descriptor_dict = self.__engine_locations.get((engine_name, app_name))
        if descriptor_dict is None:
            raise TankError(
                "The environment %s does not have a valid location "
                "key for app %s.%s" % (self._env_path, engine_name, app_name)
            )
        return descriptor_dict

    def find_location_for_engine(self, engine_name):
        """
        Returns the filename and a list of dictionary keys where an engine instance resides.
        The dictionary key list (tokens) can be nested, for example [engines, tk-maya] or just flat [tk-maya-ref]

        :param str engine_name: The name of the engine to find

        :returns: (list of tokens, file path)
        :rtype: tuple
        """
        return self._find_location_for_engine(engine_name)

    def _find_location_for_engine(self, engine_name, absolute_location=False):
        """
        Returns the filename and a list of dictionary keys where an engine instance resides.
        The dictionary key list (tokens) can be nested, for example [engines, tk-maya] or just flat [tk-maya-ref]

        :param str engine_name: The name of the engine to find
        :param bool absolute_location: Whether to resolve to the yml file and
            tokens that point to the concrete location descriptor of the bundle.

        :returns: (list of tokens, file path)
        """
        # get the raw data:
        root_yml_data = self.__load_environment_data()

        logger.debug(
            "Finding %s, absolute_location=%s...", engine_name, absolute_location
        )

        # find the location for the engine:
        tokens, path = self.__find_location_for_bundle(
            self._env_path,
            root_yml_data,
            "engines",
            engine_name,
            absolute_location=absolute_location,
        )

        if not path:
            raise TankError(
                "Failed to find the location of the '%s' engine in the '%s' environment!"
                % (engine_name, self._env_path)
            )

        logger.debug("Engine %s found: %s", tokens, path)
        return tokens, path

    def find_framework_instances_from(self, yml_file):
        """
        Returns the list of frameworks available from a file and it's includes inside the environment.

        :params yml_file: Environment file to start the search from.

        :returns: List of framework instances accessible from the file.
        """
        if yml_file is None:
            return self.get_frameworks()
        else:
            return [
                fw
                for fw in self.get_frameworks()
                if self._is_framework_available_from(fw, yml_file)
            ]

    def _is_framework_available_from(self, framework_name, starting_point):
        """
        Tests if a framework is reachable from a given file in the environment by following its includes.

        :param framework_name: Name of the framework instance to search for, e.g. tk-framework-something_v1.x.x
        :param starting_point: First file to start looking for the framework.

        :returns: True if the framework is available from the starting point, False otherwise.
        """
        fw_location = environment_includes.find_framework_location(
            starting_point, framework_name, self.__context
        )
        return True if fw_location else False

    def find_location_for_framework(self, framework_name):
        """
        Returns the filename and a list of dictionary keys where a framework instance resides.
        The dictionary key list (tokens) can be nested, for example [frameworks, tk-framework-widget_v0.2.x]
        or just flat [tk-framework-widget_v0.2.x]

        :param framework_name: The name of the framework to find the location of

        :returns: (list of tokens, file path)
        :rtype: tuple
        """
        return self._find_location_for_framework(framework_name)

    def _find_location_for_framework(self, framework_name, absolute_location=False):
        """
        Returns the filename and a list of dictionary keys where a framework instance resides.
        The dictionary key list (tokens) can be nested, for example [frameworks, tk-framework-widget_v0.2.x]
        or just flat [tk-framework-widget_v0.2.x]

        Note, this tries a two stage search.  It first looks to see if there is a matching
        framework in a regular 'frameworks' block in this or any included file.  This matches
        the behaviour at run-time to ensure the framework that is found is the same as one
        that is used!

        The second stage is to check for a framework (or frameworks block) that has been
        specified using the @include syntax.

        :param framework_name: The name of the framework to find the location of
        :param bool absolute_location: Whether to resolve to the yml file and
            tokens that point to the concrete location descriptor of the bundle.

        :returns: (list of tokens, file path)
        :rtype: tuple
        """
        # first, try to find the place on disk of the framework definition that will be used at
        # run-time.  This handles the special case where multiple 'frameworks' blocks from
        # different levels of included files have been concatenated together.
        fw_location = environment_includes.find_framework_location(
            self._env_path, framework_name, self.__context
        )

        if not fw_location:
            # assume the framework is in the environment - this also handles the @include syntax
            # not handled by the previous search method!
            fw_location = self._env_path

        # get the raw data
        root_yml_data = self.__load_data(fw_location)

        # find the location for the framework:
        logger.debug(
            "Finding %s, absolute_location=%s...", framework_name, absolute_location
        )
        tokens, path = self.__find_location_for_bundle(
            fw_location,
            root_yml_data,
            "frameworks",
            framework_name,
            absolute_location=absolute_location,
        )

        if not path:
            raise TankError(
                "Failed to find the location of the '%s' framework in the '%s' environment!"
                % (framework_name, self._env_path)
            )

        logger.debug("Framework %s found: %s", tokens, path)
        return tokens, path

    def find_location_for_app(self, engine_name, app_name):
        """
        Returns the filename and the dictionary key where an app instance resides.
        The dictionary key list (tokens) can be nested, for example [engines, tk-maya, apps, tk-multi-about]
        or just flat [tk-mylti-about-def]

        :param str engine_name: The name of the engine to look for the app in
        :param str app_name: The name of the app to find

        :returns: (list of tokens, file path)
        :rtype: tuple
        """
        return self._find_location_for_app(engine_name, app_name)

    def _find_location_for_app(self, engine_name, app_name, absolute_location=False):
        """
        Returns the filename and the dictionary key where an app instance resides.
        The dictionary key list (tokens) can be nested, for example [engines, tk-maya, apps, tk-multi-about]
        or just flat [tk-mylti-about-def]

        :param str engine_name: The name of the engine to look for the app in
        :param str app_name: The name of the app to find
        :param bool absolute_location: Whether to resolve to the yml file and
            tokens that point to the concrete location descriptor of the bundle.

        :returns: (list of tokens, file path)
        :rtype: tuple
        """
        logger.debug(
            "Finding %s, engine_name=%s, absolute_location=%s...",
            app_name,
            engine_name,
            absolute_location,
        )
        # first, find the location of the engine:
        (engine_tokens, engine_yml_file) = self.find_location_for_engine(engine_name)

        # load the engine data:
        engine_yml_data = self.__load_data(engine_yml_file)

        # traverse down the token hierarchy and find the data for our engine instance:
        # (The token list looks something like this: ["engines", "tk-maya"])
        engine_data = engine_yml_data
        for x in engine_tokens:
            engine_data = engine_data.get(x)

        # find the location for the app within the engine data:
        tokens, path = self.__find_location_for_bundle(
            engine_yml_file,
            engine_data,
            "apps",
            app_name,
            engine_tokens,
            absolute_location=absolute_location,
        )

        if not path:
            raise TankError(
                "Failed to find the location of the '%s' app under the '%s' engine in the '%s' environment!"
                % (engine_name, app_name, self._env_path)
            )

        logger.debug("App %s found: %s", tokens, path)
        return tokens, path

    def __find_location_for_bundle(
        self,
        yml_file,
        parent_yml_data,
        section_name,
        bundle_name,
        parent_tokens=None,
        absolute_location=False,
    ):
        """
        Return the location for the specified bundle within the specified section of the parent yml
        data block.

        .. note:: The absolute_location should be True or False depending on
            what it is the caller intends to do with the resulting location
            returned. In the situation where the descriptor for the bundle
            is to be updated to a new version, it is ctitical that the location
            returned by this method be the yml file and associated tokens
            housing the concrete descriptor dictionary. The goal is to ensure
            that the new descriptor contents are written to the same yml file
            where the old descriptor is defined, rather than what might be
            an included value from another yml file. A good example is how
            engines are structured in tk-config-basic, where the engine instance
            is defined in a project.yml file, but the engine's location setting
            points to an included value. In the case where absolute_location
            is True, that include will be followed and the yml file where it
            is defined will be returned. If absolute_location were False, the
            yml file where the engine instance itself is defined will be returned,
            meaning the location setting's include will not be resolved and
            followed to its source. There is the need for each of these,
            depending on the situation: when a descriptor is going to be
            updated, absolute_location should be True, and when settings other
            than the descriptor are to be queried or updated, absolute_location
            should be False. In some cases these two will return the same
            thing, but that is not guaranteed and it is entirely up to how
            the config is structured as to whether they are consistent.

        :param str yml_file: The starting environment yml file
        :param dict parent_yml_data: The parent yml data block to start the search from
        :param str section_name: The name of the section that contains the bundle
        :param str bundle_name: The name of the bundle to find
        :param list bundle_tokens: A list of tokens representing the path to the parent data block
        :param bool absolute_location: Whether to ensure that the file path and tokens returned
            references where the given bundle's location descriptor is
            defined in full.

        :returns: (list of tokens, file path)
        :rtype: tuple
        """
        bundle_tokens = list(parent_tokens or [])
        bundle_yml_file = yml_file

        # Check to see if the whole bundle section is a reference.
        bundle_section = parent_yml_data[section_name]
        bundle_data = None

        def is_included(item):
            """
            Tests whether the given item is an included value or not. This
            is determined by whether it is a string, and if so, it is an
            included value if it has an @ at its head.
            """
            return isinstance(item, six.string_types) and item.startswith("@")

        if is_included(bundle_section):
            # The whole section is a reference! The token is just the include
            # definition with the @ at the head chopped off.
            bundle_section_token = bundle_section[1:]
            bundle_yml_file, bundle_section_token = environment_includes.find_reference(
                bundle_yml_file, self.__context, bundle_section_token, absolute_location
            )
            bundle_yml_data = self.__load_data(bundle_yml_file)
            bundle_data = bundle_yml_data[bundle_section_token]
            bundle_tokens = [bundle_section_token]
        else:
            bundle_data = bundle_section.get(bundle_name)
            bundle_tokens.append(section_name)

        if not bundle_data:
            # failed to find the data for the specified bundle!
            return ([], None)

        if is_included(bundle_data):
            # This is a reference, so we need to flatten it out. The token
            # is just the include definition with the @ at the head chopped
            # off.
            bundle_token = bundle_data[1:]
            bundle_yml_file, bundle_token = environment_includes.find_reference(
                bundle_yml_file, self.__context, bundle_token, absolute_location
            )
            bundle_tokens = [bundle_token]
        elif absolute_location:
            # The bundle data isn't included, but we need to make sure that
            # the location is concrete if we've been asked to ensure that.
            location = bundle_data.get(constants.ENVIRONMENT_LOCATION_KEY)

            if is_included(location):
                bundle_yml_file, bundle_token = environment_includes.find_reference(
                    bundle_yml_file,
                    self.__context,
                    location[1:],  # Trim the @ at the head.
                    absolute_location,
                )
                bundle_tokens = [bundle_token]
            else:
                bundle_tokens.append(bundle_name)
        else:
            # bundle is defined in the current file
            bundle_tokens.append(bundle_name)

        return (bundle_tokens, bundle_yml_file)


class InstalledEnvironment(Environment):
    """
    Represents an :class:`Environment` that has been installed
    and has an associated pipeline configuration.

    Don't construct this class by hand! Instead, use the
    pipelineConfiguration.get_environment() method.
    """

    def __init__(self, env_path, pipeline_config, context=None):
        """
        :param env_path: Path to the environment file
        :param pipeline_config: Pipeline configuration assocaited with the installed environment
        :param context: Optional context object. If this is omitted,
                        context-based include file resolve will be
                        skipped.
        """
        super(InstalledEnvironment, self).__init__(env_path, context)
        self.__pipeline_config = pipeline_config

    def get_framework_descriptor(self, framework_name):
        """
        Returns the descriptor object for a framework.

        :param framework_name: Name of framework
        :returns: :class:`~sgtk.descriptor.BundleDescriptor` that represents
                  this object. The descriptor has been configured to use
                  whatever caching settings the associated pipeline
                  configuration is using.
        """
        return self.__pipeline_config.get_framework_descriptor(
            self.get_framework_descriptor_dict(framework_name)
        )

    def get_engine_descriptor(self, engine_name):
        """
        Returns the descriptor object for an engine.

        :param engine_name: Name of engine
        :returns: :class:`~sgtk.descriptor.BundleDescriptor` that represents
                  this object. The descriptor has been configured to use
                  whatever caching settings the associated pipeline
                  configuration is using.
        """
        return self.__pipeline_config.get_engine_descriptor(
            self.get_engine_descriptor_dict(engine_name)
        )

    def get_app_descriptor(self, engine_name, app_name):
        """
        Returns the descriptor object for an app.

        :param engine_name: Name of engine
        :param app_name: Name of app
        :returns: :class:`~sgtk.descriptor.BundleDescriptor` that represents
                  this object. The descriptor has been configured to use
                  whatever caching settings the associated pipeline
                  configuration is using.
        """
        return self.__pipeline_config.get_app_descriptor(
            self.get_app_descriptor_dict(engine_name, app_name)
        )


class WritableEnvironment(InstalledEnvironment):
    """
    Represents a mutable environment.

    If you need to make change to the environment, this class should be used
    rather than the Environment class. Additional methods are added
    to support modification and updates and handling of writing yaml
    content back to disk.
    """

    (NONE, INCLUDE_DEFAULTS, STRIP_DEFAULTS) = range(3)
    """Format enumeration to use when dumping an environment.

    NONE: Don't modify the settings.
    INCLUDE_DEFAULTS: Include all settings, using default values as necessary.
    STRIP_DEFAULTS: Exclude settings using default values.
    """

    def __init__(self, env_path, pipeline_config, context=None):
        """
        :param env_path: Path to the environment file
        :param pipeline_config: Pipeline configuration assocaited with the installed environment
        :param context: Optional context object. If this is omitted,
                        context-based include file resolve will be
                        skipped.
        """
        self.set_yaml_preserve_mode(True)
        super(WritableEnvironment, self).__init__(env_path, pipeline_config, context)

    def __load_writable_yaml(self, path):
        """
        Loads yaml data from disk.

        :param path: Path to yaml file
        :returns: yaml object representing the data structure
        """
        try:
            fh = open(path, "r")
        except Exception as e:
            raise TankError(
                "Could not open file '%s'. Error reported: '%s'" % (path, e)
            )

        try:
            # the ruamel parser doesn't have 2.5 support so
            # only use it on 2.6+
            if self._use_ruamel_yaml_parser and not (sys.version_info < (2, 6)):
                # note that we use the RoundTripLoader loader here. This ensures
                # that structure and comments are preserved when the yaml is
                # written back to disk.
                #
                # the object returned back is a dictionary-like object
                # which also holds the additional contextual metadata
                # required by the parse to maintain the lexical integrity
                # of the content.
                from tank_vendor import ruamel_yaml

                yaml_data = ruamel_yaml.load(fh, ruamel_yaml.RoundTripLoader)
            else:
                # use pyyaml parser
                yaml_data = yaml.load(fh, Loader=yaml.FullLoader)
        except ImportError:
            # In case the ruamel_yaml module cannot be loaded, use pyyaml parser
            # instead. This is known to happen when and old version (<= v1.3.20) of
            # tk-framework-desktopstartup is in use.
            yaml_data = yaml.load(fh, Loader=yaml.FullLoader)
        except Exception as e:
            raise TankError(
                "Could not parse file '%s'. Error reported: '%s'" % (path, e)
            )
        finally:
            fh.close()

        return yaml_data

    def __write_data(self, path, data):
        """
        Writes the yaml data back to disk

        :param path: Path to yaml file
        :param data: yaml data structure to write
        """
        try:
            g_yaml_cache.invalidate(path)
            fh = open(path, "wt")
        except Exception as e:
            raise TankError(
                "Could not open file '%s' for writing. "
                "Error reported: '%s'" % (path, e)
            )

        try:
            self.__write_data_file(fh, data)
        except Exception as e:
            raise TankError(
                "Could not write to environment file '%s'. "
                "Error reported: %s" % (path, e)
            )
        finally:
            fh.close()

    def __write_data_file(self, fh, data):
        """
        Writes the yaml data to a supplied file handle

        :param fh: An open file handle to write to.
        :param data: yaml data structure to write
        """

        try:
            # the ruamel parser doesn't have 2.5 support so
            # only use it on 2.6+
            if self._use_ruamel_yaml_parser and not (sys.version_info < (2, 6)):
                # note that we are using the RoundTripDumper in order to
                # preserve the structure when writing the file to disk.
                #
                # the default_flow_style=False tells the parse to write
                # any modified values on multi-line form, e.g.
                #
                # foo:
                #   bar: 3
                #   baz: 4
                #
                # rather than
                #
                # foo: { bar: 3, baz: 4 }
                #
                # note that safe_dump is not needed when using the
                # roundtrip dumper, it will adopt a 'safe' behaviour
                # by default.
                from tank_vendor import ruamel_yaml

                ruamel_yaml.dump(
                    data,
                    fh,
                    default_flow_style=False,
                    Dumper=ruamel_yaml.RoundTripDumper,
                )
            else:
                # use pyyaml parser
                #
                # using safe_dump instead of dump ensures that we
                # don't serialize any non-std yaml content. In particular,
                # this causes issues if a unicode object containing a 7-bit
                # ascii string is passed as part of the data. in this case,
                # dump will write out a special format which is later on
                # *loaded in* as a unicode object, even if the content doesn't
                # need unicode handling. And this causes issues down the line
                # in toolkit code, assuming strings:
                #
                # >>> yaml.dump({"foo": u"bar"})
                # "{foo: !!python/unicode 'bar'}\n"
                # >>> yaml.safe_dump({"foo": u"bar"})
                # '{foo: bar}\n'
                #
                yaml.safe_dump(data, fh, default_flow_style=None)
        except ImportError:
            # In case the ruamel_yaml module cannot be loaded, use pyyaml parser
            # instead. This is known to happen when an old version (<= v1.3.20)
            # of tk-framework-desktopstartup is being used.
            yaml.safe_dump(data, fh)

    def set_yaml_preserve_mode(self, val):
        """
        If set to true, the ruamel parser will be used instead of the
        traditional pyyaml one. This parser will preserve structure and
        comments and generally try to more gracefully update the yaml
        content

        :param val: True to enable new parser, false to disable
        """
        # environment variable setting overrides
        if constants.USE_LEGACY_YAML_ENV_VAR in os.environ:
            self._use_ruamel_yaml_parser = False
        else:
            self._use_ruamel_yaml_parser = val

    def _update_location_data(self, data, new_location_data):
        """
        Updates the location contents of the given data dictionary
        with that contained in the given new_location_data. If the
        old data contains a location key, that will be replaced with
        with the contents of new_location_data, otherwise the
        new location data will be returned as is.

        :param dict data: The data dictionary to update with the new
            location information.
        :param dict new_location_data: The new location information to
            use.

        :returns: An updated dictionary containing the new location
            information.
        :rtype: dict
        """
        # This is ghetto, but is required given the current design of
        # this environment API and how the updates work. We might be in
        # a situation where we're updating a descriptor, but in a bare
        # data structure in the yml that isn't under a "location" key.
        # This is possible and probably in configs structured like
        # tk-config-basic and tk-config-default2, where we have locations
        # centralized in an include file, and those are then referenced
        # into location settings for bundled in other yml files. In that
        # situation we need to drop the new location into the bundle
        # settings as is, so as not to create a new location key where
        # it isn't correct to have one.
        #
        # It is the difference between the following:
        #
        # common.engines.tk-maya.location:
        #   type: app_store
        #   name: tk-maya
        #   version: v0.8.1
        #
        # And:
        #
        # common.apps.tk-multi-shotgunpanel:
        #   location:
        #     type: app_store
        #     name: tk-multi-shotgunpanel
        #     version: v1.4.3
        #
        # In the former, the new location information is replaced at
        # the top level of the data dictionary. For the latter, the
        # location key's contents is replaced.
        if new_location_data and constants.ENVIRONMENT_LOCATION_KEY in data:
            data[constants.ENVIRONMENT_LOCATION_KEY] = new_location_data
        elif new_location_data:
            data.update(new_location_data)

        return data

    def update_engine_settings(self, engine_name, new_data, new_location):
        """
        Updates the engine configuration
        """

        if engine_name not in self._env_data["engines"]:
            raise TankError(
                "Engine %s does not exist in environment %s"
                % (engine_name, self._env_path)
            )

        # In this case, we want to make sure that we are getting the
        # yml file where the engine's location descriptor is defined
        # in a concrete manner (ie: the actual dict and not an include
        # to another yml file). The absolute_location argument will allow
        # us to do that.
        (tokens, yml_file) = self._find_location_for_engine(
            engine_name, absolute_location=True
        )

        # now update the yml file where the engine is defined
        yml_data = self.__load_writable_yaml(yml_file)

        # now the token may be either [my-maya-ref] or [engines, tk-maya]
        # find the right chunk in the file
        engine_data = yml_data
        for x in tokens:
            engine_data = engine_data.get(x)

        # Update our data with the new location.
        engine_data = self._update_location_data(engine_data, new_location)

        self._update_settings_recursive(engine_data, new_data)
        self.__write_data(yml_file, yml_data)

        # sync internal data with disk
        self._refresh()

    def update_app_settings(self, engine_name, app_name, new_data, new_location):
        """
        Updates the app configuration.
        """

        if engine_name not in self._env_data["engines"]:
            raise TankError(
                "Engine %s does not exist in environment %s"
                % (engine_name, self._env_path)
            )
        if app_name not in self._env_data["engines"][engine_name]["apps"]:
            raise TankError(
                "App %s.%s does not exist in environment %s"
                % (engine_name, app_name, self._env_path)
            )

        # In this case, we want to make sure that we are getting the
        # yml file where the app's location descriptor is defined
        # in a concrete manner (ie: the actual dict and not an include
        # to another yml file). The absolute_location argument will allow
        # us to do that.
        (tokens, yml_file) = self._find_location_for_app(
            engine_name, app_name, absolute_location=True
        )

        # now update the yml file where the engine is defined
        yml_data = self.__load_writable_yaml(yml_file)

        # now the token may be either [my-maya-ref] or [engines, tk-maya]
        # find the right chunk in the file
        app_data = yml_data
        for x in tokens:
            app_data = app_data.get(x)

        # Update our data with the new location information.
        app_data = self._update_location_data(app_data, new_location)

        self._update_settings_recursive(app_data, new_data)
        self.__write_data(yml_file, yml_data)

        # sync internal data with disk
        self._refresh()

    def update_framework_settings(self, framework_name, new_data, new_location):
        """
        Updates the framework configuration
        """

        if framework_name not in self._env_data["frameworks"]:
            raise TankError(
                "Framework %s does not exist in environment %s"
                % (framework_name, self._env_path)
            )

        # In this case, we want to make sure that we are getting the
        # yml file where the framework's location descriptor is defined
        # in a concrete manner (ie: the actual dict and not an include
        # to another yml file). The absolute_location argument will allow
        # us to do that.
        (tokens, yml_file) = self._find_location_for_framework(
            framework_name, absolute_location=True
        )

        # now update the yml file where the engine is defined
        yml_data = self.__load_writable_yaml(yml_file)

        # now the token may be either [my_fw_ref] or [frameworks, tk-framework-widget_v0.1.x]
        # find the right chunk in the file
        framework_data = yml_data
        for x in tokens:
            framework_data = framework_data.get(x)

        # Update our data with the new location information.
        framework_data = self._update_location_data(framework_data, new_location)

        self._update_settings_recursive(framework_data, new_data)
        self.__write_data(yml_file, yml_data)

        # sync internal data with disk
        self._refresh()

    def _update_settings_recursive(self, settings, new_data):
        """
        Recurse through new data passed in and update settings structure accordingly.

        :param settings: settings dictionary to update with the new values
        :parma new_data: new settings data to update into the settings dictionary
        """
        for name, data in new_data.items():
            # if data is a dictionary then we may need to recurse to update nested settings:
            if isinstance(data, dict):
                setting = settings.get(name)
                if setting:
                    if isinstance(setting, list):
                        # need to handle a list of dictionaries so update
                        # each item in the list with the new data:
                        for item in setting:
                            if isinstance(item, dict):
                                # make sure we have a unique instance of the data
                                # for each item in the list
                                item_data = copy.deepcopy(data)
                                # recurse:
                                self._update_settings_recursive(item, item_data)
                            else:
                                # setting type doesn't match data type so skip!
                                pass

                    elif isinstance(setting, dict):
                        # recurse:
                        self._update_settings_recursive(setting, data)
                    else:
                        # setting type doesn't match data type so skip!
                        pass
                else:
                    # setting didn't exist before so just add it:
                    settings[name] = data

            else:
                # add new or update existing setting:
                settings[name] = data

    def create_framework_settings(self, yml_file, framework_name, params, location):
        """
        Creates new framework settings.
        """

        data = self.__load_writable_yaml(yml_file)

        if data.get("frameworks") is None:
            data["frameworks"] = {}

        # it is possible that the whole framework is referenced via an @include. In this case,
        # raise an error. Here's an example structure of what that looks like:
        #
        # frameworks: '@included_fw'
        frameworks_section = data["frameworks"]
        if isinstance(frameworks_section, str) and frameworks_section.startswith("@"):
            raise TankError(
                "The frameworks section in environment file '%s' is a reference to another file. "
                "This type of configuration arrangement cannot currently be automatically "
                "modified - please edit it by hand! Please add the following to your external "
                "framework include: "
                "%s: { %s: %s }. "
                "If the framework has any settings, these need to be added "
                "by hand."
                % (
                    self._env_path,
                    framework_name,
                    constants.ENVIRONMENT_LOCATION_KEY,
                    location,
                )
            )

        if framework_name in data["frameworks"]:
            raise TankError(
                "Framework %s already exists in environment %s"
                % (framework_name, yml_file)
            )

        data["frameworks"][framework_name] = {}
        data["frameworks"][framework_name][
            constants.ENVIRONMENT_LOCATION_KEY
        ] = location
        self._update_settings_recursive(data["frameworks"][framework_name], params)

        self.__write_data(yml_file, data)
        # sync internal data with disk
        self._refresh()

    def create_engine_settings(self, engine_name):
        """
        Creates a new engine settings chunk in the root file of the env tree.
        """

        data = self.__load_writable_yaml(self._env_path)

        if engine_name in data["engines"]:
            raise TankError(
                "Engine %s already exists in environment %s"
                % (engine_name, self._env_path)
            )

        data["engines"][engine_name] = {}
        # and make sure we also create the location key
        data["engines"][engine_name][constants.ENVIRONMENT_LOCATION_KEY] = {}
        # and make sure we also create the apps key
        data["engines"][engine_name]["apps"] = {}

        self.__write_data(self._env_path, data)
        # sync internal data with disk
        self._refresh()

    def __verify_engine_local(self, data, engine_name):
        """
        It is possible that the whole engine is referenced via an @include. In this case,
        raise an error. Here's an example structure of what that looks like:

        engines:
          tk-houdini: '@tk-houdini-shot'
          tk-maya: '@tk-maya-shot-lighting'
          tk-motionbuilder: '@tk-motionbuilder-shot'

        :param data: The raw environment data without processing
        :param engine_name: The name of an engine instance
        """
        engines_section = data["engines"][engine_name]
        if isinstance(engines_section, str) and engines_section.startswith("@"):
            raise TankError(
                "The configuration for engine '%s' located in the environment file '%s' has a "
                "reference to another file ('%s'). This type "
                "of configuration arrangement cannot currently be automatically "
                "modified - please edit it by hand!"
                % (engine_name, self._env_path, engines_section)
            )

    def __verify_apps_local(self, data, engine_name):
        """
        It is possible that the 'apps' dictionary is actually an @include. In this case,
        raise an error. Here's an example of what this looks like:

        tk-maya:
          apps: '@maya_apps'
          debug_logging: false
          location: {name: tk-maya, type: app_store, version: v0.3.9}
        """
        apps_section = data["engines"][engine_name]["apps"]
        if isinstance(apps_section, str) and apps_section.startswith("@"):
            raise TankError(
                "The configuration for engine '%s' located in the environment file '%s' has an "
                "apps section which is referenced from another file ('%s'). This type "
                "of configuration arrangement cannot currently be automatically "
                "modified - please edit it by hand!"
                % (engine_name, self._env_path, apps_section)
            )

    def create_app_settings(self, engine_name, app_name):
        """
        Creates a new app settings chunk in the root file of the env tree.
        """

        data = self.__load_writable_yaml(self._env_path)

        # check that the engine name exists in the config
        if engine_name not in data["engines"]:
            raise TankError(
                "Engine %s does not exist in environment %s"
                % (engine_name, self._env_path)
            )

        # make sure the engine's apps setting is local to this file
        self.__verify_engine_local(data, engine_name)
        self.__verify_apps_local(data, engine_name)

        # because of yaml, for engines with no apps at all, the apps section may have initialized to a null value
        if data["engines"][engine_name]["apps"] is None:
            data["engines"][engine_name]["apps"] = {}

        # check that it doesn't already exist
        apps_section = data["engines"][engine_name]["apps"]

        if app_name in apps_section:
            raise TankError(
                "App %s.%s already exists in environment %s"
                % (engine_name, app_name, self._env_path)
            )

        data["engines"][engine_name]["apps"][app_name] = {}
        # and make sure we also create the location key
        data["engines"][engine_name]["apps"][app_name][
            constants.ENVIRONMENT_LOCATION_KEY
        ] = {}

        self.__write_data(self._env_path, data)
        # sync internal data with disk
        self._refresh()

    def copy_apps(self, src_engine_name, dst_engine_name):
        """
        Copies the raw app settings from the source engine to the destination engine.
        The copied settings are the raw yaml strings that have not gone through any processing.

        :param src_engine_name: The name of the engine instance to copy from (str)
        :param dst_engine_name: The name of the engine instance to copy to (str)
        """
        data = self.__load_writable_yaml(self._env_path)

        # check that the engine names exists in the config
        if src_engine_name not in data["engines"]:
            raise TankError(
                "Engine %s does not exist in environment %s"
                % (src_engine_name, self._env_path)
            )
        if dst_engine_name not in data["engines"]:
            raise TankError(
                "Engine %s does not exist in environment %s"
                % (dst_engine_name, self._env_path)
            )

        # make sure the actual engine settings are both local
        self.__verify_engine_local(data, src_engine_name)
        self.__verify_engine_local(data, dst_engine_name)

        # copy the settings over
        src_apps_section = data["engines"][src_engine_name]["apps"]
        data["engines"][dst_engine_name]["apps"] = copy.deepcopy(src_apps_section)

        self.__write_data(self._env_path, data)
        # sync internal data with disk
        self._refresh()

    ############################################################################
    # Methods specific to dumping environment settings

    def dump(self, file, transform, include_debug_comments=True):
        """
        Dump a copy of this environment's settings to the supplied file handle.

        :param file: A file handle to write to.
        :param transform: WritableEnvironment.[NONE | INCLUDE_DEFAULTS |
            STRIP_DEFAULTS]
        :param include_debug_comments: Include debug comments in the dumped
            settings.
        """

        # load the output path's yaml
        yml_data = self.__load_writable_yaml(self._env_path)

        # process each of the engines for the environment
        for engine_name in self.get_engines():

            # only process settings in this file
            (tokens, engine_file) = self.find_location_for_engine(engine_name)
            if not engine_file == self._env_path:
                continue

            # drill down into the yml data to find the chunk where the
            # engine settings live
            engine_settings = yml_data
            for token in tokens:
                engine_settings = engine_settings.get(token)

            # get information about the engine in order to process the
            # settings.
            engine_descriptor = self.get_engine_descriptor(engine_name)
            engine_schema = engine_descriptor.configuration_schema
            engine_manifest_file = os.path.join(
                engine_descriptor.get_path(), constants.BUNDLE_METADATA_FILE
            )

            # update the settings by adding or removing keys based on the
            # type of dumping being performed.
            self._update_settings(
                transform,
                engine_schema,
                engine_settings,
                engine_name,
                engine_manifest_file,
                include_debug_comments,
            )

            # processing all the installed apps
            for app_name in self.get_apps(engine_name):

                # only process settings in this file
                (tokens, app_file) = self.find_location_for_app(engine_name, app_name)
                if not app_file == self._env_path:
                    continue

                # drill down into the yml data to find the chunk where the
                # app settings live
                app_settings = yml_data
                for token in tokens:
                    app_settings = app_settings.get(token)

                # get information about the app in order to process the
                # settings.
                app_descriptor = self.get_app_descriptor(engine_name, app_name)
                app_schema = app_descriptor.configuration_schema
                app_manifest_file = os.path.join(
                    app_descriptor.get_path(), constants.BUNDLE_METADATA_FILE
                )

                # update the settings by adding or removing keys based on the
                # type of dumping being performed.
                self._update_settings(
                    transform,
                    app_schema,
                    app_settings,
                    engine_name,
                    app_manifest_file,
                    include_debug_comments,
                )

        # processing all the frameworks
        for fw_name in self.get_frameworks():

            # only process settings in this file
            (tokens, fw_file) = self.find_location_for_framework(fw_name)
            if not fw_file == self._env_path:
                continue

            # drill down into the yml data to find the chunk where the
            # framework settings live
            fw_settings = yml_data
            for token in tokens:
                fw_settings = fw_settings.get(token)

            # get information about the framework in order to process the
            # settings.
            fw_descriptor = self.get_framework_descriptor(fw_name)
            fw_schema = fw_descriptor.configuration_schema
            fw_manifest_file = os.path.join(
                fw_descriptor.get_path(), constants.BUNDLE_METADATA_FILE
            )

            # update the settings by adding or removing keys based on the
            # type of dumping being performed.
            self._update_settings(
                transform,
                fw_schema,
                fw_settings,
                fw_manifest_file,
                include_debug_comments,
            )

        try:
            self.__write_data_file(file, yml_data)
        except Exception as e:
            raise TankError(
                "Could not write to environment file handle. "
                "Error reported: %s" % (e,)
            )

    def _update_settings(
        self,
        transform,
        schema,
        settings,
        engine_name=None,
        manifest_file=None,
        include_debug_comments=False,
    ):
        """
        Given a schema and settings, update them based on the specified
        transform mode.

        :param transform: one of WritableEnvironment.[NONE | INCLUDE_DEFAULTS |
            STRIP_DEFAULTS]
        :param schema: A schema defining types and defaults for settings.
        :param settings: A dict of settings to sparsify.
        :param engine_name: The name of the current engine
        :param manifest_file: The path to the manifest file if known.
        :param include_debug_comments: If True, include debug comments on lines
            using a non-default value.

        :returns: bool - True if the settings were modified, False otherwise.
        """

        modified = False

        # check each key defined in the schema
        for setting_name in schema.keys():

            # this setting's schema
            setting_schema = schema[setting_name]

            # the default value from the schema
            schema_default = resolve_default_value(
                setting_schema, engine_name=engine_name
            )

            if setting_name in settings and transform == self.STRIP_DEFAULTS:

                # the setting is in the environment and we are removing default
                # values. see if the value is a default.

                # the value in the environment
                setting_value = settings[setting_name]

                # the setting type to address any special cases
                setting_type = setting_schema["type"]

                if setting_value == schema_default:

                    # the setting value matches the schema default. remove the
                    # setting.
                    del settings[setting_name]
                    modified = True

                # remove any legacy "default" hook references
                elif setting_type == "hook" and setting_value == "default":
                    del settings[setting_name]
                    modified = True

            elif setting_name not in settings and transform == self.INCLUDE_DEFAULTS:

                # the setting is not in the environment and we are including
                # default values. need to add it.

                settings[setting_name] = str(schema_default)
                modified = True

            # now that we've modified the setting as needed, if debug comments
            # were requested, and this is the new yaml parser (has the method
            # necessary to add the comment) and the setting is still there
            # (wasn't removed for sparse dumping) then add the debug comment.
            # this will add comments when transform was set to NONE as well.
            if (
                include_debug_comments
                and hasattr(settings, "yaml_add_eol_comment")
                and setting_name in settings
            ):

                if schema_default == settings[setting_name]:
                    # The value of the setting matches the default value in the
                    # manifest.
                    debug_comment = "MATCHES: %s default in manifest %s" % (
                        engine_name or "",
                        manifest_file or "",
                    )
                else:
                    debug_comment = "DIFFERS: %s default (%s) in manifest %s" % (
                        engine_name or "",
                        schema_default or '""',
                        manifest_file or "",
                    )

                # now add the comment
                settings.yaml_add_eol_comment(debug_comment, setting_name, column=90)

        return modified
