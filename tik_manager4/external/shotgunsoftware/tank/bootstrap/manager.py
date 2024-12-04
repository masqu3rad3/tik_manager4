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
import inspect

from . import constants
from .errors import TankBootstrapError
from .configuration import Configuration
from .resolver import ConfigurationResolver
from ..authentication import ShotgunAuthenticator
from ..pipelineconfig import PipelineConfiguration
from .. import LogManager
from ..errors import TankError
from ..util import ShotgunPath

log = LogManager.get_logger(__name__)


class ToolkitManager(object):
    """
    This class allows for flexible and non-obtrusive management of toolkit configurations
    and installations.
    """

    # Constants used to make the manager bootstrapping:
    # - download and cache the config dependencies needed to run the engine being started in a specific environment.
    # - download and cache all the config dependencies needed to run the engine in any environment.
    (CACHE_SPARSE, CACHE_FULL) = range(2)

    # Constants used to indicate that the manager is:
    # - bootstrapping the toolkit (with method bootstrap_toolkit),
    # - starting up the engine (with method _start_engine).
    (TOOLKIT_BOOTSTRAP_PHASE, ENGINE_STARTUP_PHASE) = range(2)

    # List of constants representing the status of the progress bar when these event occurs during bootstrap.
    _RESOLVING_PROJECT_RATE = 0.0
    _RESOLVING_CONFIG_RATE = 0.05
    _UPDATING_CONFIGURATION_RATE = 0.1
    _STARTING_TOOLKIT_RATE = 0.15
    _START_DOWNLOADING_APPS_RATE = 0.20
    _END_DOWNLOADING_APPS_RATE = 0.90
    _POST_INSTALL_APPS_RATE = _END_DOWNLOADING_APPS_RATE
    _RESOLVING_CONTEXT_RATE = 0.95
    _LAUNCHING_ENGINE_RATE = 0.97
    _BOOTSTRAP_COMPLETED = 1

    def __init__(self, sg_user=None):
        """
        :param sg_user: Authenticated Shotgun User object. If you pass in None,
                        the manager will provide a standard authentication for you
                        via the shotgun authentication module and prompting the user
                        if necessary. If you have special requirements around
                        authentication, simply construct an explicit user object
                        and pass it in.
        :type sg_user: :class:`~sgtk.authentication.ShotgunUser`
        """
        if sg_user is None:
            # request a user from the auth module
            sg_auth = ShotgunAuthenticator()
            self._sg_user = sg_auth.get_user()
        else:
            self._sg_user = sg_user

        self._sg_connection = self._sg_user.create_sg_connection()

        # defaults
        self._pre_engine_start_callback = None
        self._progress_cb = None

        # These are serializable parameters from the class.
        self._user_bundle_cache_fallback_paths = []
        self._caching_policy = self.CACHE_SPARSE
        self._pipeline_configuration_identifier = None  # name or id
        self._base_config_descriptor = None
        self._do_shotgun_config_lookup = True
        self._plugin_id = None
        self._allow_config_overrides = True

        # look for the standard env var SHOTGUN_PIPELINE_CONFIGURATION_ID
        # and in case this is set, use it as a default
        if constants.PIPELINE_CONFIG_ID_ENV_VAR in os.environ:
            pipeline_config_str = os.environ[constants.PIPELINE_CONFIG_ID_ENV_VAR]
            log.debug(
                "Detected %s environment variable set to '%s'"
                % (constants.PIPELINE_CONFIG_ID_ENV_VAR, pipeline_config_str)
            )
            # try to convert it to an integer
            try:
                pipeline_config_id = int(pipeline_config_str)
            except ValueError:
                log.error(
                    "Environment variable %s value '%s' is not "
                    "an integer number and will be ignored."
                    % (constants.PIPELINE_CONFIG_ID_ENV_VAR, pipeline_config_str)
                )
            else:
                log.debug("Setting pipeline configuration to %s" % pipeline_config_id)
                self.pipeline_configuration = pipeline_config_id

        log.debug("%s instantiated" % self)

    def __repr__(self):
        if self._pipeline_configuration_identifier is None:
            identifier_type = "is"
        elif isinstance(self._pipeline_configuration_identifier, int):
            identifier_type = "id"
        else:
            identifier_type = "name"

        repr = "<TkManager "
        repr += " User %s\n" % self._sg_user
        repr += (
            " Bundle cache fallback paths %s\n"
            % self._get_bundle_cache_fallback_paths()
        )
        repr += " Caching policy %s\n" % self._caching_policy
        repr += " Plugin id %s\n" % self._plugin_id
        repr += " Config %s %s\n" % (
            identifier_type,
            self._pipeline_configuration_identifier,
        )
        repr += " Base %s >" % self._base_config_descriptor
        return repr

    def extract_settings(self):
        """
        Serializes the state of the class.

        Serializes settings that impact resolution of a pipeline configuration into an
        object and returns it to the user.

        This can be useful when a process is used to enumerate pipeline configurations and another
        process will be bootstrapping an engine. Calling this method ensures the manager is
        configured the same across processes.

        Those settings can be restored with :meth:`ToolkitManager.restore_settings`.

        .. note:: Note that the extracted settings should be treated as opaque data and not something
             that should be manipulated. Their content can be changed at any time.

        :returns: User defined values.
        :rtype: object
        """
        return {
            "bundle_cache_fallback_paths": self.bundle_cache_fallback_paths,
            "caching_policy": self.caching_policy,
            "pipeline_configuration": self.pipeline_configuration,
            "base_configuration": self.base_configuration,
            "do_shotgun_config_lookup": self.do_shotgun_config_lookup,
            "plugin_id": self.plugin_id,
            "allow_config_overrides": self.allow_config_overrides,
        }

    def restore_settings(self, data):
        """
        Restores serialized state.

        This will restores the state user defined with :meth:`ToolkitManager.extract_settings`.

        .. note:: Always use :meth:`ToolkitManager.extract_settings` to extract settings when you
            plan on calling this method. The content of the settings should be treated as opaque
            data.

        :param object data: Settings obtained from :meth:`ToolkitManager.extract_settings`
        """
        self.bundle_cache_fallback_paths = data["bundle_cache_fallback_paths"]
        self.caching_policy = data["caching_policy"]
        self.pipeline_configuration = data["pipeline_configuration"]
        self.base_configuration = data["base_configuration"]
        self.do_shotgun_config_lookup = data["do_shotgun_config_lookup"]
        self.plugin_id = data["plugin_id"]
        self.allow_config_overrides = data["allow_config_overrides"]

    def _get_bundle_cache_fallback_paths(self):
        """
        Retuns a list containing both the user specified bundle caches and the one specified
        by the SHOTGUN_BUNDLE_CACHE_FALLBACK_PATHS.

        .. note::
            While the method will preserve the order of the fallback locations by first
            returning user defined locations and then ones found with the environment variable,
            the method will remove duplicate locations.

        For example::

            >>> os.environ["SHOTGUN_BUNDLE_CACHE_FALLBACK_PATHS"] = "/a/b/c:/d/e/f"
            >>> mgr = ToolkitManager()
            >>> mgr.bundle_cache_fallback_paths = ["/g/h/i:/d/e/f"]
            >>> repr(mgr)
            <TkManager
             User boismej
             Bundle cache fallback paths ["/g/h/i", "/d/e/f", "/a/b/c"]
             ...
            >

        :returns: List of bundle cache paths.
        """
        if constants.BUNDLE_CACHE_FALLBACK_PATHS_ENV_VAR in os.environ:
            fallback_str = os.environ[constants.BUNDLE_CACHE_FALLBACK_PATHS_ENV_VAR]
            log.debug(
                "Detected %s environment variable set to '%s'"
                % (constants.BUNDLE_CACHE_FALLBACK_PATHS_ENV_VAR, fallback_str)
            )
            toolkit_bundle_cache_fallback_paths = fallback_str.split(os.pathsep)

            # Python' sets do not preserve insertion order and Python 2.5 doesn't support
            # OrderedDicts, which would have been perfect for this, so we will...

            # First build the complete list of paths with possible duplicates.
            concatenated_lists = (
                self._user_bundle_cache_fallback_paths
                + toolkit_bundle_cache_fallback_paths
            )

            # Then build a set of unique paths.
            unique_items = set(concatenated_lists)

            # Finally iterate on complete list of items.
            return [x for x in concatenated_lists if x in unique_items]
        else:
            return self._user_bundle_cache_fallback_paths

    def _get_pipeline_configuration(self):
        """
        The pipeline configuration that should be operated on.

        By default, this value is set to ``None``, indicating to the Manager
        that it should attempt to automatically find the most suitable pipeline
        configuration entry in Shotgun given the project and plugin id.
        In this case, it will look at all pipeline configurations stored in Shotgun
        associated with the project who are associated with the current
        user. If no user-tagged pipeline configuration exists, it will look for
        the primary configuration, and in case this is not found, it will fall back on the
        :meth:`base_configuration`. If you don't want this check to be carried out in
        Shotgun, please set :meth:`do_shotgun_config_lookup` to False.

        Alternatively, you can set this to a specific pipeline configuration. In that
        case, the Manager will look for a pipeline configuration that matches that name or id
        and the associated project and plugin id. If such a config cannot be found in
        Shotgun, it falls back on the :meth:`base_configuration`.
        """
        return self._pipeline_configuration_identifier

    def _set_allow_config_overrides(self, state):
        self._allow_config_overrides = bool(state)

    def _get_allow_config_overrides(self):
        """
        Whether pipeline configuration resolution can be overridden via the
        environment. Defaults to True on manager instantiation.
        """
        return self._allow_config_overrides

    allow_config_overrides = property(
        _get_allow_config_overrides, _set_allow_config_overrides
    )

    def _set_pipeline_configuration(self, identifier):
        self._pipeline_configuration_identifier = identifier

    def _get_pre_engine_start_callback(self):
        """
        Callback invoked after the :class:`~sgtk.Sgtk` instance has been
        created.

        This function should have the following signature::

            def pre_engine_start_callback(ctx):
                '''
                Called before the engine is started.

                :param :class:"~sgtk.Context" ctx: Context into
                    which the engine will be launched. This can also be used
                    to access the Toolkit instance.
                '''
        """
        return self._pre_engine_start_callback

    def _set_pre_engine_start_callback(self, callback):
        self._pre_engine_start_callback = callback

    pre_engine_start_callback = property(
        _get_pre_engine_start_callback, _set_pre_engine_start_callback
    )

    pipeline_configuration = property(
        _get_pipeline_configuration, _set_pipeline_configuration
    )

    def _get_do_shotgun_config_lookup(self):
        """
        Controls the Shotgun override behaviour.

        Boolean property to indicate if the bootstrap process should connect to
        Shotgun and attempt to resolve a config. Defaults to ``True``.

        If ``True``, the bootstrap process will connect to Shotgun as part
        of the startup, look for a pipeline configuration and attempt
        to resolve a toolkit environment to bootstrap into via the
        Pipeline configuration data. Failing this, it will fall back on
        the :meth:`base_configuration`.

        If ``False``, no Shotgun lookup will happen. Instead, whatever config
        is defined via :meth:`base_configuration` will always be used.
        """
        return self._do_shotgun_config_lookup

    def _set_do_shotgun_config_lookup(self, status):
        # setter for do_shotgun_config_lookup
        self._do_shotgun_config_lookup = status

    do_shotgun_config_lookup = property(
        _get_do_shotgun_config_lookup, _set_do_shotgun_config_lookup
    )

    def _get_plugin_id(self):
        """
        The associated plugin id.

        The Plugin Id is a string that defines the scope of the bootstrap operation.

        When you are writing plugins or tools that is intended to run side by
        side with other plugins in your target environment, the entry
        point will be used to define a scope and sandbox in which your
        plugin will execute.

        When constructing a plugin id for an integration the following
        should be considered:

        - Plugin Ids should uniquely identify the plugin.
        - The name should be short and descriptive.

        The basic toolkit integration uses a ``basic`` prefix, e.g.
        ``basic.maya``, ``basic.nuke``. We recommend using the
        ``basic`` prefix for standard workflows.

        For more information, see :ref:`plugins_and_plugin_ids`.
        """
        return self._plugin_id

    def _set_plugin_id(self, plugin_id):
        # setter for plugin_id
        self._plugin_id = plugin_id

    plugin_id = property(_get_plugin_id, _set_plugin_id)

    # backwards compatibility
    entry_point = plugin_id

    def _get_base_configuration(self):
        """
        The fallback configuration to use.

        The descriptor (string or dict) for the
        configuration that should be used as a base fallback
        to be used if an override configuration isn't set in Shotgun.

        For
        """
        return self._base_config_descriptor

    def _set_base_configuration(self, descriptor):
        # setter for base_configuration
        self._base_config_descriptor = descriptor

    base_configuration = property(_get_base_configuration, _set_base_configuration)

    def _get_user_bundle_cache_fallback_paths(self):
        """
        A list of fallback paths where toolkit will look for cached bundles.

        This is useful if you want to distribute a pre-baked
        package, containing all the app version that a user needs.
        This avoids downloading anything from the app store or other
        sources.

        Any bundles missing from locations specified in the
        fallback paths will be downloaded and cached into
        the global bundle cache.
        """
        return self._user_bundle_cache_fallback_paths

    def _set_user_bundle_cache_fallback_paths(self, paths):
        # setter for bundle_cache_fallback_paths
        self._user_bundle_cache_fallback_paths = paths

    bundle_cache_fallback_paths = property(
        _get_user_bundle_cache_fallback_paths, _set_user_bundle_cache_fallback_paths
    )

    def _get_caching_policy(self):
        """
        Specifies the config caching policy to use when bootstrapping.

        ``ToolkitManager.CACHE_SPARSE`` will make the manager download and cache
        the sole config dependencies needed to run the engine being started.
        This is the default caching policy.

        ``ToolkitManager.CACHE_FULL`` will make the manager download and cache
        all the config dependencies.
        """
        return self._caching_policy

    def _set_caching_policy(self, caching_policy):
        # Setter for property 'caching_policy'.
        if caching_policy not in (self.CACHE_SPARSE, self.CACHE_FULL):
            raise TankBootstrapError(
                "Invalid config caching policy %s. "
                "Set to 'ToolkitManager.CACHE_SPARSE' or 'ToolkitManager.CACHE_FULL'."
                % caching_policy
            )
        self._caching_policy = caching_policy

    caching_policy = property(_get_caching_policy, _set_caching_policy)

    def _get_progress_callback(self):
        """
        Callback that gets called whenever progress should be reported.

        This function should have the following signature::

            def progress_callback(progress_value, message):
                '''
                Called whenever toolkit reports progress.

                :param progress_value: The current progress value as float number.
                                       values will be reported in incremental order
                                       and always in the range 0.0 to 1.0
                :param message:        Progress message string
                '''

        .. note:: When registering a progress callback, ensure that it is ALWAYS
            thread safe. There is no guarantee that it will be called from the
            main thread.
        """
        return self._progress_cb or self._default_progress_callback

    def _set_progress_callback(self, value):
        # Setter for progress_callback.
        self._progress_cb = value

    progress_callback = property(_get_progress_callback, _set_progress_callback)

    def set_progress_callback(self, progress_callback):
        """
        Sets the function to call whenever progress of the bootstrap should be reported back.

        .. note:: This is a deprecated method. Property ``progress_callback`` should now be used.

        :param progress_callback: Callback function that reports back on the toolkit
            and engine bootstrap progress. This callback should ALWAYS be thread safe,
            as there is no guarantee that it will be called in the main thread.
        """

        self.progress_callback = progress_callback

    def bootstrap_engine(self, engine_name, entity=None):
        """
        Create an :class:`~sgtk.Sgtk` instance for the given engine and entity,
        then launch into the given engine.

        The whole engine bootstrap logic will be executed synchronously in the main application thread.

        If entity is None, the method will bootstrap into the site
        config. This method will attempt to resolve the config according
        to business logic set in the associated resolver class and based
        on this launch a configuration. This may involve downloading new
        apps from the toolkit app store and installing files on disk.

        Please note that the API version of the tk instance that hosts
        the engine may not be the same as the API version that was
        executed during the bootstrap.

        :param engine_name: Name of engine to launch (e.g. ``tk-nuke``).
        :param entity: Shotgun entity to launch engine for.
        :type entity: Dictionary with keys ``type`` and ``id``, or ``None`` for the site.

        :returns: :class:`~sgtk.platform.Engine` instance.
        """
        self._log_startup_message(engine_name, entity)

        tk = self._bootstrap_sgtk(engine_name, entity)

        engine = self._start_engine(tk, engine_name, entity)

        self._report_progress(
            self.progress_callback, self._BOOTSTRAP_COMPLETED, "Engine launched."
        )

        return engine

    def bootstrap_engine_async(
        self,
        engine_name,
        entity=None,
        completed_callback=None,
        failed_callback=None,
        parent=None,
    ):
        """
        Asynchronous version of :meth:`bootstrap_engine`.

        Create an :class:`~sgtk.Sgtk` instance for the given engine and entity,
        then launch into the given engine.

        This method launches the bootstrap process and returns immediately.
        The :class:`~sgtk.Sgtk` instance will be bootstrapped asynchronously in a background thread,
        followed by launching the engine synchronously in the main application thread.
        This will allow the main application to continue its execution and
        remain responsive when bootstrapping the toolkit involves downloading files and
        installing apps from the toolkit app store.

        If entity is None, the method will bootstrap into the site
        config. This method will attempt to resolve the config according
        to business logic set in the associated resolver class and based
        on this launch a configuration. This may involve downloading new
        apps from the toolkit app store and installing files on disk.

        Two callback functions can be provided.

        A callback function that handles cleanup after successful completion of the bootstrap
        with the following signature::

            def completed_callback(engine):
                '''
                Called by the asynchronous bootstrap upon completion.

                :param engine: Engine instance representing the engine
                               that was launched.
                '''

        A callback function that handles cleanup after failed completion of the bootstrap
        with the following signature::

            def failed_callback(phase, exception):
                '''
                Called by the asynchronous bootstrap if an exception is raised.

                :param phase: Indicates in which phase of the bootstrap the exception
                              was raised. An integer constant which is either
                              ToolkitManager.TOOLKIT_BOOTSTRAP_PHASE or
                              ToolkitManager.ENGINE_STARTUP_PHASE. The former if the
                              failure happened while the system was still bootstrapping
                              and the latter if the system had switched over into the
                              Toolkit startup phase. At this point, the running core API
                              instance may have been swapped over to another version than
                              the one that was originally loaded and may need to be reset
                              in an implementation of this callback.

                :param exception: The python exception that was raised.
                '''

        :param engine_name: Name of engine to launch (e.g. ``tk-nuke``).
        :param entity: Shotgun entity to launch engine for.
        :type entity: Dictionary with keys ``type`` and ``id``, or ``None`` for the site.
        :param completed_callback: Callback function that handles cleanup after successful completion of the bootstrap.
        :param failed_callback: Callback function that handles cleanup after failed completion of the bootstrap.
        :param parent: The parent object used for the async bootstrapper. This will be necessary
            in some environments, as it will prevent the thread used to bootstrap from being
            garbage collected before it completes its work. An example input for this argument would
            be to provide a reference to the main window of the parent application being integrated
            with (ie: Maya, Nuke, etc), which is guaranteed to remain in memory for the duration of
            bootstrap process.
        """
        self._log_startup_message(engine_name, entity)

        log.debug("Will attempt to start up asynchronously.")

        if completed_callback is None:
            completed_callback = self._default_completed_callback

        if failed_callback is None:
            failed_callback = self._default_failed_callback

        try:
            from .async_bootstrap import AsyncBootstrapWrapper
        except ImportError:
            AsyncBootstrapWrapper = None
            log.warning(
                "Cannot bootstrap asynchronously in a background thread;"
                " falling back on synchronous startup."
            )

        if AsyncBootstrapWrapper:

            # Bootstrap an Sgtk instance asynchronously in a background thread,
            # followed by launching the engine synchronously in the main application thread.

            self._bootstrapper = AsyncBootstrapWrapper(
                self, engine_name, entity, completed_callback, failed_callback, parent
            )
            self._bootstrapper.bootstrap()

        else:

            # Since Qt is not available, fall back on synchronous bootstrapping.
            # Execute the whole engine bootstrap logic synchronously in the main application thread,
            # while still calling the provided callbacks in order for the caller to work as expected.

            try:

                tk = self._bootstrap_sgtk(engine_name, entity)

            except Exception as exception:

                # Handle cleanup after failed completion of the toolkit bootstrap.
                failed_callback(self.TOOLKIT_BOOTSTRAP_PHASE, exception)

                return

            try:

                engine = self._start_engine(tk, engine_name, entity)

            except Exception as exception:

                # Handle cleanup after failed completion of the engine startup.
                failed_callback(self.ENGINE_STARTUP_PHASE, exception)

                return

            # Handle cleanup after successful completion of the engine bootstrap.
            completed_callback(engine)

    def prepare_engine(self, engine_name, entity):
        """
        Updates and caches a configuration on disk for a given project. The resolution of the pipeline
        configuration will follow the same rules as the method :meth:`ToolkitManager.bootstrap_engine`,
        but it simply caches all the bundles for later use instead of bootstrapping directly into it.

        :param str engine_name: Name of the engine instance to cache if using sparse caching. If ``None``,
            all engine instances will be cached.

        :param entity: An entity link. If the entity is not a project, the project for that entity will be resolved.
        :type project: Dictionary with keys ``type`` and ``id``, or ``None`` for the site

        :returns: Path to the fully realized pipeline configuration on disk and to the descriptor that
            spawned it.

        :rtype: (str, :class:`sgtk.descriptor.ConfigDescriptor`)
        """
        config = self._get_updated_configuration(entity, self.progress_callback)

        path = config.path.current_os

        try:
            pc = PipelineConfiguration(path)
        except TankError as e:
            raise TankBootstrapError(
                "Unexpected error while caching configuration: %s" % str(e)
            )

        self._cache_bundles(config, pc, engine_name, self.progress_callback)
        self._report_progress(
            self.progress_callback, self._BOOTSTRAP_COMPLETED, "Preparations complete."
        )

        return path, config.descriptor

    def _cache_bundles(self, config, pc, engine_name, progress_callback):
        """
        Caches the bundles required by the configuration.

        :param config: The Configuration we're bootstrapping into.
        :param pc: The PipelineConfiguration instantiated from the configuration.
        :param engine_name: Name of the engine we're bootstrapping into.
        :param
        """

        def report_bundle_progress(message, idx, nb_descriptors):
            # Scale the progress step 0.8 between this value 0.15 and the next one 0.95
            # to compute a value progressing while looping over the indexes.
            step_size = (
                float(
                    self._END_DOWNLOADING_APPS_RATE - self._START_DOWNLOADING_APPS_RATE
                )
                / nb_descriptors
            )
            progress_value = self._START_DOWNLOADING_APPS_RATE + (idx * step_size)

            self._report_progress(progress_callback, progress_value, message)

        config.cache_bundles(
            pc,
            # If we're going to do a sparse cache, only cache for the engine
            # we're bootstrapping into.
            engine_name if self._caching_policy == self.CACHE_SPARSE else None,
            report_bundle_progress,
        )

    def get_pipeline_configurations(self, project):
        """
        Retrieves the pipeline configurations available for a given project.

        In order for a pipeline configuration to be considered as available, the following
        conditions must be met:

           - There can only be one primary
           - If there is one site level and one project level primary, the site level
             primary is not available.
           - If there are multiple site level or multiple project level primaries,
             only the one with the lowest id is available, unless one or more of them is a Toolkit
             Centralized Primary, in which case the Toolkit Centralized Primary with the lowest id will
             be returned.
           - A :class:`~sgtk.descriptor.Descriptor` object must be able to be created from the
             pipeline configuration.
           - All sandboxes are available.

        In practice, this means that if there are 3 primaries, two of them using plugin ids and
        one of them not using them, the one not using a plugin id will always be used.

        This filtering also takes into account the current user and optional pipeline
        configuration name or id. If the :meth:`pipeline_configuration` property has been
        set to a string, it will look for pipeline configurations with that specific name.
        If it has been set to ``None``, any pipeline that can be applied for the current
        user and project will be retrieved. Note that this method does not support
        :meth:`pipeline_configuration` being an integer.

        **Return value**

        The data structure returned is a dictionary with several keys to
        describe the configuration, for example::

            {'descriptor': <CachedConfigDescriptor <IODescriptorAppStore sgtk:descriptor:app_store?name=tk-config-basic&version=v1.1.6>>,
             'descriptor_source_uri': 'sgtk:descriptor:app_store?name=tk-config-basic',
             'id': 500,
             'name': 'Primary',
             'project': {'id': 123, 'name': 'Test Project', 'type': 'Project'},
             'type': 'PipelineConfiguration'}

        The returned dictionary mimics the result of a Shotgun API query, including
        standard fields for ``type``, ``id``, ``name`` and ``project``. In addition,
        the resolved descriptor object is returned in a ``descriptor`` key.

        For pipeline configurations which are defined in Shotgun via their **descriptor** field,
        this field is returned in a ``descriptor_source_uri`` key. For pipeline configurations
        defined via an uploaded attachment or explicit path fields, the ``descriptor_source_uri``
        key will return ``None``.

        .. note:: Note as per the example above how the ``descriptor_source_uri``
                  value can be different than the uri of the resolved descriptor;
                  this happens in the case when a descriptor uri is omitting
                  the version number and tracking against the latest version
                  number available.
                  In that case, the ``descriptor`` key will contain the
                  fully resolved descriptor object, representing the
                  latest descriptor version as of right now, where as the
                  ``descriptor_source_uri`` key contains the versionless descriptor
                  uri string as it is defined in Shotgun.

        :param project: Project entity link to enumerate pipeline configurations for.
            If ``None``, this will enumerate the pipeline configurations
            for the site configuration.
        :type project: Dictionary with keys ``type`` and ``id``.

        :returns: List of pipeline configurations.
        :rtype: List of dictionaries with syntax described above.
            The pipeline configurations will always be sorted such as the primary pipeline configuration,
            if available, will be first. Then the remaining pipeline configurations will be sorted by
            ``name`` field (case insensitive), then the ``project`` field and finally then ``id`` field.
        """
        if isinstance(self.pipeline_configuration, int):
            raise TankBootstrapError(
                "Can't enumerate pipeline configurations matching a specific id."
            )

        resolver = ConfigurationResolver(
            self.plugin_id, project["id"] if project else None
        )

        # Only return id, type and code fields.
        pcs = []
        for pc in resolver.find_matching_pipeline_configurations(
            pipeline_config_name=None,
            current_login=self._sg_user.login,
            sg_connection=self._sg_connection,
        ):
            pipeline_config_data = {
                "id": pc["id"],
                "type": pc["type"],
                "name": pc["code"],
                "project": pc["project"],
                "descriptor": pc["config_descriptor"],
                "descriptor_source_uri": None,
            }

            # if the config is descriptor based, resolve the uri
            # note: for a descriptor such as
            # sgtk:descriptor:app_store?name=tk-config-basic,
            # this is not the same as
            # pipeline_config_data["descriptor"].get_uri(), which
            # will return the fully resolved descriptor URI.
            path = ShotgunPath.from_shotgun_dict(pc)
            if path.current_os is None and pc["plugin_ids"]:
                # this is a descriptor based config:
                pipeline_config_data["descriptor_source_uri"] = pc["descriptor"]

            pcs.append(pipeline_config_data)

        return pcs

    def get_entity_from_environment(self):
        """
        Standardized environment variable retrieval.

        Helper method that looks for the standard environment variables
        ``SHOTGUN_SITE``, ``SHOTGUN_ENTITY_TYPE`` and
        ``SHOTGUN_ENTITY_ID`` and attempts to extract and validate them.
        This is typically used in conjunction with :meth:`bootstrap_engine`.
        The standard environment variables read by this method can be
        generated by :meth:`~sgtk.platform.SoftwareLauncher.get_standard_plugin_environment`.

        :returns: Standard Shotgun entity dictionary with type and id or
            None if not defined.
        """
        shotgun_site = os.environ.get("SHOTGUN_SITE")
        entity_type = os.environ.get("SHOTGUN_ENTITY_TYPE")
        entity_id = os.environ.get("SHOTGUN_ENTITY_ID")

        # Check that the shotgun site (if set) matches the site we are currently
        # logged in to. If not, issue a warning and ignore the entity type/id variables
        if shotgun_site and self._sg_user.host != shotgun_site:
            log.warning(
                "You are currently logged in to site %s but your launch environment "
                "is set to start up %s %s on site %s. The PTR integration "
                "currently doesn't support switching between sites and the contents of "
                "SHOTGUN_ENTITY_TYPE and SHOTGUN_ENTITY_ID will therefore be ignored."
                % (self._sg_user.host, entity_type, entity_id, shotgun_site)
            )
            entity_type = None
            entity_id = None

        if (entity_type and not entity_id) or (not entity_type and entity_id):
            log.error(
                "Both environment variables SHOTGUN_ENTITY_TYPE and SHOTGUN_ENTITY_ID must be provided "
                "to set a context entity."
            )

        if entity_id:
            # The entity id must be an integer number.
            try:
                entity_id = int(entity_id)
            except ValueError:
                log.error(
                    "The environment variable SHOTGUN_ENTITY_ID value '%s' "
                    "is not an integer and will be ignored." % entity_id
                )
                entity_type = None
                entity_id = None

        if entity_type and entity_id:
            # Set the entity to launch the engine for.
            entity = {"type": entity_type, "id": entity_id}
        else:
            # Set the entity to launch the engine in site context.
            entity = None

        return entity

    def resolve_descriptor(self, project):
        """
        Resolves a pipeline configuration and returns its associated descriptor object.

        :param dict project: The project entity, or None.
        """
        if project is None:
            return self._get_configuration(None, self.progress_callback).descriptor
        else:
            return self._get_configuration(project, self.progress_callback).descriptor

    def _log_startup_message(self, engine_name, entity):
        """
        Helper method that logs information about the current session
        :param engine_name: Name of the engine used to bootstrap
        :param entity: Shotgun entity to bootstrap into.
        """
        log.debug("-----------------------------------------------------------------")
        log.debug("Begin bootstrapping Toolkit.")
        log.debug("")
        log.debug("Plugin Id: %s" % self._plugin_id)

        if self._do_shotgun_config_lookup:
            log.debug("Will connect to PTR to look for overrides.")
            log.debug(
                "If no overrides found, this config will be used: %s"
                % self._base_config_descriptor
            )

            if self._pipeline_configuration_identifier not in [0, None, ""]:
                log.debug("Potential config overrides will be pulled ")
                log.debug(
                    "from pipeline config '%s'"
                    % self._pipeline_configuration_identifier
                )
            else:
                log.debug(
                    "The system will automatically determine the pipeline configuration"
                )
                log.debug("based on the current project id and user.")

        else:
            log.debug("Will not connect to PTR to resolve config overrides.")
            log.debug(
                "The following config will be used: %s" % self._base_config_descriptor
            )

        log.debug("")
        log.debug("Target entity for runtime context: %s" % entity)
        log.debug("Bootstrapping engine %s." % engine_name)
        log.debug("-----------------------------------------------------------------")

    def _get_configuration(self, entity, progress_callback):
        """
        Resolves the configuration to use without creating it on disk.

        :param entity: Shotgun entity used to resolve a project context.
        :type entity: Dictionary with keys ``type`` and ``id``, or ``None`` for the site.
        :param progress_callback: Callback function that reports back on the toolkit bootstrap progress.
                                  Set to ``None`` to use the default callback function.

        :returns: A :class:`sgtk.bootstrap.configuration.Configuration` instance.
        """
        self._report_progress(
            progress_callback, self._RESOLVING_PROJECT_RATE, "Resolving project..."
        )
        if entity is None:
            project_id = None

        elif entity.get("type") == "Project":
            project_id = entity["id"]

        elif "project" in entity and entity["project"].get("type") == "Project":
            # user passed a project link
            project_id = entity["project"]["id"]

        else:
            # resolve from shotgun
            data = self._sg_connection.find_one(
                entity["type"], [["id", "is", entity["id"]]], ["project"]
            )

            if not data or not data.get("project"):
                raise TankBootstrapError("Cannot resolve project for %s" % entity)
            project_id = data["project"]["id"]

        # get an object to represent the business logic for
        # how a configuration location is being determined
        self._report_progress(
            progress_callback, self._RESOLVING_CONFIG_RATE, "Resolving configuration..."
        )

        resolver = ConfigurationResolver(
            self._plugin_id, project_id, self._get_bundle_cache_fallback_paths()
        )

        # now request a configuration object from the resolver.
        # this object represents a configuration that may or may not
        # exist on disk. We can use the config object to check if the
        # object needs installation, updating etc.
        if (
            constants.CONFIG_OVERRIDE_ENV_VAR in os.environ
            and self._allow_config_overrides
        ):
            # an override environment variable has been set. This takes precedence over
            # all other methods and is useful when you do development. For example,
            # if you are developing an app and want to test it with an existing plugin
            # without wanting to rebuild the plugin, simply set this environment variable
            # to point at a local config on disk:
            #
            # TK_BOOTSTRAP_CONFIG_OVERRIDE=/path/to/dev_config
            #
            log.info(
                "Detected a %s environment variable."
                % constants.CONFIG_OVERRIDE_ENV_VAR
            )
            config_override_path = os.environ[constants.CONFIG_OVERRIDE_ENV_VAR]
            # resolve env vars and tildes
            config_override_path = os.path.expanduser(
                os.path.expandvars(config_override_path)
            )
            log.info("Config override set to '%s'" % config_override_path)

            if not os.path.exists(config_override_path):
                raise TankBootstrapError(
                    "Cannot find config '%s' defined by override env var %s."
                    % (config_override_path, constants.CONFIG_OVERRIDE_ENV_VAR)
                )

            config = resolver.resolve_configuration(
                {"type": "dev", "path": config_override_path}, self._sg_connection
            )

        elif self._do_shotgun_config_lookup:
            # do the full resolve where we connect to shotgun etc.
            log.debug("Checking for pipeline configuration overrides in Flow Production Tracking.")
            log.debug(
                "In order to turn this off, set do_shotgun_config_lookup to False"
            )
            config = resolver.resolve_shotgun_configuration(
                self._pipeline_configuration_identifier,
                self._base_config_descriptor,
                self._sg_connection,
                self._sg_user.login,
            )

        else:
            # fixed resolve based on the base config alone
            # do the full resolve where we connect to shotgun etc.
            config = resolver.resolve_configuration(
                self._base_config_descriptor, self._sg_connection
            )

        log.debug("Bootstrapping into configuration %r" % config)

        return config

    def _get_updated_configuration(self, entity, progress_callback):
        """
        Resolves the configuration and updates it.

        :param entity: Shotgun entity used to resolve a project context.
        :type entity: Dictionary with keys ``type`` and ``id``, or ``None`` for the site.
        :param progress_callback: Callback function that reports back on the toolkit bootstrap progress.
                                  Set to ``None`` to use the default callback function.

        :returns: A :class:`sgtk.bootstrap.configuration.Configuration` instance.
        """
        config = self._get_configuration(entity, progress_callback)

        # verify that this configuration works with Shotgun
        config.verify_required_shotgun_fields()

        # see what we have locally
        status = config.status()

        self._report_progress(
            progress_callback,
            self._UPDATING_CONFIGURATION_RATE,
            "Updating configuration...",
        )
        if status == Configuration.LOCAL_CFG_UP_TO_DATE:
            log.debug("Your locally cached configuration is up to date.")

        elif status == Configuration.LOCAL_CFG_MISSING:
            log.debug("A locally cached configuration will be set up.")
            config.update_configuration()

        elif status == Configuration.LOCAL_CFG_DIFFERENT:
            log.debug("Your locally cached configuration differs and will be updated.")
            config.update_configuration()

        elif status == Configuration.LOCAL_CFG_INVALID:
            log.debug(
                "Your locally cached configuration looks invalid and will be replaced."
            )
            config.update_configuration()

        else:
            raise TankBootstrapError("Unknown configuration update status!")

        return config

    def _bootstrap_sgtk(self, engine_name, entity, progress_callback=None):
        """
        Create an :class:`~sgtk.Sgtk` instance for the given entity and caches all applications.

        If entity is None, the method will bootstrap into the site
        config. This method will attempt to resolve the configuration and download it

        self._report_progress(progress_callback, self._BOOTSTRAP_COMPLETED, "Toolkit ready.")

        return tk
        locally. Note that it will not cache the application bundles.

        Please note that the API version of the :class:`~sgtk.Sgtk` instance may not be the same as the
        API version that was used during the bootstrap.

        :param entity: Shotgun entity used to resolve a project context.
        :type entity: Dictionary with keys ``type`` and ``id``, or ``None`` for the site
        :param progress_callback: Callback function that reports back on the toolkit bootstrap progress.
                                  Set to ``None`` to use the default callback function.

        :returns: Bootstrapped :class:`~sgtk.Sgtk` instance.
        """

        if progress_callback is None:
            progress_callback = self.progress_callback

        config = self._get_updated_configuration(entity, progress_callback)

        # we can now boot up this config.
        self._report_progress(
            progress_callback, self._STARTING_TOOLKIT_RATE, "Starting up Toolkit..."
        )
        tk, user = config.get_tk_instance(self._sg_user)

        # Assign the post core-swap user so the rest of the bootstrap uses the new user object.
        self._sg_user = user

        self._cache_bundles(
            config, tk.pipeline_configuration, engine_name, self.progress_callback
        )

        return tk

    def _start_engine(self, tk, engine_name, entity, progress_callback=None):
        """
        Launch into the given engine.

        If entity is None, the method will bootstrap into the site config.

        Please note that the API version of the tk instance that hosts
        the engine may not be the same as the API version that was
        executed during the bootstrap.

        :param tk: Bootstrapped :class:`~sgtk.Sgtk` instance.
        :param engine_name: Name of the engine to start up.
        :param entity: Shotgun entity used to resolve a project context.
        :type entity: Dictionary with keys ``type`` and ``id``, or ``None`` for the site.
        :param progress_callback: Callback function that reports back on the engine startup progress.
                                  Set to ``None`` to use the default callback function.
        :returns: Started :class:`~sgtk.platform.Engine` instance.
        """

        log.debug("Begin starting up engine %s." % engine_name)

        if progress_callback is None:
            progress_callback = self.progress_callback

        self._report_progress(
            progress_callback, self._RESOLVING_CONTEXT_RATE, "Resolving context..."
        )
        if entity is None:
            ctx = tk.context_empty()
        else:
            ctx = tk.context_from_entity_dictionary(entity)

        self._report_progress(
            progress_callback, self._LAUNCHING_ENGINE_RATE, "Launching Engine..."
        )
        log.debug("Attempting to start engine %s for context %r" % (engine_name, ctx))

        if self.pre_engine_start_callback:
            log.debug(
                "Invoking pre engine start callback '%s'"
                % self.pre_engine_start_callback
            )
            self.pre_engine_start_callback(ctx)
            log.debug("Pre engine start callback was invoked.")

        # perform absolute import to ensure we get the new swapped core.
        import tank

        is_shotgun_engine = engine_name == constants.SHOTGUN_ENGINE_NAME

        # If this is the shotgun engine we are starting, then we will attempt a typical
        # engine start first, which will work if the engine is configured in the standard
        # environment files in the config. If it fails, though, then we can try the
        # legacy approach, which will try to use shotgun_xxx.yml environments if they
        # exist in the config. If both fail, we reraise the legacy method exception
        # and log the first one that came from the start_engine attempt.
        if is_shotgun_engine:
            try:
                log.debug(
                    "Attempting to start the PTR engine using the standard "
                    "start_engine routine..."
                )
                engine = tank.platform.start_engine(engine_name, tk, ctx)
            except Exception as outer_exc:
                log.debug(
                    "PTR engine failed to start using start_engine. An "
                    "attempt will now be made to start it using an legacy "
                    "shotgun_xxx.yml environment. The start_engine exception "
                    "was the following: %r" % outer_exc
                )
                try:
                    engine = self._legacy_start_shotgun_engine(
                        tk, engine_name, entity, ctx
                    )
                    log.debug(
                        "PTR engine started using a legacy shotgun_xxx.yml environment."
                    )
                except tank.platform.TankMissingEnvironmentFile as exc:
                    # If the reason the new style bootstrap failed was that no environment was returned by the
                    # pick_environment hook and the old style bootstrap failed because the env file is missing,
                    # we're likely in a new style setup but trying to bootstrap using an entity that is not supported.
                    if isinstance(
                        outer_exc, tank.platform.TankUnresolvedEnvironmentError
                    ):
                        msg = (
                            "No environment was found for the context {}. The pick_environment hook was "
                            "unable to provide one, and the fallback was not successful. {}".format(
                                ctx, exc
                            )
                        )
                        log.warning(msg)
                        raise tank.platform.TankUnresolvedEnvironmentError(msg)
                    raise

                except Exception as exc:
                    log.debug(
                        "PTR engine failed to start using the legacy "
                        "start_shotgun_engine routine. No more attempts will "
                        "be made to initialize the engine. The start_shotgun_engine "
                        "exception was the following: %r" % exc
                    )
                    raise
        else:
            engine = tank.platform.start_engine(engine_name, tk, ctx)

        log.debug("Launched engine %r" % engine)

        self._report_progress(
            progress_callback, self._BOOTSTRAP_COMPLETED, "Engine launched."
        )

        return engine

    def _legacy_start_shotgun_engine(self, tk, engine_name, entity, ctx):
        """
        Starts the tk-shotgun engine by way of the legacy "start_shotgun_engine"
        method provided by tank.platform.engine.

        :param tk: Bootstrapped :class:`~sgtk.Sgtk` instance.
        :param engine_name: Name of the engine to start up.
        :param entity: Shotgun entity used to resolve a project context.
        :type entity: Dictionary with keys ``type`` and ``id``, or ``None`` for the site.
        """
        # bootstrapping into a shotgun engine with an older core
        # we perform this special check to make sure that we correctly pick up
        # the shotgun_xxx.yml environment files, even for older cores.
        # new cores handles all this inside the tank.platform.start_shotgun_engine
        # business logic.
        log.debug(
            "Target core version is %s. Starting PTR engine via legacy pathway."
            % tk.version
        )

        if entity is None:
            raise TankBootstrapError(
                "Legacy PTR environments do not support bootstrapping into a site context."
            )

        # start engine via legacy pathway
        # note the local import due to core swapping.
        from tank.platform import engine

        return engine.start_shotgun_engine(tk, entity["type"], ctx)

    def _report_progress(self, progress_callback, progress_value, message):
        """
        Helper method that reports back on the bootstrap progress to a defined progress callback.

        :param progress_callback: Callback function to use to report back.
        :param progress_value: Current progress value, a float number ranging from 0.0 to 1.0
                               representing the percentage of work completed.
        :param message: Progress message string to report.
        """

        log.debug("Progress Report (%s%%): %s" % (int(progress_value * 100), message))

        try:
            # Call the new style progress callback.
            progress_callback(progress_value, message)
        except TypeError:
            # Call the old style progress callback with signature (message, current_index, maximum_index).
            progress_callback(message, None, None)

    def _default_progress_callback(self, progress_value, message):
        """
        Default callback function that reports back on the toolkit and engine bootstrap progress.

        :param progress_value: Current progress value, ranging from 0.0 to 1.0.
        :param message: Progress message to report.
        """

        log.debug("Default progress callback (%s): %s" % (progress_value, message))

    def _default_completed_callback(self, engine):
        """
        Default callback function that handles cleanup after successful completion of the bootstrap.

        :param engine: Launched :class:`sgtk.platform.Engine` instance.
        """

        log.debug("Default completed callback: %s" % engine.instance_name)

    def _default_failed_callback(self, phase, exception):
        """
        Default callback function that handles cleanup after failed completion of the bootstrap.

        :param phase: Bootstrap phase that raised the exception,
                      ``ToolkitManager.TOOLKIT_BOOTSTRAP_PHASE`` or ``ToolkitManager.ENGINE_STARTUP_PHASE``.
        :param exception: Python exception raised while bootstrapping.
        """

        phase_name = (
            "TOOLKIT_BOOTSTRAP_PHASE"
            if phase == self.TOOLKIT_BOOTSTRAP_PHASE
            else "ENGINE_STARTUP_PHASE"
        )

        log.debug("Default failed callback (%s): %s" % (phase_name, exception))

    @staticmethod
    def get_core_python_path():
        """
        Computes the path to the current Toolkit core.

        The current Toolkit core is defined as the core that gets imported when you type
        ``import sgtk`` and the python path is derived from that module.

        For example, if the ``sgtk`` module was found at ``/path/to/config/install/core/python/sgtk``,
        the return path would be ``/path/to/config/install/core/python``

        This can be useful if you want to hand down to a subprocess the location of the current
        process's core, since ``sys.path`` and the ``PYTHONPATH`` are not updated after
        bootstrapping.

        :returns: Path to the current core.
        :rtype: str
        """
        import sgtk

        sgtk_file = inspect.getfile(sgtk)
        tank_folder = os.path.dirname(sgtk_file)
        python_folder = os.path.dirname(tank_folder)
        return python_folder
