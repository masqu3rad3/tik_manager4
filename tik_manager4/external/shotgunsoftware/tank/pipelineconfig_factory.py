# Copyright (c) 2014 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import collections
import pprint


from .errors import TankError, TankInitError
from . import LogManager
from .util import shotgun
from .util import pickle
from .util import filesystem
from .util import ShotgunPath
from . import constants
from . import pipelineconfig_utils
from .pipelineconfig import PipelineConfiguration
from .util import LocalFileStorageManager

try:
    from tank_vendor import sgutils
except ImportError:
    from tank_vendor import six as sgutils

log = LogManager.get_logger(__name__)


def from_entity(entity_type, entity_id):
    """
    Factory method that constructs a pipeline configuration given a Shotgun Entity.

    Validates that the currently loaded core API is compliant with the configuration
    associated with the entity and attempts to construct a :class:`PipelineConfiguration`.

    :param str entity_type: Shotgun Entity type
    :param int entity_id: Shotgun id
    :returns: Pipeline Configuration instance
    :rtype: :class:`PipelineConfiguration`
    :raises: :class:`TankInitError`
    """
    log.debug("Executing sgtk.from_entity factory for %s %s" % (entity_type, entity_id))
    try:
        pc = _from_entity(entity_type, entity_id, force_reread_shotgun_cache=False)
    except TankInitError:
        # lookup failed! This may be because there are missing items
        # in the cache. For failures, try again, but this time
        # force re-read the cache (e.g connect to shotgun)
        # if the previous failure was due to a missing item
        # in the cache,
        pc = _from_entity(entity_type, entity_id, force_reread_shotgun_cache=True)

    log.debug("sgtk.from_path resolved %s %s -> %s" % (entity_type, entity_id, pc))
    return pc


def _from_entity(entity_type, entity_id, force_reread_shotgun_cache):
    """
    Factory method that constructs a pipeline configuration given a Shotgun Entity.

    For info, see :meth:`from_entity`

    :param str entity_type: Shotgun Entity type
    :param int entity_id: Shotgun id
    :param bool force_reread_shotgun_cache: If true,
        fresh values will be cached from Shotgun.
    :returns: Pipeline Configuration instance
    :rtype: :class:`PipelineConfiguration`
    :raises: :class:`TankInitError`
    """
    # first see if we can resolve a project id from this entity
    project_id = __get_project_id(entity_type, entity_id, force_reread_shotgun_cache)

    log.debug(
        "The project id associated with %s %s was determined "
        "to be %s" % (entity_type, entity_id, project_id)
    )

    # now given the project id, find the pipeline configurations
    if project_id is None:
        raise TankInitError(
            "%s %s is not associated with a project and "
            "can therefore not be associated with a "
            "pipeline configuration." % (entity_type, entity_id)
        )

    # now find the pipeline configurations that are matching this project
    data = _get_pipeline_configs(force_reread_shotgun_cache)
    associated_sg_pipeline_configs = _get_pipeline_configs_for_project(project_id, data)

    log.debug(
        "Associated pipeline configurations are: %s"
        % pprint.pformat(associated_sg_pipeline_configs)
    )

    if len(associated_sg_pipeline_configs) == 0:
        raise TankInitError(
            "No pipeline configurations associated with %s %s."
            % (entity_type, entity_id)
        )

    # perform various validations to make sure the version of the sgtk codebase running
    # is associated with the given configuration correctly, and if successful,
    # create a pipeline configuration
    return _validate_and_create_pipeline_configuration(
        associated_sg_pipeline_configs, source="%s %s" % (entity_type, entity_id)
    )


def from_path(path):
    """
    Factory method that constructs a pipeline configuration given a path on disk.

    The path can either be a path pointing directly at a pipeline configueration
    on disk or a path to an asset which belongs to a toolkit project.

    Validates that the currently loaded core API is compliant with the configuration
    associated with the entity and attempts to construct a :class:`PipelineConfiguration`.

    :param str path: Path to a pipeline configuration or associated project folder
    :returns: Pipeline Configuration instance
    :rtype: :class:`PipelineConfiguration`
    :raises: :class:`TankInitError`
    """
    log.debug("Executing sgtk.from_path factory for '%s'" % path)
    try:
        pc = _from_path(path, force_reread_shotgun_cache=False)
    except TankInitError:
        # lookup failed! This may be because there are missing items
        # in the cache. For failures, try again, but this time
        # force re-read the cache (e.g connect to shotgun)
        # if the previous failure was due to a missing item
        # in the cache,
        pc = _from_path(path, force_reread_shotgun_cache=True)

    log.debug("sgtk.from_path resolved '%s' -> %s" % (path, pc))
    return pc


