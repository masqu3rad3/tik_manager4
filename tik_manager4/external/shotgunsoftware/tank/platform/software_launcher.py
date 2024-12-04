# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Defines the base class for DCC application launchers all Toolkit engines
should implement.
"""

import os
import sys
import glob
import pprint

from ..errors import TankError
from ..log import LogManager
from ..util.loader import load_plugin
from ..util.version import is_version_older
from ..util import ShotgunPath, is_windows, sgre as re

from . import constants
from . import validation

from .bundle import resolve_setting_value
from .engine import get_env_and_descriptor_for_engine

# std core level logger
core_logger = LogManager.get_logger(__name__)


def create_engine_launcher(tk, context, engine_name, versions=None, products=None):
    """
    Factory method that creates a :class:`SoftwareLauncher` subclass
    instance implemented by a toolkit engine in the environment config
    that can be used by a custom script or toolkit app. The engine
    subclass manages the business logic for DCC executable path
    discovery and the environmental requirements for launching the DCC.
    Toolkit is automatically started up during the DCC's launch phase.
    A very simple example of how this works is demonstrated here::

        >>> import subprocess
        >>> import sgtk
        >>> tk = sgtk.sgtk_from_path("/studio/project_root")
        >>> context = tk.context_from_path("/studio/project_root/sequences/AAA/ABC/Light/work")
        >>> launcher = sgtk.platform.create_engine_launcher(tk, context, "tk-maya")
        >>> software_versions = launcher.scan_software()
        >>> launch_info = launcher.prepare_launch(
        ...     software_versions[0].path,
        ...     args,
        ...     "/studio/project_root/sequences/AAA/ABC/Light/work/scene.ma"
        ... )
        >>> subprocess.Popen([launch_info.path + " " + launch_info.args], env=launch_info.environment)

    where ``software_versions`` is a list of :class:`SoftwareVersion`
    instances and ``launch_info`` is a :class:`LaunchInformation`
    instance. This example will launch the first version of Maya
    found installed on the local filesystem, automatically start
    the tk-maya engine for that Maya session, and open
    /studio/project_root/sequences/AAA/ABC/Light/work/scene.ma.

    :param tk: :class:`~sgtk.Sgtk` Toolkit instance.
    :param context: :class:`~sgtk.Context` Context to launch the DCC in.
    :param str engine_name: Name of the Toolkit engine associated with
                            the DCC(s) to launch.
    :param list versions: A list of version strings for filtering software
        versions. See the :class:`SoftwareLauncher` for more info.
    :param list products: A list of product strings for filtering software
        versions. See the :class:`SoftwareLauncher` for more info.

    :rtype: :class:`SoftwareLauncher` instance or ``None`` if the
            engine can be found on disk, but no ``startup.py`` file exists.
    :raises: :class:`TankError` if the specified engine cannot be found
             on disk.
    """
    # Get the engine environment and descriptor using engine.py code
    (env, engine_descriptor) = get_env_and_descriptor_for_engine(
        engine_name, tk, context
    )

    # Make sure it exists locally
    if not engine_descriptor.exists_local():
        raise TankError(
            "Cannot create %s software launcher! %s does not exist on disk."
            % (engine_name, engine_descriptor)
        )

    # Get path to engine startup code and load it.
    engine_path = engine_descriptor.get_path()
    plugin_file = os.path.join(engine_path, constants.ENGINE_SOFTWARE_LAUNCHER_FILE)

    # Since we don't know what version of the engine is currently
    # installed, the plugin file may not exist.
    if not os.path.isfile(plugin_file):
        # Nothing to do.
        core_logger.debug(
            "SoftwareLauncher plugin file '%s' does not exist!" % plugin_file
        )
        return None

    core_logger.debug("Loading SoftwareLauncher plugin '%s' ..." % plugin_file)
    class_obj = load_plugin(plugin_file, SoftwareLauncher)
    launcher = class_obj(tk, context, engine_name, env, versions, products)
    core_logger.debug("Created SoftwareLauncher instance: %s" % launcher)

    # Return the SoftwareLauncher instance
    return launcher


class SoftwareLauncher(object):
    """
    Functionality related to the discovery and launch of a DCC. This class
    should only be constructed through the :meth:`create_engine_launcher`
    factory method.
    """

    def __init__(self, tk, context, engine_name, env, versions=None, products=None):
        """
        :param tk: :class:`~sgtk.Sgtk` Toolkit instance

        :param context: A :class:`~sgtk.Context` object to define the
            context on disk where the engine is operating.

        :param str engine_name: Name of the Toolkit engine associated
            with the DCC(s) to launch.

        :param env: An :class:`~sgtk.platform.environment.Environment` object to
            associate with this launcher.

        :param list versions: List of strings representing versions to search
            for. If set to ``None`` or ``[]``, search for all versions. A version string
            is DCC-specific but could be something like "2017", "6.3v7" or
            "1.2.3.52"

        :param list products: List of strings representing product names to
            search for. If set to ``None`` or ``[]``, search for all products. A product
            string is DCC-specific but could be something like "Houdini FX",
            "Houdini Core" or "Houdini"
        """
        # get the engine settings
        settings = env.get_engine_settings(engine_name)

        # get the descriptor representing the engine
        descriptor = env.get_engine_descriptor(engine_name)

        # check that the context contains all the info that the launcher needs
        validation.validate_context(descriptor, context)

        # make sure the current operating system platform is supported
        validation.validate_platform(descriptor)

        # Once validated, initialize members of this class. Since this code only
        # runs during the pre-launch phase of an engine, there are no
        # opportunities to change the Context or environment. Safe to cache
        # these values.
        self.__tk = tk
        self.__context = context
        self.__environment = env
        self.__engine_settings = settings
        self.__engine_descriptor = descriptor
        self.__engine_name = engine_name

        # product and version string lists to limit the scope of sw discovery
        self._products = products or []
        self._lower_case_products = [product.lower() for product in self._products]
        self._versions = versions or []

    ##########################################################################################
    # properties

    @property
    def context(self):
        """
        The :class:`~sgtk.Context` associated with this launcher.
        """
        return self.__context

    @property
    def descriptor(self):
        """
        Internal method - not part of Tank's public interface.
        This method may be changed or even removed at some point in the future.
        We leave no guarantees that it will remain unchanged over time, so
        do not use in any app code.
        """
        return self.__engine_descriptor

    @property
    def settings(self):
        """
        Internal method - not part of Tank's public interface.
        This method may be changed or even removed at some point in the future.
        We leave no guarantees that it will remain unchanged over time, so
        do not use in any app code.
        """
        return self.__engine_settings

    @property
    def sgtk(self):
        """
        The :class:`~sgtk.Sgtk` instance associated with this item
        """
        return self.__tk

    @property
    def disk_location(self):
        """
        The folder on disk where this item is located.
        This can be useful if you want to write app code
        to retrieve a local resource::

            app_font = os.path.join(self.disk_location, "resources", "font.fnt")
        """
        path_to_this_file = os.path.abspath(sys.modules[self.__module__].__file__)
        return os.path.dirname(path_to_this_file)

    @property
    def display_name(self):
        """
        The display name for the item. Automatically
        appends 'Startup' to the end of the display
        name if that string is missing from the display
        name (e.g. Maya Engine Startup)
        """
        disp_name = self.descriptor.display_name
        if not disp_name.lower().endswith("startup"):
            # Append "Startup" to the default descriptor
            # display_name to distinguish it from the
            # engine's display name.
            disp_name = "%s Startup" % disp_name
        return disp_name

    @property
    def engine_name(self):
        """
        Returns the toolkit engine name this launcher is based on as a ``str``.
        """
        return self.__engine_name

    @property
    def logger(self):
        """
        :class:`~logging.Logger` for this launcher. Use this whenever you want to emit or process log messages.
        """
        return LogManager.get_logger(
            "env.%s.%s.startup" % (self.__environment.name, self.__engine_name)
        )

    @property
    def shotgun(self):
        """
        :class:`shotgun_api3.Shotgun` handle associated with the currently running
        environment. This method is a convenience method that calls out
        to :meth:`~sgtk.Tank.shotgun`.
        """
        return self.sgtk.shotgun

    @property
    def minimum_supported_version(self):
        """
        The minimum software version that is supported by the launcher.
        Returned as a string, for example `2015` or `2015.3.sp3`.
        Returns ``None`` if no constraint has been set.
        """
        # returns none by default, subclassed by implementing classes
        return None

    @property
    def products(self):
        """
        A list of product names limiting executable discovery.

        Example::

            ["Houdini", "Houdini Core", "Houdini FX"]
        """
        return self._products

    @property
    def versions(self):
        """
        A list of versions limiting executable discovery.

        Example::

            ["15.5.324", "16.0.1.322"]
        """
        return self._versions

    ##########################################################################################
    # abstract methods

    def prepare_launch(self, exec_path, args, file_to_open=None):
        """
        This is an abstract method that must be implemented by a subclass. The
        engine implementation should prepare an environment to launch the specified
        executable path in.

        .. note:: By returning an executable path and args string, we allow for
                  a workflow where the engine launcher can rewrite the launch
                  sequence in arbitrary ways. For example, if a DCC has a
                  pre-check phase that requires input from a human, a different
                  executable path that launches a standalone UI which in turn
                  launches the specified path can be returned with the appropriate
                  args.

        :param str exec_path: Path to DCC executable to launch
        :param str args: Command line arguments as strings
        :param str file_to_open: (optional) Full path name of a file to open on
            launch
        :returns: :class:`LaunchInformation` instance
        """
        raise NotImplementedError

    def _format(self, template, tokens):
        """
        Limited implementation of Python 2.6-like str.format.

        :param str template: String using {<name>} tokens for substitution.
        :param dict tokens: Dictionary of <name> to substitute for <value>.

        :returns: The substituted string, when "<name>" will yield "<value>".
        """
        for key, value in tokens.items():
            template = template.replace("{%s}" % key, value)
        return template

    def _glob_and_match(self, match_template, template_key_expressions):
        r"""
        This is a helper method that can be invoked in an implementation of :meth:`scan_software`.

        The ``match_template`` argument provides a template to use both for globbing files and then pattern
        matching them using regular expressions provided by the ``tokens_expressions`` dictionary.

        The method will first substitute every token surrounded by ``{}`` from the template with a ``*``
        for globbing files. It will then replace the tokens in the template with the regular expressions
        that were provided.

        Example::

            self._glob_and_match(
                "C:\\Program Files\\Nuke{full_version}\\Nuke{major_minor_version}.exe",
                {
                    "full_version": r"[\d.v]+",
                    "major_minor_version": r"[\d.]+"
                }
            )

        The example above would look for every file matching the glob ``C:\Program Files\softwares\Nuke*\Nuke*.exe``
        and then run the regular expression ``C:\\Program Files\\Nuke([\d.v]+)\\Nuke([\d.]+).exe``
        on each match. Each match will be comprised of a path and a dictionary with they token's value.

        For example, if Nuke 10.0v1 was installed, the following would have been returned::

            [("C:\\Program Files\\Nuke10.0v1\\Nuke10.1.exe",
              {"full_version": "10.0v1", "major_minor_version"="10.0"})]

        :param str match_template: String template that will be used both for globbing and performing
            a regular expression.

        :param dict template_key_expressions: Dictionary of regular expressions that can be substituted
            in the template. The key should be the name of the token to substitute.

        :returns: A list of tuples containing the path and a dictionary with each token's value.
        """

        # Sanitize glob pattern.
        fixed_match_template = ShotgunPath.from_current_os_path(
            match_template
        ).current_os
        if fixed_match_template != match_template:
            self.logger.debug(
                "Template was sanitized from '%s' to '%s'"
                % (match_template, fixed_match_template)
            )
            match_template = fixed_match_template

        # First start by globbing files.
        glob_pattern = self._format(
            match_template, dict((key, "*") for key in template_key_expressions)
        )
        self.logger.debug("Globbing for executable matching: %s ..." % (glob_pattern,))
        matching_paths = glob.glob(glob_pattern)

        # If nothing was found, we can leave right away.
        if not matching_paths:
            self.logger.debug("No matches were found.")
            return []

        self.logger.debug(
            "Found %s matches: %s" % (len(matching_paths), matching_paths)
        )

        # Now prepare the template to be turned into a regular expression. First, double up the
        # backward slashes to escape them properly in the regular expression on Windows.
        if is_windows():
            regex_pattern = match_template.replace("\\", "\\\\")
        else:
            regex_pattern = match_template
        # Then swap the tokens into the regular template key expressions.
        regex_pattern = self._format(
            regex_pattern,
            # Put () around the provided expressions so that they become capture groups.
            dict(
                (k, "(?P<%s>%s)" % (k, v)) for k, v in template_key_expressions.items()
            ),
        )

        # accumulate the software version objects to return. this will include
        # include the head/tail anchors in the regex
        regex_pattern = "^%s$" % (regex_pattern,)

        self.logger.debug("Now matching components with regex: %s" % (regex_pattern,))

        # compile the regex
        executable_regex = re.compile(regex_pattern, re.IGNORECASE)

        # iterate over each executable found for the glob pattern and find
        # matched components via the regex
        matches = []
        for matching_path in matching_paths:

            self.logger.debug("Processing path: %s" % (matching_path,))

            match = executable_regex.match(matching_path)

            if not match:
                self.logger.debug("Path did not match regex.")
                continue

            matches.append((matching_path, match.groupdict()))

        return matches

    ##########################################################################################
    # public methods

    def get_setting(self, key, default=None):
        """
        Get a value from the item's settings::

            >>> app.get_setting('entity_types')
            ['Sequence', 'Shot', 'Asset', 'Task']

        :param key: config name
        :param default: default value to return
        :returns: Value from the environment configuration
        """
        # An old use case exists whereby the key does not exist in the
        # config schema so we need to account for that.
        schema = self.descriptor.configuration_schema.get(key, None)

        # Use engine.py method to resolve the setting value
        return resolve_setting_value(
            self.sgtk, self.engine_name, schema, self.settings, key, default
        )

    def get_standard_plugin_environment(self):
        """
        Create a standard plugin environment, suitable for
        plugins to utilize. This will compute the following
        environment variables:

        - ``SHOTGUN_SITE``: Derived from the Toolkit instance's site url
        - ``SHOTGUN_ENTITY_TYPE``: Derived from the current context
        - ``SHOTGUN_ENTITY_ID``: Derived from the current context
        - ``SHOTGUN_PIPELINE_CONFIGURATION_ID``: Derived from the current pipeline config id
        - ``SHOTGUN_BUNDLE_CACHE_FALLBACK_PATHS``: Derived from the curent pipeline configuration's list of bundle cache fallback paths.

        These environment variables are set when launching a new process to capture the state of
        Toolkit so we can launch in the same environment. It ensures subprocesses have access to the
        same bundle caches, which allows to reuse already cached bundles.

        :returns: Dictionary of environment variables.
        """
        self.logger.debug("Computing standard plugin environment variables...")
        env = {}

        # site
        env["SHOTGUN_SITE"] = self.sgtk.shotgun_url

        # pipeline config id
        # note: get_shotgun_id() returns None for unmanaged configs.
        pipeline_config_id = self.sgtk.pipeline_configuration.get_shotgun_id()
        if pipeline_config_id:
            env["SHOTGUN_PIPELINE_CONFIGURATION_ID"] = str(pipeline_config_id)
        else:
            self.logger.debug(
                "Pipeline configuration doesn't have an id. "
                "Not setting SHOTGUN_PIPELINE_CONFIGURATION_ID."
            )

        bundle_cache_fallback_paths = os.pathsep.join(
            self.sgtk.pipeline_configuration.get_bundle_cache_fallback_paths()
        )
        if bundle_cache_fallback_paths:
            env["SHOTGUN_BUNDLE_CACHE_FALLBACK_PATHS"] = bundle_cache_fallback_paths
        else:
            self.logger.debug(
                "Pipeline configuration doesn't have bundle cache fallback paths. "
                "Not setting SHOTGUN_BUNDLE_CACHE_FALLBACK_PATHS."
            )

        # get the most accurate entity, first see if there is a task, then entity then project
        entity_dict = self.context.task or self.context.entity or self.context.project

        if entity_dict:
            env["SHOTGUN_ENTITY_TYPE"] = entity_dict["type"]
            env["SHOTGUN_ENTITY_ID"] = str(entity_dict["id"])
        else:
            self.logger.debug(
                "No context found. Not setting SHOTGUN_ENTITY_TYPE and SHOTGUN_ENTITY_ID."
            )

        self.logger.debug("Returning Plugin Environment: \n%s" % pprint.pformat(env))
        return env

    def scan_software(self):
        """
        Performs a search for supported software installations.

        Typical implementations will use functionality such as :meth:`_glob_and_match`
        or :meth:`glob.glob` to locate all versions and variations of executables on disk
        and then create :class:`SoftwareVersion` objects for each executable and check against the launcher's
        lists of supported version and product variations via the :meth:`_is_supported` method.

        :returns: List of :class:`SoftwareVersion` supported by this launcher.
        :rtype: list
        """
        raise NotImplementedError

    ##########################################################################################
    # protected methods

    def _is_supported(self, sw_version):
        """
        Inspects the supplied :class:`SoftwareVersion` object to see if it
        aligns with this launcher's known product and version limitations. Will
        check the :meth:`~minimum_supported_version` as well as the list of
        product and version filters.

        :param sw_version: :class:`SoftwareVersion` object to test against the
            launcher's product and version limitations.

        :returns: A tuple of the form: ``(bool, str)`` where the first item
            is a boolean indicating whether the supplied :class:`SoftwareVersion` is
            supported or not. The second argument is ``""`` if supported, but if
            not supported will be a string representing the reason the support
            check failed.

        This helper method can be used by subclasses in the :meth:`scan_software`
        method.

        The method can be overridden by subclasses that require more
        sophisticated :class:`SoftwareVersion` support checks.
        """

        # check version support
        if not self.__is_version_supported(sw_version.version):
            return (
                False,
                "Executable '%s' didn't meet the version requirements"
                "(%s not in %s or is older than %s)"
                % (
                    sw_version.path,
                    sw_version.version,
                    self.versions,
                    self.minimum_supported_version,
                ),
            )

        # check products list
        if not self.__is_product_supported(sw_version.product):
            return (
                False,
                "Executable '%s' didn't meet the product requirements"
                "(%s not in %s)" % (sw_version.path, sw_version.product, self.products),
            )

        # passed all checks. must be supported!
        return (True, "")

    def __is_version_supported(self, version):
        """
        Returns ``True`` if the supplied version string is supported by the
        launcher, ``False`` otherwise.

        The method first checks against the minimum supported version. If the
        supplied version is greater it then checks to ensure that it is in the
        launcher's ``versions`` constraint. If there are no constraints on the
        versions, the method will return ``True``.

        :param str version: A string representing the version to check against.

        :return: Boolean indicating if the supplied version string is supported.
        """

        # first, compare against the minimum version
        min_version = self.minimum_supported_version
        if min_version and is_version_older(version, min_version):
            # the version is older than the minimum supported version
            return False

        if not self.versions:
            # No version restriction. All versions supported
            return True

        # check versions list
        return version in self.versions

    def __is_product_supported(self, product):
        """
        Returns ``True`` if the supplied product name string is supported by the
        launcher, ``False`` otherwise.

        The method checks to ensure that the product name is in the launcher's
        ``products`` constraint. If there are no constraints on the products,
        the method will return ``True``.

        .. note::
            Product name comparison is case-insensitive.

        :param str product: A string representing the product name to check
            against.

        :return: Boolean indicating if the supplied product name string is
            supported.
        """

        if not self.products:
            # No product restriction. All product variations are supported
            return True

        # check products list
        return product.lower() in self._lower_case_products


class SoftwareVersion(object):
    """
    Container class that stores properties of a DCC that
    are useful for Toolkit Engine Startup functionality.
    """

    def __init__(self, version, product, path, icon=None, args=None):
        """
        :param str version: Explicit version of the DCC represented
                            (e.g. 2017)
        :param str product: Explicit product name of the DCC represented
                            (e.g. "Houdini Apprentice")
        :param str path: Full path to the DCC executable.
        :param str icon: (optional) Full path to a 256x256 (or smaller)
                         ``png`` file to use for graphical displays of
                         this :class:`SoftwareVersion`.
        :param list args: (optional) List of command line arguments
                               that need to be passed down to the DCC.
        """
        self._version = version
        self._product = product
        self._path = path
        self._icon_path = icon
        self._args = args or []

    def __repr__(self):
        """
        Returns unique str representation of the software version
        """
        return "<SoftwareVersion 0x%08x: %s %s, path: %s args: %s>" % (
            id(self),
            self.product,
            self.version,
            self.path,
            self.args,
        )

    @property
    def version(self):
        """
        An explicit version of the DCC represented by this :class`SoftwareVersion`.

        :returns: String version
        """
        return self._version

    @property
    def product(self):
        """
        An explicit product name for the DCC represented by this
        :class`SoftwareVersion`. Example: "Houdini FX"

        :return: String product name
        """

        return self._product

    @property
    def display_name(self):
        """
        Name to use for this :class`SoftwareVersion` in graphical displays.

        :returns: String display name, a combination of the product and version.
        """
        return "%s %s" % (self.product, self.version)

    @property
    def path(self):
        """
        Specified path to the DCC executable. May be relative.

        :returns: String path
        """
        return self._path

    @property
    def icon(self):
        """
        Path to the icon to use for graphical displays of this
        :class:`SoftwareVersion`. Expected to be a 256x256 (or smaller)
        `png` file.

        :returns: String path
        """
        return self._icon_path

    @property
    def args(self):
        """
        Command line arguments required to launch the DCC.

        :returns: List of string arguments.
        """
        return self._args


class LaunchInformation(object):
    """
    Stores blueprints for how to launch a specific DCC which includes
    required environment variables, the executable path, and command
    line arguments to pass when launching the DCC. For example, given
    a LaunchInformation instance ``launch_info``, open a DCC using
    ``subprocess``::

        >>> launch_cmd = "%s %s" % (launch_info.path, launch_info.args)
        >>> subprocess.Popen([launch_cmd], env=launch_info.environment)

    A LaunchInformation instance is generally obtained from an engine's
    subclass implementation of :meth:`SoftwareLauncher.prepare_launch``
    """

    def __init__(self, path=None, args=None, environ=None):
        """
        :param str path: Resolved path to DCC
        :param str args: Args to pass on the command line
                         when launching the DCC
        :param dict environ: Environment variables that
                             must be set to successfully
                             launch the DCC.
        """
        # Initialize members
        self._path = path
        self._args = args or ""
        self._environment = environ or {}

    @property
    def path(self):
        """
        The DCC path to launch

        :returns: String path
        """
        return self._path

    @property
    def args(self):
        """
        Arguments to pass to the DCC on launch

        :returns: String args
        """
        return self._args

    @property
    def environment(self):
        """
        Dictionary of environment variables to set before
        launching DCC.

        :returns: Dict {env_var: value}
        """
        return self._environment
