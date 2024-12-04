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
Encapsulates the pipeline configuration and helps navigate and resolve paths
across storages, configurations etc.
"""
import os
import glob

from tank_vendor import yaml
import tank_vendor.six.moves.cPickle as pickle

from .errors import TankError, TankUnreadableFileError
from .util.version import is_version_older
from . import constants
from .platform.environment import InstalledEnvironment, WritableEnvironment
from .util import shotgun, yaml_cache
from .util import ShotgunPath
from .util import StorageRoots
from .util.pickle import retrieve_env_var_pickled
from . import hook
from . import pipelineconfig_utils
from . import template_includes
from . import LogManager

from .descriptor import Descriptor, create_descriptor, descriptor_uri_to_dict
from tank_vendor import six

log = LogManager.get_logger(__name__)


class PipelineConfiguration(object):
    """
    Represents a pipeline configuration in Tank.

    Use the factory methods in pipelineconfig_factory
    to construct this object, do not create directly via the constructor.
    """

    def __init__(self, pipeline_configuration_path, descriptor=None):
        """
        Constructor. Do not call this directly, use the factory methods
        in pipelineconfig_factory.

        NOTE ABOUT SYMLINKS!

        The pipeline_configuration_path is always populated by the paths
        that were registered in shotgun, regardless of how the symlink setup
        is handled on the OS level.

        :param str pipeline_configuration_path: Path to the pipeline configuration on disk.
        :param descriptor: Descriptor that was used to create this pipeline configuration.
            Defaults to ``None`` for backwards compatibility with Bootstrapper that only
            pass down one argument. Also this argument was passed down by cores from
            v0.18.72 to 0.18.94. The descriptor is now read from the disk inside
            pipeline_configuration.yml.
        :type descriptor: :class:`sgtk.descriptor.ConfigDescriptor`
        """
        self._pc_root = pipeline_configuration_path

        # validate that the current code version matches or is compatible with
        # the code that is locally stored in this config!!!!
        our_associated_api_version = self.get_associated_core_version()

        # and get the version of the API currently in memory
        current_api_version = pipelineconfig_utils.get_currently_running_api_version()

        if our_associated_api_version not in [
            None,
            "unknown",
            "HEAD",
        ] and is_version_older(current_api_version, our_associated_api_version):
            # currently running API is too old!
            current_api_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..")
            )

            # tell the user that their core is too old for this config
            #
            # this can happen if you are running a configuration but you are getting the core
            # API from somewhere else. For example, if you have added a core to your pythonpath
            # and then try to do sgtk_from_path("/path/to/pipeline/config") and that config
            # is using a more recent version of the core.

            raise TankError(
                "You are running Toolkit %s located in '%s'. The configuration you are "
                "trying to use needs core version %s or higher. To fix this, "
                "use the tank command (or Toolkit core API) located at '%s' "
                "which is associated with this configuration."
                % (
                    current_api_version,
                    current_api_path,
                    our_associated_api_version,
                    self.get_install_location(),
                )
            )

        # keep a storage roots object interface instance in order to query roots
        # info as needed
        config_folder = os.path.join(self._pc_root, "config")
        self._storage_roots = StorageRoots.from_config(config_folder)

        # If there are storage required for this configuration, ensure one of
        # them can be identified as the default storage. We need to keep this
        # constraint as we are not able to keep roots definition in the order
        # they were defined, so this is the only way we can guarantee we always
        # use the same root for any template which does not have an explicit
        # root setting.
        if self._storage_roots.required_roots and not self._storage_roots.default_path:
            raise TankError(
                "Could not identify a default storage root for this pipeline "
                "configuration! File: '%s'" % (self._storage_roots.roots_file,)
            )

        # get the project tank disk name (Project.tank_name),
        # stored in the pipeline config metadata file.
        pipeline_config_metadata = self._get_metadata()
        self._project_name = pipeline_config_metadata.get("project_name")
        self._project_id = pipeline_config_metadata.get("project_id")
        self._pc_id = pipeline_config_metadata.get("pc_id")
        self._plugin_id = pipeline_config_metadata.get("plugin_id")
        self._pc_name = pipeline_config_metadata.get("pc_name")
        self._published_file_entity_type = pipeline_config_metadata.get(
            "published_file_entity_type", "PublishedFile"
        )

        # Enable the use of env variables for project and pipeline configuration settings
        self._project_name = os.path.expandvars(self._project_name)
        self._pc_name = os.path.expandvars(self._pc_name)
        self._project_id = (
            int(os.path.expandvars(self._project_id))
            if isinstance(self._project_id, str)
            else self._project_id
        )
        self._pc_id = (
            int(os.path.expandvars(self._pc_id))
            if isinstance(self._pc_id, str)
            else self._pc_id
        )

        self._use_shotgun_path_cache = pipeline_config_metadata.get(
            "use_shotgun_path_cache", False
        )

        # figure out whether to use the bundle cache or the
        # local pipeline configuration 'install' cache
        if pipeline_config_metadata.get("use_bundle_cache"):
            # use bundle cache
            self._bundle_cache_root_override = None
        else:
            # use cache relative to core install
            self._bundle_cache_root_override = os.path.join(
                self.get_install_location(), "install"
            )

        if pipeline_config_metadata.get("bundle_cache_fallback_roots"):
            self._bundle_cache_fallback_paths = pipeline_config_metadata.get(
                "bundle_cache_fallback_roots"
            )
        else:
            self._bundle_cache_fallback_paths = []

        # There are five ways this initializer can be invoked.
        #
        # 1) Centralized: We're instantiated from sgtk_from_path with a single path.
        # 2) Bootstrap: path is set, descriptor is unset and no descriptor inside
        #    pipeline_configuration.yml
        # 3) Bootstrap: path is set, descriptor is set and no descriptor inside
        #    pipeline_configuration.yml
        # 4) Bootstrap, path is set, descriptor is set and descriptor inside
        #    pipeline_configuration.yml
        # 5) Baked configs via bootstrap, path is set, the rest is None. A baked
        #    config has got the same layout as a centralized installation.
        #
        # The correct way to handle all of this is to go from a descriptor string or dictionary and
        # instantiate the correct descriptor type.
        #
        # Note that since the boostapper can't tell if the pipeline configuration is going to use
        # the file to read the descriptor or not, it is always going to pass down the descriptor in
        # the arguments. We can however ignore that argument in favor of the descriptor on disk.

        descriptor_dict = pipeline_config_metadata.get("source_descriptor")
        # We'll first assume the pipeline configuration is not installed.
        is_installed = False

        # If there is a descriptor in the file (4), we know we're not installed and we're done!
        if descriptor_dict:
            # The bootstrapper wrote the descriptor in the pipeline_configuration.yml file, nothing
            # more needs to be done.
            pass

        # If there's nothing in the file, but we're being passed down something by the bootstrapper,
        # we should use it! (3)
        elif descriptor:
            # Up to 0.18.94, we could be passed in a descriptor pointing to what we now consider to
            # be an Descriptor.INSTALLED_CONFIG, but the API back then didn't make the distinction
            # and called it a Descriptor.CONFIG.

            # We will test to see if the path referred to by the descriptor is the same as the
            # current os path. If it is the same then the descriptor is an installed descriptor. If
            # it isn't then it must be pointing to something inside the bundle cache, which means it
            # isn't installed.
            if self._pc_root == descriptor.get_path():
                is_installed = True

            descriptor_dict = descriptor.get_dict()

        # Now we only have a path set. (1, 2, 5). We can't assume anything, but since all pipeline
        # configurations, cached or installed, have the same layout on disk, we'll assume that we're
        # in an installed one. Also, since installed configurations are a bit more lenient about
        # things like info.yml, its a great fit since there are definitely installed configurations
        # in the wild without an info.yml in their config folder.
        else:
            is_installed = True
            descriptor_dict = {"type": "path", "path": self._pc_root}

        descriptor = create_descriptor(
            shotgun.get_deferred_sg_connection(),
            Descriptor.INSTALLED_CONFIG if is_installed else Descriptor.CONFIG,
            descriptor_dict,
            self._bundle_cache_root_override,
            self._bundle_cache_fallback_paths,
        )

        self._descriptor = descriptor

        #
        # Now handle the case of a baked and immutable configuration.
        #
        # In this case, Toolkit is always started via the bootstrap manager.
        # A baked config means that the configuration isn't entirely determined
        # from what is written into the pipeline configuration yaml file but that
        # certain values, such as the project id, are specified at runtime.
        #
        # Such values are determined by the bootstrap process and passed via an
        # environment variable which is probed and unpacked below.
        #
        if constants.ENV_VAR_EXTERNAL_PIPELINE_CONFIG_DATA in os.environ:
            try:
                external_data = retrieve_env_var_pickled(
                    constants.ENV_VAR_EXTERNAL_PIPELINE_CONFIG_DATA
                )
            except Exception as e:
                log.warning("Could not load external config data from: %s" % e)
                external_data = {}
            finally:
                # The passing of state from bootstrap to core is complete.
                # Make sure we clean up so we don't interfere any further
                # bootstrapping or forked process bootstrapping.
                del os.environ[constants.ENV_VAR_EXTERNAL_PIPELINE_CONFIG_DATA]

            if "project_id" in external_data:
                self._project_id = external_data["project_id"]
                log.debug(
                    "%s: Setting project id to %s from external config data"
                    % (self, self._project_id)
                )

            if "project_name" in external_data:
                self._project_name = external_data["project_name"]
                log.debug(
                    "%s: Setting project name to %s from external config data"
                    % (self, self._project_name)
                )

            if "pipeline_config_id" in external_data:
                self._pc_id = external_data["pipeline_config_id"]
                log.debug(
                    "%s: Setting pipeline config id to %s from external config data"
                    % (self, self._pc_id)
                )

            if "pipeline_config_name" in external_data:
                self._pc_name = external_data["pipeline_config_name"]
                log.debug(
                    "%s: Setting pipeline config name to %s from external config data"
                    % (self, self._pc_name)
                )

            if "bundle_cache_paths" in external_data:
                self._bundle_cache_fallback_paths = external_data["bundle_cache_paths"]
                log.debug(
                    "%s: Setting bundle cache fallbacks to %s from external config data"
                    % (self, self._bundle_cache_fallback_paths)
                )

        # Populate the global yaml_cache if we find a pickled cache on disk.
        # TODO: For immutable configs, move this into bootstrap
        self._populate_yaml_cache()

        # run init hook
        self.execute_core_hook_internal(
            constants.PIPELINE_CONFIGURATION_INIT_HOOK_NAME, parent=self
        )

    def __repr__(self):
        return "<Sgtk Configuration %s>" % self._pc_root

    ########################################################################################
    # handling pipeline config metadata

    def _get_metadata(self):
        """
        Loads the pipeline config metadata (the pipeline_configuration.yml) file from disk.

        :param pipeline_config_path: path to a pipeline configuration root folder
        :returns: deserialized content of the file in the form of a dict.
        """

        # now read in the pipeline_configuration.yml file
        cfg_yml = self._get_pipeline_config_file_location()

        if not os.path.exists(cfg_yml):
            raise TankError(
                "Configuration metadata file '%s' missing! "
                "Please contact support." % cfg_yml
            )

        fh = open(cfg_yml, "rt")
        try:
            data = yaml.load(fh, Loader=yaml.FullLoader)
            if data is None:
                raise Exception("File contains no data!")
        except Exception as e:
            raise TankError(
                "Looks like a config file is corrupt. Please contact "
                "support! File: '%s' Error: %s" % (cfg_yml, e)
            )
        finally:
            fh.close()

        return data

    def _update_metadata(self, updates):
        """
        Updates the pipeline configuration on disk with the passed in values.

        :param updates: Dictionary of values to update in the pipeline configuration
        """
        # get current settings
        curr_settings = self._get_metadata()

        # apply updates to existing cache
        curr_settings.update(updates)

        # write the record to disk
        pipe_config_sg_id_path = self._get_pipeline_config_file_location()

        old_umask = os.umask(0)
        try:
            os.chmod(pipe_config_sg_id_path, 0o666)
            # and write the new file
            fh = open(pipe_config_sg_id_path, "wt")
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
            yaml.safe_dump(curr_settings, fh)
        except Exception as exp:
            raise TankError(
                "Could not write to configuration file '%s'. "
                "Error reported: %s" % (pipe_config_sg_id_path, exp)
            )
        finally:
            fh.close()
            os.umask(old_umask)

        self._project_id = curr_settings.get("project_id")
        self._pc_id = curr_settings.get("pc_id")
        self._pc_name = curr_settings.get("pc_name")

    def _get_pipeline_config_file_location(self):
        """
        Returns the location of the pipeline_configuration.yml file.
        """
        return os.path.join(
            self._pc_root, "config", "core", constants.PIPELINECONFIG_FILE
        )

    def get_yaml_cache_location(self):
        """
        Returns the location of the yaml cache for this configuration.
        """
        return os.path.join(self._pc_root, "yaml_cache.pickle")

    def _populate_yaml_cache(self):
        """
        Loads pickled yaml_cache items if they are found and merges them into
        the global YamlCache.
        """
        cache_file = self.get_yaml_cache_location()
        if not os.path.exists(cache_file):
            return

        try:
            fh = open(cache_file, "rb")
        except Exception as e:
            log.warning("Could not read yaml cache %s: %s" % (cache_file, e))
            return

        try:
            cache_items = pickle.load(fh)
            yaml_cache.g_yaml_cache.merge_cache_items(cache_items)
        except Exception as e:
            log.warning("Could not merge yaml cache %s: %s" % (cache_file, e))
        else:
            log.debug(
                "Read %s items from yaml cache %s" % (len(cache_items), cache_file)
            )
        finally:
            fh.close()

    ########################################################################################
    # general access and properties

    def get_path(self):
        """
        Returns the master root for this pipeline configuration
        """
        return self._pc_root

    def get_bundle_cache_fallback_paths(self):
        """
        Returns the list of bundle cache fallback location for this pipeline configuration.
        """
        return self._bundle_cache_fallback_paths

    def get_all_os_paths(self):
        """
        Returns the path to this config for all operating systems,
        as defined in the install_locations file.

        :returns: ShotgunPath
        """
        return pipelineconfig_utils.resolve_all_os_paths_to_config(self._pc_root)

    def get_name(self):
        """
        Returns the name of this PC.
        """
        return self._pc_name

    def is_auto_path(self):
        """
        Returns true if this config was set up with auto path mode.
        This method will connect to shotgun in order to determine the
        auto path status.

        January 2016:
        DEPRECATED - DO NOT USE! At some stage this will be removed.

        :returns: boolean indicating auto path state
        """
        if self.is_unmanaged():
            # unmanaged configs introduced in core 0.18 means that
            # pipeline configurations now may not even have a
            # pipeline configuration entity in shotgun at all. This means
            # that the configuration is tracking a particular version of a
            # config directly, without any config settings anywhere.
            #
            return False

        sg = shotgun.get_sg_connection()
        data = sg.find_one(
            constants.PIPELINE_CONFIGURATION_ENTITY,
            [["id", "is", self.get_shotgun_id()]],
            ["linux_path", "windows_path", "mac_path"],
        )

        if data is None:
            raise TankError(
                "Cannot find a Pipeline configuration in PTR "
                "that has id %s." % self.get_shotgun_id()
            )

        def _is_empty(d):
            """
            Returns true if value is "" or None, False otherwise
            """
            if d is None or d == "":
                return True
            else:
                return False

        if (
            _is_empty(data.get("linux_path"))
            and _is_empty(data.get("windows_path"))
            and _is_empty(data.get("mac_path"))
        ):
            # all three pipeline config fields are empty.
            # This means that we are running an auto path config
            return True

        else:
            return False

    def is_unmanaged(self):
        """
        Returns true if the configuration is unmanaged, e.g. it does not have a
        corresponding pipeline configuration in Shotgun.

        :return: boolean indicating if config is unmanaged
        """
        return self.get_shotgun_id() is None

    def is_localized(self):
        """
        Returns true if this pipeline configuration has its own Core

        :returns: boolean indicating if config is localized
        """
        return pipelineconfig_utils.is_localized(self._pc_root)

    def get_shotgun_id(self):
        """
        Returns the shotgun id for this PC.
        """
        return self._pc_id

    def get_plugin_id(self):
        """
        Returns the plugin id for this PC.
        For more information, see :meth:`~sgtk.bootstrap.ToolkitManager.plugin_id`.
        """
        return self._plugin_id

    def get_project_id(self):
        """
        Returns the shotgun id for the project associated with this PC.
        Can return None if the pipeline config represents the site and not a project.
        """
        return self._project_id

    def is_site_configuration(self):
        """
        Returns in the pipeline configuration is for the site configuration.

        :returns: True if this is a site configuration, False otherwise.
        """
        return self.get_project_id() is None

    def get_project_disk_name(self):
        """
        Returns the project name for the project associated with this PC.

        .. note:: If the project name spans over multiple folder levels,
                  it will contain a forward slash regardless of the current
                  operating system platform.
        """
        return self._project_name

    def get_published_file_entity_type(self):
        """
        Returns the type of entity being used
        for the 'published file' entity
        """
        return self._published_file_entity_type

    def convert_to_site_config(self):
        """
        Converts the pipeline configuration into the site configuration.
        """
        self._update_metadata({"project_id": None})

    ########################################################################################
    # path cache

    def get_shotgun_path_cache_enabled(self):
        """
        Returns true if the shotgun path cache should be used.
        This should only ever return False for setups created before 0.15.
        All projects created with 0.14+ automatically sets this to true.
        """
        return self._use_shotgun_path_cache

    def turn_on_shotgun_path_cache(self):
        """
        Updates the pipeline configuration settings to have the shotgun based (v0.15+)
        path cache functionality enabled.

        Note that you need to force a full path sync once this command has been executed.
        """

        if self.get_shotgun_path_cache_enabled():
            raise TankError("PTR based path cache already turned on!")

        self._update_metadata({"use_shotgun_path_cache": True})
        self._use_shotgun_path_cache = True

    ########################################################################################
    # storage roots related

    def get_local_storage_roots(self):
        """
        Returns local OS paths to each shotgun local storage defined in this
        configuration. Paths are validated and guaranteed not to be None.

        Raises a ``TankError`` exception if no local path could be determined
        for any storage defined in the configuration.

        :returns: dictionary of storages

        Example return dictionary::

            {
                "primary": "/studio",
                "textures": "/textures"
            }
        """

        current_os_path_lookup = {}

        for root_name, sg_path in self._storage_roots.as_shotgun_paths.items():

            # get current os path
            local_path = sg_path.current_os

            # validate it
            if local_path is None:

                raise TankError(
                    "Undefined storage! The local file storage '%s' is not "
                    "defined for this operating system! Please contact "
                    "toolkit support." % (root_name,)
                )

            current_os_path_lookup[root_name] = local_path

        return current_os_path_lookup

    def get_local_storage_for_root(self, root_name):
        """
        Given a root name, return the associated local storage in PTR.

        If no local storage can be determined, ``None`` will be returned.

        :param root_name:
        :return: A standard PTR entity dictionary for the matching PTR local
            storage.
        """

        if root_name not in self._storage_roots.required_roots:
            log.warning(
                "Unable to identify PTR local storage for root name '%s'. "
                "This root name is not required by the configuration." % (root_name,)
            )
            return None

        # get the storage data for required roots
        (mapped_roots, unmapped_roots) = self.get_local_storage_mapping()

        if root_name in mapped_roots:
            return mapped_roots[root_name]
        else:
            log.warning(
                "Unable to identify PTR local storage for root name '%s'. "
                "The root is not mapped to any PTR local storage. It does "
                "not explicitly define a local storage id and does not match "
                "the name of any known storages." % (root_name,)
            )
            return None

    def get_local_storage_mapping(self):
        """
        Returns a tuple of information about the required storage roots and how
        they map to local storages in PTR.

        The first item in the tuple is a dictionary of storage root names mapped
        to a corresponding dictionary of fields for a local storage defined in
        Shotgun.

        The second item is a list of storage roots required by the configuration
        that can not be mapped to a PTR local storage.

        Example return value::

            (
                {
                    "work": {
                        "code": "primary",
                        "type": "LocalStorage",
                        "id": 123
                        "linux_path": "/proj/work"
                        "mac_path": "/proj/work"
                        "windows_path": None
                    }
                    "data": {
                        "code": "data",
                        "type": "LocalStorage",
                        "id": 456
                        "linux_path": "/proj/data"
                        "mac_path": "/proj/data"
                        "windows_path": None
                    }
                },
                ["data2", "data3"]
            )

        In the example above, 4 storage roots are defined by the configuration:
        "work", "data", "data2", and "data3". The "work" and "data" roots can
        be associated with a PTR local storage. The other two roots have no
        corresponding local storage in PTR.

        :param: A shotgun connection
        :returns: A tuple of information about local storages mapped to the
            configuration's required storage roots.
        """
        # get the storage data for required roots
        sg = shotgun.get_sg_connection()
        return self._storage_roots.get_local_storages(sg)

    def get_all_platform_data_roots(self):
        r"""
        Similar to get_data_roots but instead of returning project data roots
        for a single operating system, the data roots for all operating systems
        are returned.

        The return structure is a nested dictionary structure, for example::

            {
                "primary": {
                    "win32": "z:\studio\my_project",
                    "linux2": "/studio/my_project",
                    "darwin": "/studio/my_project"
                },
                "textures": {
                    "win32": "z:\textures\my_project",
                    "linux2": None,
                    "darwin": "/textures/my_project"
                },
            }

        The operating system keys are returned on sys.platform-style notation.
        If a data root has not been defined on a particular platform, None is
        returned (see example above).

        :returns: dictionary of dictionaries. See above.
        """

        project_roots_lookup = {}

        for root_name, sg_path in self._storage_roots.as_shotgun_paths.items():

            # join the project name to the storage ShotgunPath
            project_root = sg_path.join(self._project_name)

            # break out the ShotgunPath object in sys.platform style dict
            project_roots_lookup[root_name] = project_root.as_system_dict()

        return project_roots_lookup

    def get_data_roots(self):
        """
        Returns a dictionary of all the data roots defined for this pipeline
        configuration, keyed by their storage name. Only returns paths for
        current platform. Paths are guaranteed to be not None.

        Exaple return dictionary::

            {
                "primary": "/studio/my_project",
                "textures": "/textures/my_project"
            }

        :returns: A dictionary of root name to project local path. See above.
        """

        project_roots_lookup = {}

        for root_name, sg_path in self._storage_roots.as_shotgun_paths.items():

            # join the project name to the storage ShotgunPath
            project_root = sg_path.join(self._project_name)

            # break out the ShotgunPath object in sys.platform style dict
            project_roots_lookup[root_name] = project_root.current_os

        return project_roots_lookup

    def has_associated_data_roots(self):
        """
        Some configurations do not have a notion of a project storage and
        therefore do not have any storages defined. This flag indicates whether
        a configuration has any associated data storages.

        :returns: True if the configuration has a data root defined, False
            otherwise.
        """

        # Return True if the default path can be identified. this implies there
        # is at least one storage root has been defined.
        return self._storage_roots.default_path is not None

    def get_primary_data_root_name(self):
        """
        Returns the default root name as defined by the required roots for this
        configuration.

        :returns: str name of a storage root
        """
        return self._storage_roots.default

    def get_primary_data_root(self):
        """
        Returns the path to the primary (default) data root for the current
        platform. For configurations where no default root path can be
        determined, a ``TankError`` exception will be raised.

        :returns: str to local path on disk
        """

        default_path = self._storage_roots.default_path

        if not default_path:
            raise TankError(
                "Could not identify a default storage root for this pipeline "
                "configuration! File: '%s'" % (self._storage_roots.roots_file,)
            )

        return default_path.join(self._project_name).current_os

    ########################################################################################
    # installation payload (core/apps/engines) disk locations

    def get_associated_core_version(self):
        """
        Returns the version string for the core api associated with this config.
        This method is 'forgiving' and in the case no associated core API can be
        found for this pipeline configuration, None will be returned rather than
        an exception raised.

        :returns: version str e.g. 'v1.2.3', None if no version could be determined.
        """
        associated_api_root = self.get_install_location()
        return pipelineconfig_utils.get_core_api_version(associated_api_root)

    def get_install_location(self):
        """
        Returns the core api install location associated with this pipeline configuration.

        Tries to resolve it via the explicit link which exists between
        the pipeline config and the its core. If this fails, it uses
        runtime introspection to resolve it.

        :returns: path string to the current core API install root location
        """
        core_api_root = pipelineconfig_utils.get_core_path_for_config(self._pc_root)

        if core_api_root is None:
            # lookup failed. fall back onto runtime introspection
            core_api_root = pipelineconfig_utils.get_path_to_current_core()

        return core_api_root

    def get_core_python_location(self):
        """
        Returns the python root for this install.

        :returns: path string
        """
        return os.path.join(self.get_install_location(), "install", "core", "python")

    ########################################################################################
    # descriptors and locations

    def execute_post_install_bundle_hook(self, bundle_path):
        """
        Executes a post install hook for a bundle.
        Some bundles come with an associated script that is meant
        to be executed after install. This method probes for such a script
        and in case it exists, executes it.

        :param bundle_path: Path to bundle (app/engine/framework)
        """
        post_install_hook_path = os.path.join(
            bundle_path, "hooks", constants.BUNDLE_POST_INSTALL_HOOK
        )

        if os.path.exists(post_install_hook_path):
            hook.execute_hook(
                post_install_hook_path,
                parent=None,
                pipeline_configuration=self.get_path(),
                path=bundle_path,
            )

    def _preprocess_descriptor(self, descriptor_dict):
        """
        Preprocess descriptor dictionary to resolve config-specific
        constants and directives such as {PIPELINE_CONFIG} and
        {CONFIG_FOLDER}

        :param descriptor_dict: Descriptor dict to operate on
        :returns: Descriptor dict with any directives resolved.
        """

        # Not a path or dev descriptor, early out.
        if descriptor_dict.get("type") not in ["dev", "path"]:
            return descriptor_dict

        # several different path parameters are supported by path based descriptors.

        substitutions = {
            constants.PIPELINE_CONFIG_DESCRIPTOR_TOKEN: self.get_path(),
            constants.CONFIG_FOLDER_DESCRIPTOR_TOKEN: self.get_config_location(),
        }

        # For each token, check if the platform or the generic path key are specified
        # and replace the token if found.
        for token, substitution in substitutions.items():
            for key in ["path", ShotgunPath.get_shotgun_storage_key()]:
                if key in descriptor_dict:
                    descriptor_dict[key] = descriptor_dict[key].replace(
                        token, substitution
                    )

        return descriptor_dict

    def _get_descriptor(
        self, descriptor_type, dict_or_uri, latest=False, constraint_pattern=None
    ):
        """
        Constructs a descriptor object given a descriptor dictionary.

        :param descriptor_type: Descriptor type (APP, ENGINE, etc)
        :param dict_or_uri: Descriptor dict or uri
        :param latest: Resolve latest version of descriptor. This
                       typically requires some sort of remote lookup and may error
                       if the machine is not connected to the Internet.
        :param constraint_pattern: If resolve_latest is True, this pattern can be used to constrain
                               the search for latest to only take part over a subset of versions.
                               This is a string that can be on the following form:
                                    - v0.1.2, v0.12.3.2, v0.1.3beta - a specific version
                                    - v0.12.x - get the highest v0.12 version
                                    - v1.x.x - get the highest v1 version
        :returns: Descriptor object
        """

        # note: certain legacy methods, for example how shotgun menu actions are cached
        # from the tank command, are not authenticated pathways. This is something we
        # ultimately need to more away from, ensuring that the system is fully authenticated
        # across the board. However, in the meantime, ensure that *basic* descriptor operations can
        # be accessed without having a valid shotgun connection by using a deferred shotgun API wrapper
        # rather than a wrapper that is initialized straight away. This ensures that a valid authentication
        # state in toolkit is not required until the connection is actually needed. In the case of descriptors,
        # a connection is typically only needed at download and when checking for latest. Path resolution
        # methods do not require a connection.
        sg_connection = shotgun.get_deferred_sg_connection()

        if isinstance(dict_or_uri, six.string_types):
            descriptor_dict = descriptor_uri_to_dict(dict_or_uri)
        else:
            descriptor_dict = dict_or_uri

        descriptor_dict = self._preprocess_descriptor(descriptor_dict)

        desc = create_descriptor(
            sg_connection,
            descriptor_type,
            descriptor_dict,
            self._bundle_cache_root_override,
            self._bundle_cache_fallback_paths,
            latest,
            constraint_pattern,
        )

        return desc

    def get_app_descriptor(self, dict_or_uri):
        """
        Convenience method that returns a descriptor for the app
        that is associated with the given descriptor.

        :param dict_or_uri: Descriptor dictionary or uri
        :returns:           Descriptor object
        """
        return self._get_descriptor(Descriptor.APP, dict_or_uri)

    def get_engine_descriptor(self, dict_or_uri):
        """
        Convenience method that returns a descriptor for the engine
        that is associated with the given descriptor.

        :param dict_or_uri: Descriptor dictionary or uri
        :returns:        Descriptor object
        """
        return self._get_descriptor(Descriptor.ENGINE, dict_or_uri)

    def get_framework_descriptor(self, dict_or_uri):
        """
        Convenience method that returns a descriptor for the framework
        that is associated with the given descriptor.

        :param dict_or_uri: Descriptor dictionary or uri
        :returns:        Descriptor object
        """
        return self._get_descriptor(Descriptor.FRAMEWORK, dict_or_uri)

    def get_latest_app_descriptor(self, dict_or_uri):
        """
        Convenience method that returns the latest descriptor for the
        given app. The descriptor dictionary or uri does not have to contain
        any version information. This will be resolved as part of the call.
        Please note that this call may be slow as it will typically connect
        to an external source (git, toolkit app store etc) in order to determine
        which the most recent version is.

        :param dict_or_uri: Descriptor dictionary or uri
        :returns:           Descriptor object
        """
        return self._get_descriptor(Descriptor.APP, dict_or_uri, latest=True)

    def get_latest_engine_descriptor(self, dict_or_uri):
        """
        Convenience method that returns the latest descriptor for the
        given engine. The descriptor dictionary or uri does not have to contain
        any version information. This will be resolved as part of the call.
        Please note that this call may be slow as it will typically connect
        to an external source (git, toolkit app store etc) in order to determine
        which the most recent version is.

        :param dict_or_uri: Descriptor dictionary or uri
        :returns:        Descriptor object
        """
        return self._get_descriptor(Descriptor.ENGINE, dict_or_uri, latest=True)

    def get_latest_framework_descriptor(self, dict_or_uri, constraint_pattern=None):
        """
        Convenience method that returns the latest descriptor for the
        given framework. The descriptor dictionary or uri does not have to contain
        any version information. This will be resolved as part of the call.
        Please note that this call may be slow as it will typically connect
        to an external source (git, toolkit app store etc) in order to determine
        which the most recent version is.

        :param dict_or_uri: Descriptor dictionary or uri
        :param constraint_pattern: This pattern can be used to constrain
                                   the search for latest to only take part over a subset of versions.
                                   This is a string that can be on the following form:
                                        - v0.1.2, v0.12.3.2, v0.1.3beta - a specific version
                                        - v0.12.x - get the highest v0.12 version
                                        - v1.x.x - get the highest v1 version
        :returns:        Descriptor object
        """
        return self._get_descriptor(
            Descriptor.FRAMEWORK,
            dict_or_uri,
            latest=True,
            constraint_pattern=constraint_pattern,
        )

    def get_configuration_descriptor(self):
        """
        Returns the :class:`~sgtk.descriptor.ConfigDescriptor` associated with
        the pipeline configuration.
        """
        return self._descriptor

    ########################################################################################
    # configuration disk locations

    def get_core_hooks_location(self):
        """
        Returns the path to the core hooks location

        :returns: path string
        """
        return os.path.join(os.path.join(self.get_config_location(), "core"), "hooks")

    def get_schema_config_location(self):
        """
        Returns the location of the folder schema

        :returns: path string
        """
        return os.path.join(os.path.join(self.get_config_location(), "core"), "schema")

    def get_config_location(self):
        """
        Returns the config folder location for the project

        :returns: path string
        """
        return self._descriptor.get_config_folder()

    def get_hooks_location(self):
        """
        Returns the hooks folder for the project

        :returns: path string
        """
        return os.path.join(self.get_config_location(), "hooks")

    def get_shotgun_menu_cache_location(self):
        """
        returns the folder where shotgun menu cache files
        (used by the browser plugin and java applet) are stored.

        :returns: path string
        """
        return os.path.join(self._pc_root, "cache")

    ########################################################################################
    # configuration data access

    def get_environments(self):
        """
        Returns a list with all the environments in this configuration.
        """
        env_names = []
        for f in glob.glob(self.get_environment_path("*")):
            file_name = os.path.basename(f)
            (name, _) = os.path.splitext(file_name)
            env_names.append(name)
        return env_names

    def get_environment(self, env_name, context=None, writable=False):
        """
        Returns an environment object given an environment name.
        You can use the get_environments() method to get a list of
        all the environment names.

        :param env_name:    name of the environment to load
        :param context:     context to seed the environment with
        :param writable:    If true, a writable environment object will be
                            returned, allowing a user to update it.
        :returns:           An environment object
        """
        env_file = self.get_environment_path(env_name)
        EnvClass = WritableEnvironment if writable else InstalledEnvironment
        env_obj = EnvClass(env_file, self, context)
        return env_obj

    def get_environment_path(self, env_name):
        """
        Returns the path to the environment yaml file for the given
        environment name for this pipeline configuration.

        :param env_name:    The name of the environment.
        :returns:           String path to the environment yaml file.
        """
        return os.path.join(self.get_config_location(), "env", "%s.yml" % env_name)

    def _get_templates_config_location(self):
        """
        Returns the path to the configuration's template file.
        """
        return os.path.join(
            os.path.join(self.get_config_location(), "core"),
            constants.CONTENT_TEMPLATES_FILE,
        )

    def get_templates_config(self):
        """
        Returns the templates configuration as an object
        """
        templates_file = self._get_templates_config_location()

        try:
            data = (
                yaml_cache.g_yaml_cache.get(templates_file, deepcopy_data=False) or {}
            )
            data = template_includes.process_includes(templates_file, data)
        except TankUnreadableFileError:
            data = dict()

        return data

    ########################################################################################
    # helpers and internal

    def execute_core_hook_internal(self, hook_name, parent, **kwargs):
        """
        Executes an old-style core hook, passing it any keyword arguments supplied.

        Typically you don't want to execute this method but instead
        the tk.execute_core_hook method. Only use this one if you for
        some reason do not have a tk object available.

        :param hook_name: Name of hook to execute.
        :param parent: Parent object to pass down to the hook
        :param **kwargs: Named arguments to pass to the hook
        :returns: Return value of the hook.
        """
        # first look for the hook in the pipeline configuration
        # if it does not exist, fall back onto core API default implementation.
        hook_folder = self.get_core_hooks_location()
        file_name = "%s.py" % hook_name
        hook_path = os.path.join(hook_folder, file_name)
        if not os.path.exists(hook_path):
            # no custom hook detected in the pipeline configuration
            # fall back on the hooks that come with the currently running version
            # of the core API.
            hooks_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "hooks")
            )
            hook_path = os.path.join(hooks_path, file_name)

        try:
            return_value = hook.execute_hook(hook_path, parent, **kwargs)
        except:
            # log the full callstack to make sure that whatever the
            # calling code is doing, this error is logged to help
            # with troubleshooting and support
            log.exception("Exception raised while executing hook '%s'" % hook_path)
            raise

        return return_value

    def execute_core_hook_method_internal(
        self, hook_name, method_name, parent, **kwargs
    ):
        """
        Executes a new style core hook, passing it any keyword arguments supplied.

        Typically you don't want to execute this method but instead
        the tk.execute_core_hook method. Only use this one if you for
        some reason do not have a tk object available.

        :param hook_name: Name of hook to execute.
        :param method_name: Name of hook method to execute
        :param parent: Parent object to pass down to the hook
        :param **kwargs: Named arguments to pass to the hook
        :returns: Return value of the hook.
        """
        # this is a new style hook which supports an inheritance chain

        # first add the built-in core hook to the chain
        file_name = "%s.py" % hook_name
        hooks_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "hooks")
        )
        hook_paths = [os.path.join(hooks_path, file_name)]

        # the hook.method display name used when logging the metric
        hook_method_display = "%s.%s" % (hook_name, method_name)

        # now add a custom hook if that exists.
        hook_folder = self.get_core_hooks_location()
        hook_path = os.path.join(hook_folder, file_name)
        if os.path.exists(hook_path):
            hook_paths.append(hook_path)

        try:
            return_value = hook.execute_hook_method(
                hook_paths, parent, method_name, **kwargs
            )
        except:
            # log the full callstack to make sure that whatever the
            # calling code is doing, this error is logged to help
            # with troubleshooting and support
            log.exception("Exception raised while executing hook '%s'" % hook_paths[-1])
            raise

        return return_value