def _from_path(path, force_reread_shotgun_cache):
    """
    Internal method that validates and constructs a pipeline configuration given a path on disk.

    For info, see :meth:`from_path`.

    :param str path: Path to a pipeline configuration or associated project folder
    :param bool force_reread_shotgun_cache: If true,
        fresh values will be cached from Shotgun.
    :returns: Pipeline Configuration instance
    :rtype: :class:`PipelineConfiguration`
    :raises: :class:`TankInitError`
    """
    if not isinstance(path, str):
        raise ValueError(
            "Cannot create a configuration from path '%s' - path must be a string."
            % path
        )

    path = os.path.abspath(path)

    # make sure folder exists on disk
    if not os.path.exists(path):
        # there are cases when a pipeline config is being created
        # from a _file_ which does not yet exist on disk. To try to be
        # reasonable with this case, try this check on the
        # parent folder of the path as a last resort.
        parent_path = os.path.dirname(path)
        if os.path.exists(parent_path):
            path = parent_path
        else:
            raise ValueError(
                "Cannot create a configuration from path '%s' - path does not exist on disk."
                % path
            )

    # first see if someone is passing the path to an actual pipeline configuration
    if pipelineconfig_utils.is_pipeline_config(path):

        log.debug("The path %s points at a pipeline configuration." % path)

        # resolve the "real" location that is stored in Shotgun and
        # cached in the file system
        pc_registered_path = pipelineconfig_utils.get_config_install_location(path)

        log.debug(
            "Resolved the official path registered in PTR to be %s." % pc_registered_path
        )

        if pc_registered_path is None:
            raise TankError(
                "Error starting from the configuration located in '%s' - "
                "it looks like this pipeline configuration and tank command "
                "has not been configured for the current operating system." % path
            )

        return PipelineConfiguration(pc_registered_path)

    # now get storage and project data from shotgun.
    # this will use a cache unless the force flag is set
    sg_data = _get_pipeline_configs(force_reread_shotgun_cache)

    # now given ALL pipeline configs for ALL projects and their associated projects
    # and project root paths (in sg_data), figure out which pipeline configurations
    # are matching the given path. This is done by walking upwards in the path
    # until a project root is found, and then figuring out which pipeline configurations
    # belong to that project root.
    associated_sg_pipeline_configs = _get_pipeline_configs_for_path(path, sg_data)

    log.debug(
        "Associated pipeline configurations are: %s"
        % pprint.pformat(associated_sg_pipeline_configs)
    )

    if len(associated_sg_pipeline_configs) == 0:
        # no matches! The path is invalid or does not belong to any project on the current sg site.
        raise TankInitError(
            "The path '%s' does not belong to any known Toolkit project!" % path
        )

    # perform various validations to make sure the version of the sgtk codebase running
    # is associated with the given configuration correctly, and if successful,
    # create a pipeline configuration
    return _validate_and_create_pipeline_configuration(
        associated_sg_pipeline_configs, source=path
    )


