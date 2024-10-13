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
Classes for the main Sgtk API.
"""

import os
import glob

from . import folder
from . import context
from .util import shotgun, yaml_cache
from .errors import TankError, TankMultipleMatchingTemplatesError
from .path_cache import PathCache
from .template import read_templates
from . import constants
from . import pipelineconfig
from . import pipelineconfig_utils
from . import pipelineconfig_factory
from . import LogManager
from tank_vendor import six
from tank_vendor.six.moves import zip

log = LogManager.get_logger(__name__)


class Sgtk(object):
    """
    The Toolkit Core API. Instances of this class are associated with a particular
    configuration and contain access methods for a number of low level
    Toolkit services such as filesystem creation, hooks, context
    manipulation and the Toolkit template system.
    """

    (DEFAULT, CENTRALIZED, DISTRIBUTED) = range(3)

    def __init__(self, project_path):
        """
        .. note:: Do not create this instance directly - Instead, instances of
            this class should be created using the methods :meth:`sgtk_from_path`,
            :meth:`sgtk_from_entity` or via the :class:`sgtk.bootstrap.ToolkitManager`.
            For more information, see :ref:`init_and_startup`.
        """
        # special stuff to make sure we maintain backwards compatibility in the constructor
        # if the 'project_path' parameter contains a pipeline config object,
        # just use this straight away. If the param contains a string, assume
        # this is a path and try to construct a pipeline config from the path

        if isinstance(project_path, pipelineconfig.PipelineConfiguration):
            # this is actually a pipeline config object
            self.__pipeline_config = project_path
        else:
            self.__pipeline_config = pipelineconfig_factory.from_path(project_path)

        # execute default_storage_root hook
        try:
            self.execute_core_hook_method(
                constants.DEFAULT_STORAGE_ROOT_HOOK_NAME,
                "execute",
                storage_roots=self.pipeline_configuration._storage_roots,
                project_id=self.pipeline_configuration.get_project_id(),
            )
        except Exception as e:
            # Catch errors to not kill our thread, log them for debug purpose.
            log.debug(
                "%s hook failed with %s" % (constants.DEFAULT_STORAGE_ROOT_HOOK_NAME, e)
            )

        try:
            self.__templates = read_templates(self.__pipeline_config)
        except TankError as e:
            raise TankError("Could not read templates configuration: %s" % e)

        # execute a tank_init hook for developers to use.
        self.execute_core_hook(constants.TANK_INIT_HOOK_NAME)

        # cache of local storages
        self.__cache = {}

    def __repr__(self):
        return "<Sgtk Core %s@0x%08x Config %s>" % (
            self.version,
            id(self),
            self.__pipeline_config.get_path(),
        )

    def __str__(self):
        return "Sgtk Core %s, config %s" % (
            self.version,
            self.__pipeline_config.get_path(),
        )

    ################################################################################################
    # internal API

    @property
    def pipeline_configuration(self):
        """
        Internal Use Only - We provide no guarantees that this method
        will be backwards compatible. The returned objects are also
        subject to change and are not part of the public Sgtk API.
        """
        return self.__pipeline_config

    def execute_core_hook(self, hook_name, **kwargs):
        """
        Executes a core level hook, passing it any keyword arguments supplied.

        Internal Use Only - We provide no guarantees that this method
        will be backwards compatible.

        :param hook_name: Name of hook to execute.
        :param kwargs:  Additional named parameters will be passed to the hook.
        :returns:         Return value of the hook.
        """
        return self.pipeline_configuration.execute_core_hook_internal(
            hook_name, parent=self, **kwargs
        )

    # compatibility alias - previously the name of this *internal method* was named execute_hook.
    # in order to try to avoid breaking client code that uses these *internal methods*, let's
    # provide a backwards compatibility alias.
    execute_hook = execute_core_hook

    def execute_core_hook_method(self, hook_name, method_name, **kwargs):
        """
        Executes a specific method on a core level hook,
        passing it any keyword arguments supplied.

        Internal Use Only - We provide no guarantees that this method
        will be backwards compatible.

        :param hook_name:   Name of hook to execute.
        :param method_name: Name of method to execute.
        :param **kwargs:    Additional named parameters will be passed to the hook.
        :returns:           Return value of the hook.
        """
        return self.pipeline_configuration.execute_core_hook_method_internal(
            hook_name, method_name, parent=self, **kwargs
        )

    def log_metric(self, action, log_once=False):
        """
        This method is now deprecated and shouldn't be used anymore.
        Use the `tank.util.metrics.EventMetrics.log` method instead.
        """
        pass

    def get_cache_item(self, cache_key):
        """
        Returns an item from the cache held within this tk instance.

        Internal Use Only - We provide no guarantees that this method
        will be backwards compatible.

        :param str cache_key: name of cache key to access
        :return: cached object or None if no object found
        """
        return self.__cache.get(cache_key)

    def set_cache_item(self, cache_key, value):
        """
        Adds a value to the tk instance cache. To clear a value,
        set it to None.

        Internal Use Only - We provide no guarantees that this method
        will be backwards compatible.

        :param str cache_key: name of cache key to set
        :param value: Value to set or None to clear it.
        """
        self.__cache[cache_key] = value

    ################################################################################################
    # properties

    @property
    def configuration_descriptor(self):
        """
        The :class:`~sgtk.descriptor.ConfigDescriptor` which represents the
        source of the environments associated with this pipeline configuration.
        """
        return self.__pipeline_config.get_configuration_descriptor()

    @property
    def bundle_cache_fallback_paths(self):
        """
        List of paths to the fallback bundle caches for the pipeline configuration.
        """
        return self.__pipeline_config.get_bundle_cache_fallback_paths()

    @property
    def project_path(self):
        """
        Path to the default data directory for a project.

        Toolkit Projects that utilize the template system to read and write data
        to disk will use a number of Shotgun local storages as part of their
        setup to define where data should be stored on disk. One of these
        storages is identified as the default storage.

        :raises: :class:`TankError` if the configuration doesn't use storages.
        """
        return self.__pipeline_config.get_primary_data_root()

    @property
    def roots(self):
        """
        Returns a dictionary of storage root names to storage root paths.

        Toolkit Projects that utilize the template system to read and write data
        to disk will use one or more Shotgun local storages as part of their
        setup to define where data should be stored on disk. This method returns
        a dictionary keyed by storage root name with the value being the path
        on the current operating system platform::

            {
                "work": "/studio/work/my_project",
                "textures": "/studio/textures/my_project"
            }

        These items reflect the Local Storages that you have set up in Shotgun.

        Each project using the template system is connected to a number of these
        storages - these storages define the root points for all the different
        data locations for your project. So for example, if you have a mount
        point for textures, one for renders and one for production data such
        as scene files, you can set up a multi root configuration which uses
        three Local Storages in Shotgun. This method returns the project
        storage locations for the current project. The key is the name of the
        local storage as defined in your configuration. The value is the path
        which is defined in the associated Shotgun Local storage definition for
        the current operating system, concatenated with the project folder name.
        """
        return self.__pipeline_config.get_data_roots()

    @property
    def shotgun_url(self):
        """
        The associated shotgun url, e.g. ``https://mysite.shotgunstudio.com``
        """
        return shotgun.get_associated_sg_base_url()

    @property
    def shotgun(self):
        """
        Just-in-time access to a per-thread Shotgun API instance.

        This Shotgun API is threadlocal, meaning that each thread will get
        a separate instance of the Shotgun API. This is in order to prevent
        concurrency issues and add a layer of basic protection around the
        Shotgun API, which isn't threadsafe.
        """
        sg = shotgun.get_sg_connection()

        # pass on information to the user agent manager which core version is returning
        # this sg handle. This information will be passed to the web server logs
        # in the shotgun data centre and makes it easy to track which core versions
        # are being used by clients
        try:
            sg.tk_user_agent_handler.set_current_core(self.version)
        except AttributeError:
            # looks like this sg instance for some reason does not have a
            # tk user agent handler associated.
            pass

        return sg

    @property
    def version(self):
        """
        The version of the tank Core API (e.g. v0.2.3)
        """
        return pipelineconfig_utils.get_currently_running_api_version()

    @property
    def documentation_url(self):
        """
        A url pointing at relevant documentation for this version of the Toolkit Core
        or None if no documentation is associated.
        """
        # read this from info.yml
        info_yml_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "info.yml")
        )
        try:
            data = yaml_cache.g_yaml_cache.get(info_yml_path, deepcopy_data=False)
            data = str(data.get("documentation_url"))
            if data == "":
                data = None
        except Exception:
            data = None

        return data

    @property
    def configuration_mode(self):
        """
        The mode of the currently running configuration:

        - ``sgtk.CENTRALIZED`` if the configuration is part of a
          :ref:`centralized<centralized_configurations>` setup.
        - ``sgtk.DISTRIBUTED`` if the configuration is part of a
          :ref:`distributed<distributed_configurations>` setup.
        - ``sgtk.DEFAULT`` if the configuration does not have an associated pipeline
          pipeline configuration but is falling back to its default builtins.
        """
        if self.configuration_id is None:
            return self.DEFAULT
        # any pipeline configuration which has the linux_path/windows_path or mac_path
        # populated are defined as a centralized configuration
        sg_data = self.shotgun.find_one(
            "PipelineConfiguration",
            [["id", "is", self.configuration_id]],
            ["windows_path", "mac_path", "linux_path"],
        )
        if sg_data["windows_path"] or sg_data["mac_path"] or sg_data["linux_path"]:
            return self.CENTRALIZED
        else:
            return self.DISTRIBUTED

    @property
    def configuration_name(self):
        """
        The name of the currently running Shotgun Pipeline
        Configuration, e.g. ``Primary``.
        If the current session does not have an associated
        pipeline configuration in Shotgun (for example
        because you are running the built-in integrations),
        ``None`` will be returned.
        """
        return self.__pipeline_config.get_name()

    @property
    def configuration_id(self):
        """
        The associated Shotgun pipeline configuration id.
        If the current session does not have an associated
        pipeline configuration in Shotgun (for example
        because you are running the built-in integrations),
        ``None`` will be returned.
        """
        return self.__pipeline_config.get_shotgun_id()

    @property
    def templates(self):
        """
        A dictionary, where the keys are the template names, and the values
        are :class:`~sgtk.Template` instances representing the tokenized paths, as defined in
        the configuration's ``templates.yml``.

        :return: :class:`dict`
        """
        # defined as a getter setter so that we could document it properly
        return self.__templates

    @templates.setter
    def templates(self, value):
        """
        Allows setting the templates property.
        You shouldn't set the templates property from out side of the api module.
        However this was implemented when changing the instance variable to a property so as
        to not change the interface.
        """
        self.__templates = value

    ##########################################################################################
    # public methods

    def reload_templates(self):
        """
        Reloads the template definitions from disk. If the reload fails a
        :class:`TankError` will be raised and the previous template definitions
        will be preserved.

        .. note:: This method can be helpful if you are tweaking
                 templates inside of for example Maya and want to reload them. You can
                 then access this method from the python console via the current engine
                 handle::

                    sgtk.platform.current_engine().sgtk.reload_templates()

        :raises: :class:`TankError`
        """
        try:
            self.__templates = read_templates(self.__pipeline_config)
        except TankError as e:
            raise TankError("Templates could not be reloaded: %s" % e)

    def list_commands(self):
        """
        Lists the system commands registered with the system.

        This method will return all system commands which
        are available in the context of a project configuration will be returned.
        This includes for example commands for configuration management,
        anything app or engine related and validation and overview functionality.
        In addition to these commands, the global commands such as project setup
        and core API check commands will also be returned.

        For more information, see :meth:`sgtk.list_commands`

        :returns: list of command names
        """
        # avoid cyclic dependencies
        from . import commands

        return commands.list_commands(self)

    def get_command(self, command_name):
        """
        Returns an instance of a command object that can be used to execute a command.

        Once you have retrieved the command instance, you can perform introspection to
        check for example the required parameters for the command, name, description etc.
        Lastly, you can execute the command by running the execute() method.

        In order to get a list of the available commands, use the list_commands() method.

        For more information, see :meth:`sgtk.get_command`

        :param command_name: Name of command to execute. Get a list of all available commands
                             using the :meth:`list_commands` method.

        :returns: :class:`~sgtk.SgtkSystemCommand` object instance
        """
        # avoid cyclic dependencies
        from . import commands

        return commands.get_command(command_name, self)

    def templates_from_path(self, path):
        """
        Finds templates that matches the given path::

            >>> import sgtk
            >>> tk = sgtk.sgtk_from_path("/studio/project_root")
            >>> tk.templates_from_path("/studio/my_proj/assets/Car/Anim/work")
            <Sgtk Template maya_asset_project: assets/%(Asset)s/%(Step)s/work>


        :param path: Path to match against a template
        :returns: list of :class:`TemplatePath` or [] if no match could be found.
        """
        matched_templates = []
        for key, template in self.templates.items():
            if template.validate(path):
                matched_templates.append(template)
        return matched_templates

    def template_from_path(self, path):
        """
        Finds a template that matches the given path::

            >>> import sgtk
            >>> tk = sgtk.sgtk_from_path("/studio/project_root")
            >>> tk.template_from_path("/studio/my_proj/assets/Car/Anim/work")
            <Sgtk Template maya_asset_project: assets/%(Asset)s/%(Step)s/work>


        :param path: Path to match against a template
        :returns: :class:`TemplatePath` or None if no match could be found.
        """
        matched_templates = self.templates_from_path(path)

        if len(matched_templates) == 0:
            return None
        elif len(matched_templates) == 1:
            return matched_templates[0]
        else:
            # ambiguity!
            # We're erroring out anyway, take the time to create helpful debug info!
            matched_fields = []
            for template in matched_templates:
                matched_fields.append(template.get_fields(path))

            msg = "%d templates are matching the path '%s'.\n" % (
                len(matched_templates),
                path,
            )
            msg += "The overlapping templates are:\n"
            for fields, template in zip(matched_fields, matched_templates):
                msg += "%s\n%s\n" % (template, fields)
            raise TankMultipleMatchingTemplatesError(msg)

    def paths_from_template(
        self, template, fields, skip_keys=None, skip_missing_optional_keys=False
    ):
        """
        Finds paths that match a template using field values passed.

        This is useful if you want to get a list of files matching a particular
        template and set of fields. One common pattern is when you are dealing
        with versions, and you want to retrieve all the different versions for a
        file. In that case just resolve all the fields for the file you want to operate
        on, then pass those in to the paths_from_template() method. By passing version to
        the ``skip_keys`` parameter, the method will return all the versions associated
        with your original file.

        Any keys that are required by the template but aren't included in the fields
        dictionary are always skipped. Any optional keys that aren't included are only
        skipped if the ``skip_missing_optional_keys`` parameter is set to True.

        If an optional key is to be skipped, all matching paths that contain a value for
        that key as well as those that don't will be included in the result.

        .. note:: The result is not ordered in any particular way.

        Imagine you have a template ``maya_work: sequences/{Sequence}/{Shot}/work/{name}.v{version}.ma``::

            >>> import sgtk
            >>> tk = sgtk.sgtk_from_path("/studio/my_proj")
            >>> maya_work = tk.templates["maya_work"]

        All fields that you don't specify will be searched for. So if we want to search for all
        names and versions for a particular sequence and shot, we can do::

            >>> tk.paths_from_template(maya_work, {"Sequence": "AAA", "Shot": "001"})
            /studio/my_proj/sequences/AAA/001/work/background.v001.ma
            /studio/my_proj/sequences/AAA/001/work/background.v002.ma
            /studio/my_proj/sequences/AAA/001/work/background.v003.ma
            /studio/my_proj/sequences/AAA/001/work/mainscene.v001.ma
            /studio/my_proj/sequences/AAA/001/work/mainscene.v002.ma
            /studio/my_proj/sequences/AAA/001/work/mainscene.v003.ma

        :param template: Template against whom to match.
        :type  template: :class:`TemplatePath`
        :param fields: Fields and values to use.
        :type  fields: Dictionary
        :param skip_keys: Keys whose values should be ignored from the fields parameter.
        :type  skip_keys: List of key names
        :param skip_missing_optional_keys: Specify if optional keys should be skipped if they
                                        aren't found in the fields collection
        :returns: Matching file paths
        :rtype: List of strings.
        """
        skip_keys = skip_keys or []
        if isinstance(skip_keys, six.string_types):
            skip_keys = [skip_keys]

        # construct local fields dictionary that doesn't include any skip keys:
        local_fields = dict(
            (field, fields[field]) for field in fields if field not in skip_keys
        )

        # we always want to automatically skip 'required' keys that weren't
        # specified so add wildcards for them to the local fields
        for key in template.missing_keys(local_fields):
            if key not in skip_keys:
                skip_keys.append(key)
            local_fields[key] = "*"

        # iterate for each set of keys in the template:
        found_files = set()
        globs_searched = set()
        for keys in template._keys:
            # create fields and skip keys with those that
            # are relevant for this key set:
            current_local_fields = local_fields.copy()
            current_skip_keys = []
            for key in skip_keys:
                if key in keys:
                    current_skip_keys.append(key)
                    current_local_fields[key] = "*"

            # find remaining missing keys - these will all be optional keys:
            missing_optional_keys = template._missing_keys(
                current_local_fields, keys, False
            )
            if missing_optional_keys:
                if skip_missing_optional_keys:
                    # Add wildcard for each optional key missing from the input fields
                    for missing_key in missing_optional_keys:
                        current_local_fields[missing_key] = "*"
                        current_skip_keys.append(missing_key)
                else:
                    # if there are missing fields then we won't be able to
                    # form a valid path from them so skip this key set
                    continue

            # Apply the fields to build the glob string to search with. We are iterating
            # through all the possible key combinations that do and do not include the
            # optional keys so we need _apply_fields to skip defaults otherwise if an
            # optional key has a default value, we will never find files that don't include
            # the optional key in their file name
            glob_str = template._apply_fields(
                current_local_fields, ignore_types=current_skip_keys, skip_defaults=True
            )
            if glob_str in globs_searched:
                # it's possible that multiple key sets return the same search
                # string depending on the fields and skip-keys passed in
                continue
            globs_searched.add(glob_str)

            # Find all files which are valid for this key set
            found_files.update(
                [
                    found_file
                    for found_file in glob.iglob(glob_str)
                    if template.validate(found_file)
                ]
            )

        return list(found_files)

    def abstract_paths_from_template(self, template, fields):
        """
        Returns an abstract path based on a template.

        Similar to :meth:`paths_from_template`, but optimized for abstract fields
        such as image sequences and stereo patterns.

        An *abstract field* is for example an image sequence pattern
        token, such as ``%04d``, ``%V`` or ``@@@@@``. This token represents
        a large collection of files. This method will return abstract fields whenever
        it can, and it will attempt to optimize the calls based on abstract
        pattern matching, trying to avoid doing a thousand file lookups for a
        thousand frames in a sequence.

        It works exactly like :meth:`paths_from_template` with the difference
        that any field marked as abstract in the configuration will use its
        default value rather than any matched file values. Sequence
        fields are abstract by default.

        .. note:: The result is not ordered in any particular way.

        Imagine you have a template ``render: sequences/{Sequence}/{Shot}/images/{eye}/{name}.{SEQ}.exr``::

            >>> import sgtk
            >>> tk = sgtk.sgtk_from_path("/studio/my_proj")
            >>> render = tk.templates["render"]

        All fields that you don't specify will be searched for. So if we want to search for all
        names and versions for a particular sequence and shot, we can do::

            >>> tk.abstract_paths_from_template(maya_work, {"Sequence": "AAA", "Shot": "001"})
            /studio/my_proj/sequences/AAA/001/images/%V/render_1.%04d.exr
            /studio/my_proj/sequences/AAA/001/images/%V/render_2.%04d.exr
            /studio/my_proj/sequences/AAA/001/images/%V/render_3.%04d.exr

        .. note:: There are situations where the resulting abstract paths may not match any files on disk

        Take the following template::

            render: sequences/{Sequence}/{Shot}/images/{Shot}.{SEQ}.jpg

        Assuming ``Shot`` is provided via the ``fields`` argument, the method will avoid
        listing all files in the leaf directory since ``{SEQ}`` is abstract and ``{Shot}``
        is known. The following abstract path will be returned even if only the
        parent ``images`` directory exists::

            /studio/my_proj/sequences/AAA/001/images/001.%04d.exr

        :param template: Template with which to search
        :type  template: :class:`TemplatePath`
        :param fields: Mapping of keys to values with which to assemble the abstract path.
        :type fields: dictionary

        :returns: A list of paths whose abstract keys use their abstract(default) value unless
                  a value is specified for them in the fields parameter.
        """
        search_template = template

        # the logic is as follows:
        # do a glob and collapse abstract fields down into their abstract patterns
        # unless they are specified with values in the fields dictionary
        #
        # if the leaf level can be avoided, do so.
        # the leaf level can be avoided if it contains
        # a combination of non-abstract templates with values in the fields dict
        # and abstract templates.

        # can we avoid the leaf level?
        leaf_keys = set(template.keys.keys()) - set(template.parent.keys.keys())

        abstract_key_names = [k.name for k in template.keys.values() if k.is_abstract]

        skip_leaf_level = True
        for k in leaf_keys:
            if k not in abstract_key_names:
                # a non-abstract key
                if k not in fields:
                    # with no value
                    skip_leaf_level = False
                    break

        if skip_leaf_level:
            search_template = template.parent

        # now carry out a regular search based on the template
        found_files = self.paths_from_template(search_template, fields)

        st_abstract_key_names = [
            k.name for k in search_template.keys.values() if k.is_abstract
        ]

        # now collapse down the search matches for any abstract fields,
        # and add the leaf level if necessary
        abstract_paths = set()
        for found_file in found_files:

            cur_fields = search_template.get_fields(found_file)

            # pass 1 - go through the fields for this file and
            # zero out the abstract fields - this way, apply
            # fields will pick up defaults for those fields
            #
            # if the system found matches for eye=left and eye=right,
            # by deleting all eye values they will be replaced by %V
            # as the template is applied.
            #
            for abstract_key_name in st_abstract_key_names:
                del cur_fields[abstract_key_name]

            # pass 2 - if we ignored the leaf level, add those fields back
            # note that there is no risk that we add abstract fields at this point
            # since the fields dictionary should only ever contain "real" values.
            # also, we may have deleted actual fields in the pass above and now we
            # want to put them back again.
            for f in fields:
                if f not in cur_fields:
                    cur_fields[f] = fields[f]

            # now we have all the fields we need to compose the full template
            abstract_path = template.apply_fields(cur_fields)
            abstract_paths.add(abstract_path)

        return list(abstract_paths)

    def paths_from_entity(self, entity_type, entity_id):
        """
        Finds paths associated with a Shotgun entity.

        .. note:: Only paths that have been generated by :meth:`create_filesystem_structure` will
                 be returned. Such paths are stored in Shotgun as ``FilesystemLocation`` entities.

        :param entity_type: a Shotgun entity type
        :param entity_id: a Shotgun entity id
        :returns: Matching file paths
        :rtype: List of strings.
        """

        # Use the path cache to look up all paths associated with this entity
        path_cache = PathCache(self)
        paths = path_cache.get_paths(entity_type, entity_id, primary_only=True)
        path_cache.close()

        return paths

    def entity_from_path(self, path):
        """
        Returns the shotgun entity associated with a path.

        .. note:: Only paths that have been generated by :meth:`create_filesystem_structure` will
                 be returned. Such paths are stored in Shotgun as ``FilesystemLocation`` entities.

        :param path: A path to a folder or file
        :returns: Shotgun dictionary containing name, type and id or None
                  if no path was associated.
        """
        # Use the path cache to look up all paths associated with this entity
        path_cache = PathCache(self)
        entity = path_cache.get_entity(path)
        path_cache.close()

        return entity

    def context_empty(self):
        """
        Factory method that constructs an empty Context object.

        :returns: :class:`Context`
        """
        return context.create_empty(self)

    def context_from_path(self, path, previous_context=None):
        """
        Factory method that constructs a context object from a path on disk.

        .. note:: If you're running this method on a render farm or on a machine where the
                  path cache may not have already been generated then you will need to run
                  :meth:`synchronize_filesystem_structure` beforehand, otherwise you will
                  get back a context only containing the shotgun site URL.

        :param path: a file system path
        :param previous_context: A context object to use to try to automatically extend the generated
                                 context if it is incomplete when extracted from the path. For example,
                                 the Task may be carried across from the previous context if it is
                                 suitable and if the task wasn't already expressed in the file system
                                 path passed in via the path argument.
        :type previous_context: :class:`Context`
        :returns: :class:`Context`
        """
        return context.from_path(self, path, previous_context)

    def context_from_entity(self, entity_type, entity_id):
        """
        Factory method that constructs a context object from a Shotgun entity.

        :param entity_type: The name of the entity type.
        :param entity_id: Shotgun id of the entity upon which to base the context.
        :returns: :class:`Context`
        """
        return context.from_entity(self, entity_type, entity_id)

    def context_from_entity_dictionary(self, entity_dictionary):
        """
        Derives a context from a shotgun entity dictionary. This will try to use any
        linked information available in the dictionary where possible but if it can't
        determine a valid context then it will fall back to :meth:`context_from_entity` which
        may result in a Shotgun path cache query and be considerably slower.

        The following values for ``entity_dictionary`` will result in a context being
        created without falling back to a potential Shotgun query - each entity in the
        dictionary (including linked entities) must have the fields: 'type', 'id' and
        'name' (or the name equivalent for specific entity types, e.g. 'content' for
        Step entities, 'code' for Shot entities, etc.)::

            {"type": "Project", "id": 123, "name": "My Project"}

            {"type": "Shot", "id": 456, "code": "Shot 001",
             "project": {"type": "Project", "id": 123, "name": "My Project"}
            }

            {"type": "Task", "id": 789, "content": "Animation",
             "project": {"type": "Project", "id": 123, "name": "My Project"}
             "entity": {"type": "Shot", "id": 456, "name": "Shot 001"}
             "step": {"type": "Step", "id": 101112, "name": "Anm"}
            }

            {"type": "PublishedFile", "id": 42, "code": "asset.ma",
             "task": {type": "Task", "id": 789, "content": "Animation"}
             "project": {"type": "Project", "id": 123, "name": "My Project"}
             "entity": {"type": "Shot", "id": 456, "name": "Shot 001"}
            }

        The following values for ``entity_dictionary`` don't contain enough information to
        fully form a context so the code will fall back to :meth:`context_from_entity` which
        may then result in a Shotgun query to retrieve the missing information::

            # missing project name
            {"type": "Project", "id": 123}

            # missing linked project
            {"type": "Shot", "id": 456, "code": "Shot 001"}

            # missing linked project name and linked step
            {"type": "Task", "id": 789, "content": "Animation",
             "project": {"type": "Project", "id": 123}}
             "entity": {"type": "Shot", "id": 456, "name": "Shot 001"}
            }

            # Missing publish name.
            {"type": "PublishedFile", "id": 42,
             "task": {type": "Task", "id": 789, "content": "Animation"}
             "project": {"type": "Project", "id": 123, "name": "My Project"}
             "entity": {"type": "Shot", "id": 456, "name": "Shot 001"}
            }

        :param entity_dictionary:   A Shotgun entity dictionary containing at least 'type'
                                    and 'id'. See examples above.
        :returns: :class:`Context`
        """
        return context.from_entity_dictionary(self, entity_dictionary)

    def synchronize_filesystem_structure(self, full_sync=False):
        """
        Ensures that the filesystem structure on this machine is in sync
        with Shotgun. This synchronization is implicitly carried out as part of the
        normal folder creation process, however sometimes it is useful to
        be able to call it on its own.

        .. note:: That this method is equivalent to the **synchronize_folders** tank command.

        :param full_sync: If set to true, a complete sync will be carried out.
                          By default, the sync is incremental.
        :returns: List of folders that were synchronized.
        """
        return folder.synchronize_folders(self, full_sync)

    def create_filesystem_structure(self, entity_type, entity_id, engine=None):
        """
        Create folders and associated data on disk to reflect branches in the project
        tree related to a specific entity.

        It is possible to set up folder creation so that it happens in two passes -
        a primary pass and a deferred pass. Typically, the primary pass is used to
        create the high level folder structure and the deferred is executed just before
        launching an application environment. It can be used to create application specific
        folders or to create a user workspace based on the user launching the application. By
        setting the optional engine parameter to a string value (typically the engine name, for
        example ``tk-maya``) you can indicate to the system that it should trigger the deferred
        pass and recurse down in the part of the configuration that has been marked as being
        deferred in the configuration.

        Note that this is just a string following a convention - typically, we recommend
        that an engine name (e.g. 'tk-nuke') is passed in, however all this method is doing
        is to relay this string on to the folder creation (schema) setup so that it is
        compared with any deferred entries there. In case of a match, the folder creation
        will recurse down into the subtree marked as deferred.

        :param entity_type: Shotgun entity type
        :param entity_id: Shotgun id
        :param engine: Optional engine name to indicate that a second, engine specific
                       folder creation pass should be executed for a particular engine.
        :returns: The number of folders processed
        """
        folders = folder.process_filesystem_structure(
            self, entity_type, entity_id, False, engine
        )
        return len(folders)

    def preview_filesystem_structure(self, entity_type, entity_id, engine=None):
        """
        Previews folders that would be created by :meth:`create_filesystem_structure`.

        :param entity_type: Shotgun entity type
        :param entity_id: Shotgun id
        :param engine: Optional engine name to indicate that a second, engine specific
                       folder creation pass should be executed for a particular engine.
        :type engine: String.
        :returns: List of paths that would be created
        """
        folders = folder.process_filesystem_structure(
            self, entity_type, entity_id, True, engine
        )
        return folders


##########################################################################################
# module methods


def sgtk_from_path(path):
    """
    Creates a Toolkit Core API instance based on a path to a configuration
    or a path to any file inside a project root location. This factory
    method will do the following two things:

    **When the path points at a configuration**

    If the given path is determined to be pointing at a pipeline configuration,
    checks will be made to determine that the currently imported ``sgtk`` module
    is the same version that the configuration requires.

    **When the path points at a project file**

    If the given path is to a file (e.g. a maya file for example), the method will
    retrieve all projects from Shotgun, including their ``Project.tank_name``
    project root folder fields and associated pipeline configurations. It will then
    walk up the path hierarchy of the given path until one of the project roots are
    matching the path. For that project, all pipeline configurations are then retrieved.

    .. note:: If more than one configuration is matching, the
              primary one will take precendence.

    **Shared cores and localized cores**

    If you have a shared core for all your projects, you can follow a pattern where
    you add this shared core to the ``PYTHONPATH`` and you can launch Toolkit for any
    project file on disk (or Shotgun entity) on your entire site easily::

        # add the shared core to the pythonpath
        import sys
        sys.path.append("/mnt/toolkit/shared_core")

        # now import the API
        import sgtk

        # request that the API produced a tk instance suitable for a given file
        tk = sgtk.sgtk_from_path("/mnt/projects/hidden_forest/shots/aa/aa_001/lighting/foreground.v002.ma")

    .. note:: The :ref:`bootstrap_api` is now the recommended solution
              for building a pattern that can launch an engine for any given entity on a site.

    :param path: Path to pipeline configuration or to a folder associated with a project.
    :returns: :class:`Sgtk` instance
    """
    return Tank(path)


def sgtk_from_entity(entity_type, entity_id):
    """
    Creates a Toolkit Core API instance given an entity in Shotgun.

    The given object will be looked up in Shotgun, its associated pipeline configurations
    will be determined, and compared against the currently imported :class:`sgtk` module.
    The logic is identical to the one outlined in :meth:`sgtk_from_path`, but for
    a Shotgun entity rather than a path. For more details, see :meth:`sgtk_from_path`.

    :param entity_type: Shotgun entity type, e.g. ``Shot``
    :param entity_id: Shotgun entity id
    :returns: :class:`Sgtk` instance
    """
    pc = pipelineconfig_factory.from_entity(entity_type, entity_id)
    return Tank(pc)


_authenticated_user = None


def set_authenticated_user(user):
    """
    Sets the currently authenticated Shotgun user for the current toolkit session.

    You instruct the Toolkit API which user the current session is associated with by executing
    this command. Conversely, you can use :meth:`get_authenticated_user` to retrieve the current user.
    The user object above is created by the ``sgtk.authentication`` part of the API and wraps around the Shotgun
    API to provide a continuous and configurable experience around user based Shotgun connections.

    Normally, Toolkit handles this transparently as part of setting up the `sgtk` instance and there is no need
    to call this method. However, if you are running a custom tool which has particular requirements
    around authentication, you can provide your own logic if desirable.

    :param user: A :class:`~sgtk.authentication.ShotgunUser` derived object. Can
                 be None to clear the authenticated user.
    """
    global _authenticated_user
    _authenticated_user = user


def get_authenticated_user():
    """
    Returns the Shotgun user associated with Toolkit.

    :returns: A :class:`~sgtk.authentication.ShotgunUser` derived object if set,
        None otherwise.
    """
    global _authenticated_user
    return _authenticated_user


##########################################################################################
# Legacy handling


def tank_from_path(path):
    """
    Legacy alias for :meth:`sgtk_from_path`.
    """
    return sgtk_from_path(path)


def tank_from_entity(entity_type, entity_id):
    """
    Legacy alias for :meth:`sgtk_from_entity`.
    """
    return sgtk_from_entity(entity_type, entity_id)


class Tank(Sgtk):
    """
    Legacy alias for :class:`Sgtk`
    """
