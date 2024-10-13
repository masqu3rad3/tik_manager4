# Copyright (c) 2023 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
The Metrics logger thread is only launched once an engine is initialized.
But we might want to log metrics event before Toolkit is fully initialized.

For instance, when starting the PTR desktop app and authenticating, there is no
engine set yet.

This module provide a cache that can be filled prior to Toolkit initilization.
Then, once the engine is set and the metric thread starts, the cache is consumed
and send the items to the Metric instance.

Unfortunatly, this cache can not live in a singleton in this module because,
somehow, tk-core is fully unloaded off the python process between authentication
and launch of an engine (desktopstartup).
Instead, we store the records in the environment as JSON text
"""

import hashlib
import os

from . import json
from . import metrics

from .. import LogManager

logger = LogManager.get_logger(__name__)


def log(group, name, properties=None, log_once=False, bundle=None):
    """
    Same prototype as the log method from the metrics module.
    """

    args = (group, name)
    kwargs = {}
    if properties is not None:
        kwargs["properties"] = properties
    if log_once is not False:
        kwargs["log_once"] = log_once
    if bundle is not None:
        kwargs["bundle"] = bundle

    # import here to prevent circular dependency
    from ..platform.engine import current_engine

    if current_engine():
        # We don't need to cache in this situation, Let's simply forward the
        # order
        return metrics.EventMetric.log(*args, **kwargs)

    try:
        cached_data = json.json.dumps([args, kwargs])
    except TypeError:
        logger.debug("Unable to cache metric. Can not be JSON encoded")
        return

    cache_key = "sgtk_metric_cache_{cid}".format(
        cid=hashlib.sha1(cached_data.encode()).hexdigest()[:16],
    )

    os.environ[cache_key] = cached_data


def consume():
    """
    Iterate the environment to find all the cached metrics
    """

    keys = [k for k in os.environ if k.lower().startswith("sgtk_metric_cache_")]
    # This extra complicated step is to prevent the following issue in Py2
    # RuntimeError: dictionary changed size during iteration

    for cache_key in keys:
        try:
            cached_data = os.environ.pop(cache_key)
        except KeyError:
            # Might be due to parallel access
            continue

        try:
            data = json.loads(cached_data)
        except json.json.JSONDecodeError:
            logger.debug("Unable to decode cached metric")
            continue

        if not isinstance(data, list) or len(data) != 2:
            logger.debug("Invalid cached metric format")
            continue

        (args, kwargs) = data
        if not isinstance(args, list) or not isinstance(kwargs, dict):
            logger.debug("Invalid cached metric format")
            continue

        metrics.EventMetric.log(*args, **kwargs)