def _validate_and_create_pipeline_configuration(associated_pipeline_configs, source):
    """
    Given a set of pipeline configuration, validate that the currently running code
    is compliant and construct and return a suitable pipeline configuration instance.

    This method takes into account complex new and old logic, including centralized
    setups, shared cores and bootstrap workflows.

    The associated_pipeline_configs parameter contains a list of potential pipeline
    configuration shotgun dictionaries which should be considered for resolution.
    Each dictionary contains the following entries:

        - id (pipeline configuration id)
        - type (e.g. ``PipelineConfiguration``)
        - code
        - windows_path
        - linux_path
        - mac_path
        - project (associated project entity link)

    This method will either return a pipeline configuration instance based on
    one of the ``associated_pipeline_configs`` entries or raise a TankInitError
    exception.

    :param list associated_pipeline_configs: Associated Shotgun data.
    :param str source: String describing what is being manipulated,
        e.g. a path or 'Project 123'. Used for error messages and log feedback.
    :returns: Pipeline config instance.
    :rtype: :class:`PipelineConfiguration`
    :raises: :class:`TankInitError` with detailed descriptions.
    """
    # extract path data from the pipeline configuration shotgun data
    # this will return lists of dicts with keys ``id``, (local os) ``path`` and ``project_id``
    (all_pc_data, primary_pc_data) = _get_pipeline_configuration_data(
        associated_pipeline_configs
    )

    # format string with all configs, for error reporting.
    all_configs_str = ", ".join(
        [
            "'%s' (Pipeline config id %s, Project id %s)"
            % (x["path"], x["id"], x["project_id"])
            for x in all_pc_data
        ]
    )

    # Introspect the TANK_CURRENT_PC env var to determine which pipeline configuration
    # the current sgtk import belongs to.
    #
    # if the call returns a path, we are running a inside a pipeline configuration.
    # If it returns None, we are running a shared core, e.g. a core API which is
    # used by multiple pipeline configurations.
    config_context_path = _get_configuration_context()

    if config_context_path:

        # --- RUNNING THE API WITHIN A PROJECT ----

        # This is the localized case where the imported code has a 1:1 correspondence
        # with the pipeline configuration. Now we need to verify that the path is compatible
        # with this configuration, or raise an exception.

        # create an instance to represent our path
        pipeline_configuration = PipelineConfiguration(config_context_path)

        # get pipeline config shotgun id
        pc_id = pipeline_configuration.get_shotgun_id()

        # find the pipeline config in our list of configs. If we cannot find it, we
        # don't have a match beetween the code that is being run and the config
        # we are trying to start up.

        if pc_id not in [x["id"] for x in all_pc_data]:

            log.debug(
                "The currently running sgtk API code is not associated with "
                "%s so a pipeline configuration cannot be initialized. "
                "The configurations associated are: %s "
                "Please use the tank command or Toolkit API associated with one "
                "of those locations in order to continue. " % (source, all_configs_str)
            )

            log.debug(
                "This error can occur if you have moved a centralized toolkit configuration "
                "manually rather than using the 'tank move_configuration command'. "
                "It can also occur if you are trying to use a tank command associated "
                "with one Project to try to operate on a Shot or Asset "
                "that belongs to another project."
            )

            raise TankInitError(
                "You are loading the Toolkit platform from the pipeline configuration "
                "located in '%s', with PTR id %s. You are trying to initialize Toolkit "
                "from %s, however that is not associated with the pipeline configuration. "
                "Instead, it's associated with the following configurations: %s. "
                % (config_context_path, pc_id, source, all_configs_str)
            )

        else:
            # ok we got a pipeline config matching the tank command from which we launched.
            # because we found the pipeline config in the list of PCs for this project,
            # we know that it must be valid!
            return pipeline_configuration

    else:

        # --- RUNNING THE API WITHIN A CENTRALIZED CORE ----
        #
        # When you are running the tank command or import sgtk from a shared core.
        #
        # we are running the tank command or API from the studio location, e.g.
        # a core which is located outside a pipeline configuration.
        # in this case, find the primary pipeline config and use that.
        #
        # note: This kind of setup is not compatible with distributed setups, where
        #       all configurations are effectively always localized.
        #

        # We're running with a centralized pipeline configuration with shared core, which means we can
        # ignore site-wide pipeline configurations as they are not compatible with this way of doing
        # configs. Strip them all out so only project based pipeline configurations remain. This is
        # important otherwise more than one primary might match a centralized core.
        primary_pc_data = [pc for pc in primary_pc_data if pc["project_id"]]

        if len(primary_pc_data) == 0:

            raise TankInitError(
                "The project associated with %s does not have a Primary pipeline "
                "configuration! This is required by Toolkit. It needs to be named '%s'. "
                "Please double check the Pipeline configuration page in "
                "PTR for the project. The following pipeline configurations are "
                "associated with the path: %s"
                % (source, constants.PRIMARY_PIPELINE_CONFIG_NAME, all_configs_str)
            )

        elif len(primary_pc_data) > 1:
            # for an entity lookup, there should be no ambiguity - an entity belongs to a project
            # and a project has got a distinct set of pipeline configs, exactly one of which
            # is the primary. This ambiguity may arise from having pipeline configurations
            # incorrectly re-using the same paths.

            raise TankInitError(
                "%s is associated with more than one centralized Primary pipeline "
                "configuration. This can happen if there is ambiguity in your project setup, where "
                "projects store their data in an overlapping fashion, for example if a project is "
                "named the same as a local storage root. In this case, try creating "
                "your API instance (or tank command) directly from the pipeline configuration rather "
                "than via the studio level API. This will explicitly call out which project you are "
                "intending to use in conjunction with he path. It may also be caused by several projects "
                "pointing at the same configuration on disk. The Primary pipeline configuration paths "
                "associated with this path are: %s." % (source, all_configs_str)
            )

        else:
            # looks good, we got a primary pipeline config that exists in Shotgun.
            sg_config_data = primary_pc_data[0]

            # with direct access from shared cores, we don't support bootstrap workflows.
            # For this case, you HAVE to use the centralized config fields windows|mac|linux_path.
            if sg_config_data["path"] is None:
                # will not end up here unless someone tries to run shared_core on a
                # configuration which is maintained by bootstrap.
                raise TankInitError(
                    "The pipeline configuration with id %s, associated with %s, "
                    "cannot be instantiated because it is a distributed config. "
                    "To launch this kind of configuration, use "
                    "the Bootstrap API instead." % (sg_config_data["id"], source)
                )

            # This checks for a very subtle bug. If the toolkit_init.cache contains a path to a
            # pipeline configuration that matches the pre-requisites, but that doesn't actually
            # exist on disk because it was either moved to another location or deleted from disk
            # altogether, then we need to raise TankInitError. If the cache hadn't been force
            # reread, this will be caught by the factory and Shotgun will be queried once again for
            # the pipeline configuration info, hopefully finding the real pipeline configuration
            # this time around.
            if not os.path.exists(sg_config_data["path"]):
                raise TankInitError(
                    "The centralized pipeline configuration %s does not exist on disk. "
                    "This can happen if it has been moved to another location or deleted from "
                    "disk." % sg_config_data["path"]
                )

            # all good. init and return.
            return PipelineConfiguration(sg_config_data["path"])


