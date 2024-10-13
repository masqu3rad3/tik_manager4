# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import copy

from .expression_tokens import SymlinkToken
from tank_vendor import six


class Folder(object):
    """
    Abstract Base class for all other folder classes.

    This object represents a configuration file in the folder
    creation hierarchy. It can be used to instantiate folders on disk,
    typically driven by some shotgun input data.
    """

    def __init__(self, parent, full_path, config_metadata):
        """
        :param parent: Parent :class:`Folder`
        :param full_path: Full path on disk to the associated configuration file.
        :param config_metadata: Resolved metadata for this configuration object.
        """
        self._config_metadata = config_metadata
        self._children = []
        self._full_path = full_path
        self._parent = parent
        self._files = []
        self._symlinks = []

        if self._parent:
            # add me to parent's child list
            self._parent._children.append(self)

    def __repr__(self):
        class_name = self.__class__.__name__
        return "<%s %s>" % (class_name, self._full_path)

    ###############################################################################################
    # public methods

    def is_dynamic(self):
        """
        Returns true if this folder node requires some sort of dynamic input
        """
        # assume all nodes are dynamic unless explicitly stated
        return True

    def get_path(self):
        """
        Returns the path on disk to this configuration item
        """
        return self._full_path

    def get_parent(self):
        """
        Returns the folder parent, none if no parent was defined
        """
        return self._parent

    def extract_shotgun_data_upwards(self, sg, shotgun_data):
        """
        Extract data from shotgun for a specific pathway upwards through the
        schema.

        This is subclassed by deriving classes which process Shotgun data.
        For more information, see the Entity implementation.

        :param sg: Shotgun API instance
        :param shotgun_data: Shotgun data dictionary. For more information,
                             see the Entity implementation.
        """
        if self._parent is None:
            return shotgun_data
        else:
            return self._parent.extract_shotgun_data_upwards(sg, shotgun_data)

    def get_parents(self):
        """
        Returns all parent nodes as a list with the top most item last in the list

        e.g. [ </foo/bar/baz>, </foo/bar>, </foo> ]
        """
        if self._parent is None:
            return []
        else:
            return [self._parent] + self._parent.get_parents()

    def add_file(self, path):
        """
        Adds a file name that should be added to this folder as part of processing.
        The file path should be absolute.

        :param path: absolute path to file
        """
        self._files.append(path)

    def add_symlink(self, name, target, metadata):
        """
        Adds a symlink definition to this node. As part of the processing phase, symlink
        targets will be resolved and created.

        :param name: name of the symlink
        :param target: symlink target expression
        :param metadata: full config yml metadata for symlink
        """
        # first split the target expression into chunks
        resolved_expression = [SymlinkToken(x) for x in target.split("/")]
        self._symlinks.append(
            {"name": name, "target": resolved_expression, "metadata": metadata}
        )

    def create_folders(
        self, io_receiver, path, sg_data, is_primary, explicit_child_list, engine
    ):
        """
        Recursive folder creation. Creates folders for this node and all its children.

        :param io_receiver: An object which handles any io processing request. Note that
                            processing may be deferred and happen after the recursion has completed.

        :param path: The file system path to the location where this folder should be
                     created.

        :param sg_data: All Shotgun data, organized in a dictionary, as returned by
                        extract_shotgun_data_upwards()

        :param is_primary: Indicates that the folder is part of the primary creation chain
                           and not part of the secondary recursion. For example, if the
                           folder creation is running for shot ABC, the primary chain
                           folders would be Project X -> Sequence Y -> Shot ABC.
                           The secondary folders would be the children of Shot ABC.

        :param explicit_child_list: A list of specific folders to process as the algorithm
                                    traverses down. Each time a new level is traversed, the child
                                    list is popped, and that object is processed. If the
                                    child list is empty, all children will be processed rather
                                    than the explicit object given at each level.

                                    This effectively means that folder creation often starts off
                                    using an explicit child list (for example project->sequence->shot)
                                    and then when the child list has been emptied (at the shot level),
                                    the recursion will switch to a creation mode where all Folder
                                    object children are processed.

        :param engine: String used to limit folder creation. If engine is not None, folder creation
                       traversal will include nodes that have their deferred flag set.

        :returns: Nothing
        """

        # should we create any folders?
        if not self._should_item_be_processed(engine, is_primary):
            return

        # run the actual folder creation
        created_data = self._create_folders_impl(io_receiver, path, sg_data)

        # and recurse down to children
        if explicit_child_list:

            # we have been given a specific list to recurse down.
            # pop off the next item and process it.
            explicit_ch = copy.copy(explicit_child_list)
            child_to_process = explicit_ch.pop()

            # before recursing down our specific recursion path, make sure all static content
            # has been created at this level in the folder structure
            static_children = [ch for ch in self._children if ch.is_dynamic() == False]

            for (created_folder, sg_data_dict) in created_data:

                # first process the static folders
                for cp in static_children:
                    # note! if the static child is on the specific recursion path,
                    # skip it, (we will create it below)
                    if cp == child_to_process:
                        continue

                    cp.create_folders(
                        io_receiver,
                        created_folder,
                        sg_data_dict,
                        is_primary=False,
                        explicit_child_list=[],
                        engine=engine,
                    )

                # and then recurse down our specific recursion path
                child_to_process.create_folders(
                    io_receiver,
                    created_folder,
                    sg_data_dict,
                    is_primary=True,
                    explicit_child_list=explicit_ch,
                    engine=engine,
                )

        else:
            # no explicit list! instead process all children.
            # run the folder creation for all new folders created and for all
            # configuration children
            for (created_folder, sg_data_dict) in created_data:
                for cp in self._children:
                    cp.create_folders(
                        io_receiver,
                        created_folder,
                        sg_data_dict,
                        is_primary=False,
                        explicit_child_list=[],
                        engine=engine,
                    )

    ###############################################################################################
    # private/protected methods

    def _create_folders_impl(self, io_receiver, parent_path, sg_data):
        """
        Folder creation implementation. Implemented by all subclasses.

        Should return a list of tuples. Each tuple is a path + a matching shotgun data dictionary
        """
        raise NotImplementedError

    def _should_item_be_processed(self, engine_str, is_primary):
        """
        Checks if this node should be processed, given its deferred status.

        If deriving classes have other logic for deciding if a node should be processed,
        this method can be subclassed. However, the base class should also be executed.

        Is Primary indicates that the folder is part of the primary creation pass.

        in the metadata, expect the following values:

        --                                    # no config parameter at all, means always create
        defer_creation:                       # no value specified, means create folders
        defer_creation: false                 # create folders
        defer_creation: true                  # create for all engine_str <> None
        defer_creation: tk-maya               # create if engine_str matches
        defer_creation: [tk-maya, tk-nuke]    # create if engine_str is in list

        :param engine_str: Engine or defer token for which folder creation is running. (see above)
        :param is_primary: If true, the folder is part of the primary creation pass.
        :returns: True if the item should be processed
        """
        dc_value = self._config_metadata.get("defer_creation")
        # if defer_creation config param not specified or None means we
        # can always go ahead with folder creation!!
        if dc_value is None or dc_value == False:
            # deferred value not specified means proceed with creation!
            return True

        # now handle the cases where the config specifies some sort of deferred behaviour
        # first of all, if the passed engine_str is None, we know we are NOT in deferred mode,
        # so shouldn't proceed.
        if engine_str is None:
            return False

        # now handle all cases where we have an engine_str and some sort of deferred behaviour.
        if dc_value == True:
            # defer create for all engine_strs!
            return True

        # multiple values can be provided in engine_str by delimiting them with a comma
        # (eg. 'tk-nuke, tk-myApp'). Split them and remove whitespace (eg. ['tk-nuke', 'tk-myApp'])
        # then check each one for a match. If *any* of them match then return True to process!
        engine_str_list = [x.strip() for x in engine_str.split(",")]
        for engine_str_val in engine_str_list:
            if isinstance(dc_value, six.string_types) and dc_value == engine_str_val:
                # defer_creation parameter is a string and this matches the engine_str_val!
                return True

            if isinstance(dc_value, list) and engine_str_val in dc_value:
                # defer_creation parameter is a list and the engine_str_val is contained in this list
                return True

        # for all other cases, no match!
        return False

    def _process_symlinks(self, io_receiver, path, sg_data):
        """
        Helper method.
        Resolves all symlinks and requests creation via the io_receiver object.

        :param io_receiver: IO handler instance
        :param path: Path where the symlinks should be located
        :param sg_data: std shotgun data collection for the current object
        """

        for symlink in self._symlinks:

            full_path = os.path.join(path, symlink["name"])

            # resolve our symlink from the target expressions
            # this will resolve any $project, $shot etc.
            # we get a list of strings representing resolved values for all levels of the symlink
            resolved_target_chunks = [
                x.resolve_token(self, sg_data) for x in symlink["target"]
            ]

            # and join them up into a path string
            resolved_target_path = os.path.sep.join(resolved_target_chunks)

            # register symlink with the IO receiver
            io_receiver.create_symlink(
                full_path, resolved_target_path, symlink["metadata"]
            )

    def _copy_files_to_folder(self, io_receiver, path):
        """
        Helper.
        Copies all files that have been registered with this folder object
        to a specific target folder on disk, using the dedicated hook.

        :param io_receiver: IO handler instance
        :param path: Path where the symlinks should be located
        """
        for src_file in self._files:
            target_path = os.path.join(path, os.path.basename(src_file))
            io_receiver.copy_file(src_file, target_path, self._config_metadata)
