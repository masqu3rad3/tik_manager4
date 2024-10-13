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
Utility methods related to folder creation
"""

import copy

from ...errors import TankError

from .expression_tokens import (
    FilterExpressionToken,
    CurrentStepExpressionToken,
    CurrentTaskExpressionToken,
)
from tank_vendor import six


def resolve_shotgun_filters(filters, sg_data):
    """
    Replace Token instances in the filters with a real value from the tokens dictionary.

    This method processes the filters dictionary and replaces tokens with data found
    in the tokens dictionary. It returns a resolved filter dictionary that can be passed to
    a shotgun query.
    """
    # TODO: Support nested conditions
    resolved_filters = copy.deepcopy(filters)
    for condition in resolved_filters["conditions"]:
        vals = condition["values"]

        if vals[0] and isinstance(vals[0], FilterExpressionToken):
            # we got a $filter! - replace with resolved value
            expr_token = vals[0]
            vals[0] = expr_token.resolve_shotgun_data(sg_data)

        if vals[0] and isinstance(vals[0], CurrentStepExpressionToken):
            # we got a current step filter! - replace with resolved value
            expr_token = vals[0]
            vals[0] = expr_token.resolve_shotgun_data(sg_data)

        if vals[0] and isinstance(vals[0], CurrentTaskExpressionToken):
            # we got a current task filter! - replace with resolved value
            expr_token = vals[0]
            vals[0] = expr_token.resolve_shotgun_data(sg_data)

    return resolved_filters


def translate_filter_tokens(filter_list, parent, yml_path):
    """
    Helper method to translate dynamic filter tokens into FilterExpressionTokens.

    For example - the following filter list:
    [ { "path": "project", "relation": "is", "values": [ "$project" ] } ]

    Will be translated to:

    { "logical_operator": "and",
      "conditions": [ { "path": "project",
                        "relation": "is",
                        "values": [ FilterExpressionTokens(project) ] }
                    ] }
    """

    resolved_filters = copy.deepcopy(filter_list)

    for sg_filter in resolved_filters:
        values = sg_filter["values"]
        new_values = []
        for filter_value in values:
            if isinstance(filter_value, six.string_types) and filter_value.startswith(
                "$"
            ):
                # this is a filter expression!
                try:
                    expr_token = FilterExpressionToken(filter_value, parent)
                except TankError as e:
                    # specialized message
                    raise TankError(
                        "Error resolving filter expression "
                        "%s in %s.yml: %s" % (filter_list, yml_path, e)
                    )
                new_values.append(expr_token)
            else:
                new_values.append(filter_value)

        sg_filter["values"] = new_values

    # add the wrapper around the list to make shotgun happy
    entity_filter = {}
    entity_filter["logical_operator"] = "and"
    entity_filter["conditions"] = resolved_filters

    return entity_filter