#################################################################################################################
# utilities


def _get_configuration_context():
    """
    Returns a path if the API was invoked via a configuration context, otherwise None.

    If this session was involved (tank command or python API) from a studio level API,
    e.g. with no connection to any config, None is returned.

    In the case the session was started via a python proxy API or tank command
    connected to a configuration, the path to that configuration root is returned.
    The path returned is normalized and should reflect the exact value stored in the
    pipeline configuration entry in shotgun.

    :returns: path or None
    """
    # default for studio level tank command/API
    val = None

    if "TANK_CURRENT_PC" in os.environ:
        # config level tank command/API
        curr_pc_path = os.environ["TANK_CURRENT_PC"]

        # the path stored in the TANK_CURRENT_PC env var may be a symlink etc.
        # now we need to find which pipeline config entity this corresponds to in Shotgun.
        # Once found, we can double check that the current Entity is actually
        # associated with the project that the pipeline config is associated with.
        val = pipelineconfig_utils.get_config_install_location(curr_pc_path)

    return val


def _get_pipeline_configuration_data(sg_pipeline_configs):
    """
    Helper method. Given a list of Shotgun Pipeline configuration entity data, return a
    simplified list of pipeline configuration data.

    Returns a tuple with two lists (pc_data, primary_data):

    - The first first list includes one entry for all pipeline configurations
      specified in the sg_pipeline_configs input dictionary.
    - The second list includes only primary configuration entries.

    Both lists consists of dictionaries with the following keys:

    - path: A local, sanitized path to the pipeline configuration
    - id: The Shotgun id of the pipeline configuration
    - project_id: The Shotgun id of the associated project or None if the
      pipeline configuration doesn't have a project.

    :param sg_pipeline_configs: Shotgun pipeline configuration data. List of dicts.
    :returns: (pc_data, primary_data) - tuple with two lists of dicts. See above.
    """
    # get list of local path to pipeline configurations that we have
    pc_data = []
    primary_data = []

    for pc in sg_pipeline_configs:

        # extract path from shotgun, sanitize and get curr os path
        pc_path = ShotgunPath.from_shotgun_dict(pc)
        curr_os_path = pc_path.current_os

        # project is None for site config else dict
        project_id = pc["project"]["id"] if pc.get("project") else None

        pc_entry = {"path": curr_os_path, "id": pc["id"], "project_id": project_id}

        # and append to our return data structures
        pc_data.append(pc_entry)
        if pc.get("code") == constants.PRIMARY_PIPELINE_CONFIG_NAME:
            primary_data.append(pc_entry)

    return pc_data, primary_data


