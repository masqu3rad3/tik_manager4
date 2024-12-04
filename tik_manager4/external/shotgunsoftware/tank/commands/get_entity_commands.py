# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from .action_base import Action
from ..errors import TankError
from ..util.process import SubprocessCalledProcessError, subprocess_check_output
from ..util import is_linux, is_macos, is_windows

import itertools
import operator
import os
from tank_vendor.shotgun_api3.lib import sgsix


def execute_tank_command(pipeline_config_path, args):
    """
    Wrapper around execution of the tank command of a specified pipeline
    configuration.

    :raises: Will raise a SubprocessCalledProcessError if the tank command
             returns a non-zero error code.
             Will raise a TankError if the tank command could not be
             executed.
    :param pipeline_config_path: the path to the pipeline configuration that
                                 contains the tank command
    :param args:                 list of arguments to pass to the tank command
    :returns:                    text output of the command
    """
    if not os.path.isdir(pipeline_config_path):
        raise TankError(
            "Could not find the Pipeline Configuration on disk: %s"
            % pipeline_config_path
        )

    tank_command = "tank" if not is_windows() else "tank.bat"

    command_path = os.path.join(pipeline_config_path, tank_command)

    if not os.path.isfile(command_path):
        raise TankError("Could not find the tank command on disk: %s" % command_path)

    return subprocess_check_output([command_path] + args)


