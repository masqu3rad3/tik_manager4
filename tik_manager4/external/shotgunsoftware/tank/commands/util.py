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
Utility methods that are specific to tank commands
"""

from . import constants


def should_use_legacy_yaml_parser(args):
    """
    Given a set of command line args, determine if the
    legacy yaml parser should be used.

    :param args: list of arg strings
    :returns: (use_legacy, adjusted_args) - tuple with bool to indicate
              if the legacy parser should be used and a list of args where
              the legacy flag has been removed.
    """
    # look for a legacy parser flag
    if constants.LEGACY_YAML_PARSER_FLAG in args:
        legacy_parser = True
        args.remove(constants.LEGACY_YAML_PARSER_FLAG)
    else:
        legacy_parser = False

    return (legacy_parser, args)