def _get_pipeline_configs_for_path(path, data):
    r"""
    Given a path on disk and a cache data structure, return a list of
    associated pipeline configurations.

    Based on the Shotgun cache data, generates a list of project root locations.
    These are then compared (case insensitively) against the given path and
    if it is determined that the input path belongs to any of these project
    roots, the list of pipeline configuration objects for that root is returned.

    the return data structure is a list of dicts, each dict containing the
    following fields:

        - id
        - code
        - windows_path
        - linux_path
        - mac_path
        - project

    Edge case notes:

    Normally, this command returns all the pipeline configurations that
    are associated with a single project only.

    However, there are edge cases where it may return pipeline configurations
    for *multiple* projects.

    in the case there are overlapping storage roots, or where a project is named
    the same name as a storage root, this may lead to a scenario where a path on
    disk could potentially belong to *two* projects. In this case, this method will
    return the pipeline configurations for both projects.

    For example, imagine the following setup:

    Storages: f:\ and f:\foo
    Project names: foo and bar

    (Note that the project name 'foo' is named the same as the storage F:\foo)

    This means we have the following project roots:
    (1) f:\foo      (storage f:\, project foo)
    (2) f:\bar      (storage f:\, project bar)
    (3) f:\foo\foo  (storage f:\foo, project foo)
    (4) f:\foo\bar  (storage f:\foo, project bar)

    If we have a path f:\foo\bar\hello_world.ma, this could either belong to
    project 'bar' (matching 4) or project 'foo' (matching 1).

    In this case, the pipeline configurations for both foo and bar
    are returned.

    :param path: Path to look for
    :param data: Cache data chunk, obtained using _get_pipeline_configs()
    :returns: list of pipeline configurations matching the path, [] if no match.
    """
    # step 1 - extract all storages for the current os
    storages = []
    for s in data["local_storages"]:
        storage_path = ShotgunPath.from_shotgun_dict(s).current_os
        if storage_path:
            storages.append(storage_path)

    # step 2 - build a dict of storage project paths and associate with project id
    project_paths = collections.defaultdict(list)
    for pc in data["pipeline_configurations"]:

        for storage in storages:

            # This pipeline can be associated with all projects, so add this
            # pipeline configuration to all project paths
            if pc["project"] is None:
                for project in data["projects"].values():
                    if project["tank_name"]:
                        _add_to_project_paths(
                            project_paths, project["tank_name"], storage, pc
                        )

            else:
                # centralized pipeline configurations are associated with a
                # project which has a tank_name set. this key should always exist,
                # but the value may be None for projects not using the
                # templates/schema system. for safety, call 'get' as we've seen
                # issues with invalid/corrupt toolkit_init caches.
                project_id = pc["project"]["id"]
                project_name = data["projects"][project_id].get("tank_name")

                # this method is used to look up the appropriate configuration given
                # a path on disk. Configurations that don't have a file system
                # presence (not using the templates/schema system) can be safely
                # ignored as the path can't be associated with that type of
                # configuration
                if not project_name:
                    continue

                _add_to_project_paths(project_paths, project_name, storage, pc)

    # step 3 - look at the path we passed in - see if any of the computed
    # project folders are determined to be a parent path
    all_matching_pcs = []

    for project_path in project_paths:

        # (like the PTR API, this logic is case preserving, not case insensitive)
        path_lower = sgutils.ensure_str(path.lower())
        proj_path_lower = sgutils.ensure_str(project_path.lower())
        # check if the path matches. Either
        # direct match: path: /mnt/proj_x == project path: /mnt/proj_x
        # child path: path: /mnt/proj_x/foo/bar starts with /mnt/proj_x/

        if path_lower == proj_path_lower or path_lower.startswith(
            "%s%s" % (proj_path_lower, os.path.sep)
        ):
            # found a match!
            associated_pcs = project_paths[project_path]
            all_matching_pcs.extend(associated_pcs)

    return all_matching_pcs