class GetEntityCommandsAction(Action):
    """
    Gets the commands that can be launched on certain entities for another
    pipeline configuration.

    This is done by calling the tank command on the other pipeline
    configuration and asking for its cached entity commands (or ask to update
    its cache beforehand if needed).

    It is used like this:
    >>> import tank
    # create our command object
    >>> cmd = tank.get_command("get_entity_commands")
    # get the commands for tasks, but could mix and match with any other types
    >>> tasks = [("Task", 1234), ("Task", 1235)]
    >>> commands_by_task = cmd.execute({"configuration_path": "/my/pc/path",
    >>>                                 "entities": tasks})
    # extract the commands of a specific task
    >>> commands = commands_by_task[tasks[0]]
    """

    # Error codes that can be returned by the toolkit command that gets invoked
    _ERROR_CODE_CACHE_OUT_OF_DATE = 1
    _ERROR_CODE_CACHE_NOT_FOUND = 2

    def __init__(self):
        Action.__init__(
            self,
            "get_entity_commands",
            Action.GLOBAL,
            (
                "Gets the available commands that can be executed "
                "for specified entities from another pipeline "
                "configuration"
            ),
            "API",
        )

        # no tank command support for this one because it returns an object
        self.supports_tank_command = False

        # this method can be executed via the API
        self.supports_api = True

        self.parameters = {
            "configuration_path": {
                "description": "Path to the pipeline configuration associated "
                "with the entities.",
                "type": "str",
            },
            "entities": {
                "description": "List of entities to fetch the actions for. "
                "Every entity should be a tuple with the "
                "following format:"
                "  (entity_type, entity_id)",
                "type": "list",
            },
            "return_value": {
                "description": """Dictionary of the commands by entity, with
                                  the (entity_type, entity_id) tuple used as a
                                  key. Each value is a list of commands. A
                                  command is a dictionary with the following
                                  format:
                                    {
                                      "name":        command to execute
                                      "title":       title to display for the
                                                     command
                                      "description": description of what the
                                                     command does
                                      "icon":        path to the icon of this
                                                     command
                                    }""",
                "type": "dict",
            },
        }

    def run_interactive(self, log, args):
        """
        Tank command accessor

        :param log: std python logger
        :param args: command line args
        """
        raise TankError("This Action does not support command line access")

    def run_noninteractive(self, log, parameters):
        """
        Tank command API accessor.
        Called when someone runs a tank command through the core API.

        :param log: std python logger
        :param parameters: dictionary with tank command parameters
        """
        pipeline_config_path = parameters["configuration_path"]
        entities = parameters["entities"]

        # at the moment, the caching mechanism works with the entity types,
        # so we group by type and fetch the commands for each type
        per_entity_type = itertools.groupby(entities, operator.itemgetter(0))

        commands_per_entity = {}
        for (entity_type, entities_of_type) in per_entity_type:
            # make a list out of the grouped entity tuples
            entities_of_type = list(entities_of_type)
            try:
                cache_content = self._load_cached_data(
                    pipeline_config_path, entity_type
                )
                commands = self._parse_cached_commands(cache_content)

                # at the moment, the commands are the same for all entities of
                # that type
                for entity in entities_of_type:
                    commands_per_entity[entity] = commands
            except TankError as e:
                log.error(
                    "Failed to fetch the commands from the Pipeline "
                    "Configuration at '%s' for the entity type %s.\n"
                    "Details: %s" % (pipeline_config_path, entity_type, e)
                )

        return commands_per_entity

    def _get_cache_name(self, platform, entity_type):
        """
        Constructs the expected name for the cache file of a particular entity
        type.

        :param platform:    platform that will use the cached information.
                            This string is expected to be of the same format as
                            sys.platform.
        :param entity_type: entity type that we want the cache for
        :returns:           name of the file containing the desired cached data
        """
        # get a platform name that follows the conventions of the shotgun cache
        platform_name = platform
        if is_macos(platform):
            platform_name = "mac"
        elif is_windows(platform):
            platform_name = "windows"
        elif is_linux(platform):
            platform_name = "linux"

        return ("shotgun_%s_%s.txt" % (platform_name, entity_type)).lower()

    def _get_env_name(self, entity_type):
        """
        Constructs the expected name for the environment file of a particular
        entity type. This environment file should contain the shotgun engine
        with the apps that will register the desired commands.

        :param entity_type: entity type that we want the environment for
        :returns:           name of the file with the desired environment
        """
        return "shotgun_%s.yml" % entity_type.lower()

    def _load_cached_data(self, pipeline_config_path, entity_type):
        """
        Loads the cached data for the given entities from the specified
        Pipeline Configuration.

        This is done by invoking the toolkit command of the other Pipeline
        Configuration to update the cache (if needed) and get the cache
        content.

        :raises:                     will raise a TankError if we were not able
                                     to update the cache or get its content
        :param pipeline_config_path: path to the Pipeline Configuration
                                     containing the cache that we want
        :param entity_type:          type of the entity we want the cache for
        :returns:                    text data contained in the cache
        """
        cache_name = self._get_cache_name(sgsix.platform, entity_type)
        env_name = self._get_env_name(entity_type)

        # try to load the data right away if it is already cached
        try:
            return execute_tank_command(
                pipeline_config_path, ["shotgun_get_actions", cache_name, env_name]
            )
        except SubprocessCalledProcessError as e:
            # failed to load from cache - only OK if cache is missing or out
            # of date
            if e.returncode not in [
                self._ERROR_CODE_CACHE_OUT_OF_DATE,
                self._ERROR_CODE_CACHE_NOT_FOUND,
            ]:
                raise TankError(
                    "Error while trying to get the cache content."
                    "\nDetails: %s\nOutput: %s" % (e, e.output)
                )

        # cache is not up to date - update it
        try:
            execute_tank_command(
                pipeline_config_path, ["shotgun_cache_actions", entity_type, cache_name]
            )
        except SubprocessCalledProcessError as e:
            # failed to update the cache
            raise TankError(
                "Failed to update the cache.\n"
                "Details: %s\nOutput: %s" % (e, e.output)
            )

        # now that the cache is updated, we can try to load the data again
        try:
            return execute_tank_command(
                pipeline_config_path, ["shotgun_get_actions", cache_name, env_name]
            )
        except SubprocessCalledProcessError as e:
            raise TankError(
                "Failed to get the content of the updated cache.\n"
                "Details: %s\nOutput: %s" % (e, e.output)
            )

    def _parse_cached_commands(self, commands_data):
        """
        Parses raw commands data into a structured list of dictionaries
        representing the available commands in the cache.

        :raises:              will raise a TankError if the cache does not
                              have the expected format
        :param commands_data: the raw text data contained in the cache
        :returns:             list of available commands that are in the
                              cache.
                              Every command is a dictionary with the
                              following format:
                                {
                                    "name":  unique name of the command
                                    "title": title to show for the command
                                    "description": description of what the
                                                   command does
                                    "icon":  path to the command's icon
                                }
        """
        lines = commands_data.splitlines()

        commands = []
        for line in lines:
            tokens = line.split("$")

            # make sure that we have at least some tokens in the cache
            if not tokens:
                raise TankError(
                    "The cache is badly formatted on the line "
                    "'%s'.\n"
                    "Full cache:\n%s" % (line, commands_data)
                )

            # max number of expected tokens
            # must match the size of the tuple extracted below
            NUM_EXPECTED_TOKENS = 6

            # pad the missing tokens with empty strings

            # this can happen if toolkit is updated to a new version that uses
            # new fields (i.e. new tokens) BUT the old caches are still there.
            # A call to clear the shotgun menu caches will then be required to
            # get the new fields.
            tokens += [""] * (NUM_EXPECTED_TOKENS - len(tokens))

            # extract the information from the tokens
            (name, title, _, _, icon, description) = tuple(tokens)

            commands.append(
                {"name": name, "title": title, "icon": icon, "description": description}
            )

        return commands