def _add_to_project_paths(project_paths, project_name, storage, pipeline_config):
    """
    Adds a pipeline configuration to the list of pipelines that can be used
    with a given storage path.

    :param projects_path: Mapping between a project's path inside the storage
        all the pipeline configurations that can understand it.
    :param name: tank_name of the project.
    :param storage: Storage root path for the current OS.
    :param pipeline_config: Pipeline configuration entity to add.
    """

    # for multi level projects, there may be slashes, e.g
    # project_name is "parent/child"
    # ensure this is translated to "parent\child" on windows
    project_name = project_name.replace("/", os.path.sep)

    # now, another windows edge case we need to ensure is covered
    # if a windows storage is defined as 'x:', then
    # os.path.join('x:', 'folder') will return 'x:folder'
    # and not 'x:\folder as we would expect
    # so ensure that any path on this form is extended:
    # 'x:' --> 'x:\'
    if len(storage) == 2 and storage.endswith(":"):
        storage = "%s%s" % (storage, os.path.sep)

    # and concatenate it with the storage
    project_path = os.path.join(storage, project_name)

    # Associate this path with the pipeline configuration if it's not already.
    # If there are multiple storages defined with the same path,
    # this prevents the pipeline config from being added multiple times.
    # Ultimately we probably want to check that the storage
    # is being used by the pipeline config by checking the roots.yml
    # in the pipeline config before associating it here.
    if pipeline_config not in project_paths[project_path]:
        project_paths[project_path].append(pipeline_config)


def _get_pipeline_configs_for_project(project_id, data):
    """
    Given a project id, return a list of associated pipeline configurations.

    Based on the Shotgun cache data, generates a list of project root locations.
    These are then compared (case insensitively) against the given path and
    if it is determined that the input path belongs to any of these project
    roots, the list of pipeline configuration objects for that root is returned.

    the return data structure is a list of dicts, each dict containing the
    following fields:

        - id
        - code
        - windows_path
        - linux_path
        - mac_path
        - project

    :param project_id: Project id to look for
    :param data: Cache data chunk, obtained using _get_pipeline_configs()
    :returns: list of pipeline configurations matching the path, [] if no match.
    """
    matching_pipeline_configs = []

    for pc in data["pipeline_configurations"]:

        # The pipeline configuration can match a project if it has no project associated or if it is
        # associated to it.
        if pc["project"] is None or pc["project"]["id"] == project_id:
            matching_pipeline_configs.append(pc)

    return matching_pipeline_configs


#################################################################################################################
# methods relating to maintaining a small cache to speed up initialization


def __get_project_id(entity_type, entity_id, force=False):
    """
    Connects to Shotgun and retrieves the project id for an entity.

    Uses a cache if possible.

    :param entity_type: Shotgun Entity type
    :param entity_id: Shotgun entity id
    :param force: Force read values from Shotgun
    :returns: project id (int) or None if not found
    """
    if entity_type == "Project":
        # don't need the cache for this one :)
        return entity_id

    CACHE_KEY = "%s_%s" % (entity_type, entity_id)

    if force is False:
        # try to load cache first
        # if that doesn't work, fall back on shotgun
        cache = _load_lookup_cache()
        if cache and cache.get(CACHE_KEY):
            # cache hit!
            return cache.get(CACHE_KEY)

    # ok, so either we are force recomputing the cache or the cache wasn't there
    sg = shotgun.get_sg_connection()

    # get all local storages for this site
    entity_data = sg.find_one(entity_type, [["id", "is", entity_id]], ["project"])

    project_id = None
    if entity_data and entity_data["project"]:
        # we have a project id! - cache this data
        project_id = entity_data["project"]["id"]
        _add_to_lookup_cache(CACHE_KEY, project_id)

    return project_id


def _get_pipeline_configs(force=False):
    """
    Connects to Shotgun and retrieves information about all projects
    and all pipeline configurations in Shotgun. Adds this to the disk cache.
    If a cache already exists, this is used instead of talking to Shotgun.

    To force a re-cache, set the force flag to True.

    Returns a complex data structure with the following fields

    local_storages:
        - id
        - code
        - windows_path
        - mac_path
        - linux_path

    pipeline_configurations:
        - id
        - code
        - windows_path
        - linux_path
        - mac_path
        - project
        - plugin_ids

    projects:
        - id
        - tank_name

    :param force: set this to true to force a cache refresh
    :returns: dictionary with keys local_storages and pipeline_configurations.
    """

    # The new cache is not backwards compatible with previous version of Toolkit, so create
    # new cache key.
    CACHE_KEY = "paths_v2"

    if force is False:
        # try to load cache first
        # if that doesn't work, fall back on shotgun
        cache = _load_lookup_cache()
        if cache and cache.get(CACHE_KEY):
            # cache hit!
            return cache.get(CACHE_KEY)

    # ok, so either we are force recomputing the cache or the cache wasn't there
    sg = shotgun.get_sg_connection()

    # get all local storages for this site
    local_storages = sg.find(
        "LocalStorage", [], ["id", "code", "windows_path", "mac_path", "linux_path"]
    )

    # get all pipeline configurations (and their associated projects) for this site.
    #
    # To make sure we are not retrieving more and more projects over time, only
    # include non-archived projects.
    #
    # Note that we are using the filter_operator "any", not the default "all".
    pipeline_configs = sg.find(
        "PipelineConfiguration",
        [["project.Project.archived", "is", False], ["project", "is", None]],
        ["id", "code", "windows_path", "linux_path", "mac_path", "project"],
        filter_operator="any",
    )

    projects = sg.find("Project", [["archived", "is", False]], ["name", "tank_name"])

    # Index the result by project id so look-ups are easier to do later on.
    projects = dict((project["id"], project) for project in projects)

    # cache this data
    data = {
        "local_storages": local_storages,
        "pipeline_configurations": pipeline_configs,
        "projects": projects,
    }
    _add_to_lookup_cache(CACHE_KEY, data)

    return data


def _load_lookup_cache():
    """
    Load lookup cache file from disk.

    :returns: cache cache, as constructed by the _add_to_lookup_cache method
    """
    cache_file = _get_cache_location()
    cache_data = {}

    try:
        fh = open(cache_file, "rb")
        try:
            cache_data = pickle.load(fh)
        finally:
            fh.close()
    except Exception as e:
        # failed to load cache from file. Continue silently.
        log.debug(
            "Failed to load lookup cache %s. Proceeding without cache. Error: %s"
            % (cache_file, e)
        )

    return cache_data


@filesystem.with_cleared_umask
def _add_to_lookup_cache(key, data):
    """
    Add a key to the lookup cache. This method will silently
    fail if the cache cannot be operated on.

    :param key: Dictionary key for the cache
    :param data: Data to associate with the dictionary key
    """

    # first load the content
    cache_data = _load_lookup_cache()
    # update
    cache_data[key] = data
    # and write out the cache
    cache_file = _get_cache_location()

    try:
        filesystem.ensure_folder_exists(os.path.dirname(cache_file))

        # write cache file
        fh = open(cache_file, "wb")
        try:
            pickle.dump(cache_data, fh)
        finally:
            fh.close()
        # and ensure the cache file has got open permissions
        os.chmod(cache_file, 0o666)

    except Exception as e:
        # silently continue in case exceptions are raised
        log.debug("Failed to add to lookup cache %s. Error: %s" % (cache_file, e))


def _get_cache_location():
    """
    Get the location of the initializtion lookup cache.
    Just computes the path, no I/O.

    :returns: A path on disk to the cache file
    """
    # optimized version of creating an sg instance and then calling sg.base_url
    # this is to avoid connecting to shotgun if possible.
    sg_base_url = shotgun.get_associated_sg_base_url()
    root_path = LocalFileStorageManager.get_site_root(
        sg_base_url, LocalFileStorageManager.CACHE
    )
    return os.path.join(root_path, constants.TOOLKIT_INIT_CACHE_FILE)
