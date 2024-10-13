# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""Classes and functions for logging Toolkit metrics.

Internal Use Only - We provide no guarantees that the classes and functions
here will be backwards compatible. These objects are also subject to change and
are not part of the public Sgtk API.

"""

###############################################################################
# imports

from collections import deque
from threading import Event, Thread, Lock
import platform
from tank_vendor.six.moves import urllib
from copy import deepcopy

from . import constants, sgre as re

# use api json to cover py 2.5
from tank_vendor import shotgun_api3, six

try:
    from tank_vendor import sgutils
except ImportError:
    from tank_vendor import six as sgutils

json = shotgun_api3.shotgun.json

# From Python 3.8 and later, platform.linux_distribution has been removed,
# so we need something else. Fortunately, the functionality was preserved
# as the distro package on pypi.org. Given that the functionality is
# equivalent between the two, we'll use distro for every version of Python 3.
# As for Python 2, we need to keep using platform as distro is Python 2.7+
# compliant only.
if six.PY2:
    import platform as distro
else:
    from tank_vendor import distro

###############################################################################


class PlatformInfo(object):
    """
    Metric utility class providing basic platform information
    to individual emitted metric

    Platform Official Documentation
    https://docs.python.org/2/library/platform.html
    """

    __cached_platform_info = None

    @classmethod
    def get_darwin_version(cls):
        """
        Returns a macOS / OSX friendly version string such as:
            10.7, 10.11, 10.12, etc

        :return: A str of a simple OS version string.
        """

        os_version = "Unknown"

        # Now that we have 'raw' output secured, try limiting the version
        try:
            raw_version_str = platform.mac_ver()[0]
            os_version = raw_version_str

            # Now that we have 'raw' output secured, we generalize the actual version.
            # We do want to limit the number of possible OS version variant we get metrics for.
            #
            # For macOS / OSX we keep only the Major.minor
            os_version = re.findall(r"\d*\.\d*", raw_version_str)[0]

        except:
            pass

        return os_version

    @classmethod
    def get_linux_version(cls):
        """
        Returns a Linux friendly version string such as:
            "Ubuntu 12", "Fedora 24", "Red Hat 7", "Debian 8" etc

        :return: A str of a simple OS version string.
        """
        os_version = "Unknown"

        try:
            # Get the distributon name and capitalize word(s) (e.g.: Ubuntu, Red Hat)
            distribution = sgutils.ensure_str(distro.linux_distribution()[0].title())
            raw_version_str = sgutils.ensure_str(distro.linux_distribution()[1])

            # For Linux we really just want the 'major' version component
            major_version_str = re.findall(r"\d*", raw_version_str)[0]
            os_version = "%s %s" % (distribution, major_version_str)

        except:
            pass

        return os_version

    @classmethod
    def get_windows_version(cls):
        """
        Returns a Windows friendly version string such as:
            2000, XP, 7, 10 etc.

        :return: A str of a simple OS version string.
        """
        os_version = "Unknown"

        try:
            # On Windows, we can simply use the 'Release()' method
            # as it returns a friendly name e.g: XP, 7, 10 etc.
            os_version = platform.release()

        except:
            pass

        return os_version

    @classmethod
    def get_platform_info(cls):
        """
        Returns a simple OS and OS version information about the underlying host.
        The information is cached to saves on subsequent calls.

        Below are a some different output value examples:
        - {'OS Version': 'Debian 8', 'OS': 'Linux'}
        - {'OS Version': 'Ubuntu 14', 'OS': 'Linux'}
        - {'OS Version': '10.7', 'OS': 'Mac'}
        - {'OS Version': '10.13', 'OS': 'Mac'}
        - {'OS Version': '7', 'OS': 'Windows'}
        - {'OS Version': '10', 'OS': 'Windows'}

        :return: A dict of basic OS and OS version.

        """

        if cls.__cached_platform_info:
            return cls.__cached_platform_info

        os_info = {"OS": "Unknown", "OS Version": "Unknown"}

        try:
            system = platform.system()
            if system == "Darwin":
                os_info["OS"] = "Mac"
                os_info["OS Version"] = cls.get_darwin_version()

            elif system == "Linux":
                os_info["OS"] = system
                os_info["OS Version"] = cls.get_linux_version()

            elif system == "Windows":
                os_info["OS"] = system
                os_info["OS Version"] = cls.get_windows_version()

            else:
                os_info["OS"] = "Unsupported system: (%s)" % (system)

        except:
            # On any exception we fallback to default value
            pass

        # Cache information to save on subsequent calls
        cls.__cached_platform_info = os_info
        return os_info


###############################################################################
# Metrics Queue, Dispatcher, and worker thread classes


class MetricsQueueSingleton(object):
    """A FIFO queue for logging metrics.

    This is a singleton class, so any instantiation will return the same object
    instance within the current process.

    """

    MAXIMUM_QUEUE_SIZE = 100
    """
    Maximum queue size (arbitrary value) until oldest queued item is remove.
    This is to prevent memory leak in case the engine isn't started.
    """

    # keeps track of the single instance of the class
    __instance = None

    # A set of log identifier strings used to check whether a metric has been
    # logged already.
    __logged_metrics = set()

    def __new__(cls, *args, **kwargs):
        """Ensures only one instance of the metrics queue exists."""

        # create the queue instance if it hasn't been created already
        if not cls.__instance:

            # remember the instance so that no more are created
            metrics_queue = super(MetricsQueueSingleton, cls).__new__(
                cls, *args, **kwargs
            )

            metrics_queue._lock = Lock()

            # The underlying collections.deque instance
            metrics_queue._queue = deque(maxlen=cls.MAXIMUM_QUEUE_SIZE)

            cls.__instance = metrics_queue

        return cls.__instance

    def log(self, metric, log_once=False):
        """
        Add the metric to the queue for dispatching.

        If ``log_once`` is set to ``True``, this will only log the metric if it
        is the first attempt to log it.

        :param EventMetric metric: The metric to log.
        :param bool log_once: ``True`` if this metric should be ignored if it
            has already been logged. ``False`` otherwise. Defaults to ``False``.
        """

        # This assumes that supplied object's classes implement __repr__
        # to return consistent results when building objects with the same
        # internal data. See the UserActivityMetric and UserAttributeMetric
        # classes below.
        metric_identifier = repr(metric)

        if log_once and metric_identifier in self.__logged_metrics:
            # the metric is already logged! nothing to do.
            return

        self._lock.acquire()
        try:
            self._queue.append(metric)

            # remember that we've logged this one already
            self.__logged_metrics.add(metric_identifier)
        except:
            pass
        finally:
            self._lock.release()

    def get_metrics(self, count=None):
        """Return `count` metrics.

        :param int count: The number of pending metrics to return.

        If `count` is not supplied, or greater than the number of pending
        metrics, returns all metrics.

        Should never raise an exception.

        """

        metrics = []

        self._lock.acquire()
        try:
            num_pending = len(self._queue)

            # there are pending metrics
            if num_pending:

                # determine how many metrics to retrieve
                if not count or count > num_pending:
                    count = num_pending

                # would be nice to be able to pop N from deque. oh well.
                metrics = [self._queue.popleft() for i in range(0, count)]
        except:
            pass
        finally:
            self._lock.release()

        return metrics


class MetricsDispatcher(object):
    """This class manages 1 or more worker threads dispatching toolkit metrics.

    After initializing the object, the `start()` method is called to
    spin up worker threads for dispatching logged metrics. The `stop()` method
    is later called to stop the worker threads.

    """

    def __init__(self, engine, num_workers=1):
        """Initialize the dispatcher object.

        :param engine: An engine instance for logging, and api access
        :param workers: The number of worker threads to start.

        """

        self._engine = engine
        self._num_workers = num_workers
        self._workers = []
        self._dispatching = False

    def start(self):
        """Starts up the workers for dispatching logged metrics.

        If called on an already dispatching instance, then result is a no-op.

        """

        if self._dispatching:
            self._engine.log_debug(
                "Metrics dispatching already started. Doing nothing."
            )
            return

        # Now check that we have a valid authenticated user, which is
        # required for metrics dispatch. This is to ensure certain legacy
        # and edge case scenarios work, for example the
        # shotgun_cache_actions tank command which runs un-authenticated.
        from ..api import get_authenticated_user

        if not get_authenticated_user():
            return

        # start the dispatch workers to use this queue
        for i in range(self._num_workers):
            worker = MetricsDispatchWorkerThread(self._engine)
            worker.start()
            self._engine.log_debug("Added worker thread: %s" % (worker,))
            self._workers.append(worker)

        self._dispatching = True

    def stop(self):
        """Instructs all worker threads to stop processing metrics."""
        for worker in self.workers:
            worker.halt()

        self._dispatching = False
        self._workers = []

    @property
    def dispatching(self):
        """True if started and dispatching metrics."""
        return self._dispatching

    @property
    def workers(self):
        """A list of workers threads dispatching metrics from the queue."""
        return self._workers


class MetricsDispatchWorkerThread(Thread):
    """
    Worker thread for dispatching metrics to sg logging endpoint.

    Once started this worker will dispatch logged metrics to the shotgun api
    endpoint, if available. The worker retrieves any pending metrics after the
    `DISPATCH_INTERVAL` and sends them all in a single request to sg.

    This worker will also fire the `log_metrics` hooks.
    """

    API_ENDPOINT = "api3/track_metrics/"

    DISPATCH_INTERVAL = 5
    """Worker will wait this long between metrics dispatch attempts."""

    DISPATCH_SHORT_INTERVAL = 0.1
    """
    Delay in seconds between the posting of consecutive batches within a
    dispatcher cycle.
    """

    DISPATCH_BATCH_SIZE = 10
    """
    Worker will dispatch this many metrics at a time, or all if <= 0.
    NOTE: that current PTR server code reject batches larger than 10.
    """

    def __init__(self, engine):
        """
        Initialize the worker thread.

        :params engine: Engine instance
        """

        super(MetricsDispatchWorkerThread, self).__init__()

        self._engine = engine
        self._endpoint_available = False
        # Make this thread a daemon. This means the process won't wait for this
        # thread to complete before exiting. In most cases, proper engine
        # shutdown should halt the worker correctly. In cases where an engine
        # is improperly shut down, this will prevent the process from hanging.
        self.daemon = True

        # makes possible to halt the thread
        self._halt_event = Event()

    def run(self):
        """Runs a loop to dispatch metrics that have been logged."""

        # First of all, check if metrics dispatch is supported
        # connect to shotgun and probe for server version
        sg_connection = self._engine.shotgun
        self._endpoint_available = (
            hasattr(sg_connection, "server_caps")
            and sg_connection.server_caps.version
            and sg_connection.server_caps.version >= (7, 4, 0)
        )

        # Run until halted
        while not self._halt_event.is_set():

            # get the next available metric and dispatch it
            try:
                # For each dispatch cycle, we empty the queue to prevent
                # metric events from accumulating in the queue.
                # Because the server has a limit, we dispatch
                # 'DISPATCH_BATCH_SIZE' items at a time.
                while True:
                    metrics = MetricsQueueSingleton().get_metrics(
                        self.DISPATCH_BATCH_SIZE
                    )
                    if metrics:
                        self._dispatch(metrics)
                        self._halt_event.wait(self.DISPATCH_SHORT_INTERVAL)
                    else:
                        break

            except Exception as e:
                pass
            finally:
                # wait, checking for halt event before more processing
                self._halt_event.wait(self.DISPATCH_INTERVAL)

    def halt(self):
        """
        Ask the worker thread to halt as soon as possible.
        """
        self._halt_event.set()

    def _dispatch(self, metrics):
        """
        Dispatch the supplied metric to the sg api registration endpoint and fire
        the log_metrics hook.

        :param metrics: A list of :class:`EventMetric` instances.
        """

        if self._endpoint_available:
            self._dispatch_to_endpoint(metrics)
        # Execute the log_metrics core hook
        try:
            self._engine.tank.execute_core_hook_method(
                constants.TANK_LOG_METRICS_HOOK_NAME,
                "log_metrics",
                metrics=[m.data for m in metrics],
            )
        except Exception as e:
            # Catch errors to not kill our thread, log them for debug purpose.
            self._engine.log_debug(
                "%s hook failed with %s" % (constants.TANK_LOG_METRICS_HOOK_NAME, e)
            )

    def _dispatch_to_endpoint(self, metrics):
        """
        Dispatch the supplied metric to the sg api registration endpoint.

        :param metrics: A list of :class:`EventMetric` instances.
        """

        # Filter out metrics we don't want to send to the endpoint.
        filtered_metrics_data = []

        for metric in metrics:
            data = metric.data
            # As second pass re-structure unsupported events from supported groups
            # (see more complete comment below)
            if metric.is_supported_event:
                # If this is a supported event, we just need to tack on the
                # version of the core api being used.
                data["event_properties"][
                    EventMetric.KEY_CORE_VERSION
                ] = self._engine.sgtk.version
            else:
                # Still log the event but change its name so it's easy to
                # spot all unofficial events which are logged.
                # Later we might want to simply discard them instead of logging
                # them as "Unknown"
                # Forge a new properties dict with the original data under the
                # "Event Data" key
                properties = data["event_properties"]
                new_properties = {
                    "Event Name": data["event_name"],
                    "Event Data": properties,
                    EventMetric.KEY_APP: properties.get(EventMetric.KEY_APP),
                    EventMetric.KEY_APP_VERSION: properties.get(
                        EventMetric.KEY_APP_VERSION
                    ),
                    EventMetric.KEY_ENGINE: properties.get(EventMetric.KEY_ENGINE),
                    EventMetric.KEY_ENGINE_VERSION: properties.get(
                        EventMetric.KEY_ENGINE_VERSION
                    ),
                    EventMetric.KEY_HOST_APP: properties.get(EventMetric.KEY_HOST_APP),
                    EventMetric.KEY_HOST_APP_VERSION: properties.get(
                        EventMetric.KEY_HOST_APP_VERSION
                    ),
                    EventMetric.KEY_CORE_VERSION: self._engine.sgtk.version,
                }
                data["event_properties"] = new_properties
                data["event_name"] = "Unknown Event"
                data["event_group"] = EventMetric.GROUP_TOOLKIT

            filtered_metrics_data.append(data)

        # Bail out if there is nothing to do
        if not filtered_metrics_data:
            return

        # get this thread's sg connection via tk api
        sg_connection = self._engine.tank.shotgun

        # handle proxy setup by pulling the proxy details from the main
        # shotgun connection
        if sg_connection.config.proxy_handler:
            opener = urllib.request.build_opener(sg_connection.config.proxy_handler)
            urllib.request.install_opener(opener)

        # build the full endpoint url with the shotgun site url
        url = "%s/%s" % (sg_connection.base_url, self.API_ENDPOINT)

        # construct the payload with the auth args and metrics data
        payload = {
            "auth_args": {"session_token": sg_connection.get_session_token()},
            "metrics": filtered_metrics_data,
        }
        payload_json = sgutils.ensure_binary(json.dumps(payload))

        header = {"Content-Type": "application/json"}
        try:
            request = urllib.request.Request(url, payload_json, header)
            urllib.request.urlopen(request)
        except urllib.error.HTTPError:
            # fire and forget, so if there's an error, ignore it.
            pass


###############################################################################
# ToolkitMetric classes and subclasses


class EventMetric(object):
    """
    Convenience class for creating a metric event to be logged on a Shotgun site.

    Use this helper class to create a suitable metric structure that you can
    then pass to the `tank.utils.metrics.EventMetric.log` method.

    The simplest usage of this class is simply to provide an event group and
    event name to the constructor. The "Toolkit" group is reserved for internal
    use.

    Optionally, you can add your own specific metrics by using the
    `properties` parameter. The latter simply takes a standard
    dictionary.

    The class also defines numerous standard definition.
    We highly recommand usage of them. Below is a complete typical usage:

    ```
    metric = EventMetric.log(
        "Custom Event Group",
        "User Logged In",
        properties={
            EventMetric.KEY_ENGINE: "tk-maya",
            EventMetric.KEY_ENGINE_VERSION: "v0.2.2",
            EventMetric.KEY_HOST_APP: "Maya",
            EventMetric.KEY_HOST_APP_VERSION: "2017",
            EventMetric.KEY_APP: "tk-multi-publish2",
            EventMetric.KEY_APP_VERSION: "v0.2.3",
            "CustomBoolMetric": True,
            "RenderJobsSumitted": 173,
        }
    )
    ```
    """

    # Supported event groups
    GROUP_APP = "App"
    GROUP_MEDIA = "Media"
    GROUP_NAVIGATION = "Navigation"
    GROUP_PROJECTS = "Projects"
    GROUP_TASKS = "Tasks"
    GROUP_TOOLKIT = "Toolkit"

    EVENT_NAME_FORMAT = "%s: %s"

    # List of events suported by our backend
    SUPPORTED_EVENTS = [
        EVENT_NAME_FORMAT % (GROUP_APP, "Logged In"),
        EVENT_NAME_FORMAT % (GROUP_APP, "Logged Out"),
        EVENT_NAME_FORMAT % (GROUP_APP, "Viewed Login Page"),
        EVENT_NAME_FORMAT % (GROUP_MEDIA, "Created Note"),
        EVENT_NAME_FORMAT % (GROUP_MEDIA, "Created Reply"),
        EVENT_NAME_FORMAT % (GROUP_NAVIGATION, "Viewed Projects"),
        EVENT_NAME_FORMAT % (GROUP_NAVIGATION, "Viewed Panel"),
        EVENT_NAME_FORMAT % (GROUP_PROJECTS, "Viewed Project Commands"),
        EVENT_NAME_FORMAT % (GROUP_TASKS, "Created Task"),
        EVENT_NAME_FORMAT % (GROUP_TOOLKIT, "Logged In"),
        EVENT_NAME_FORMAT % (GROUP_TOOLKIT, "Launched Action"),
        EVENT_NAME_FORMAT % (GROUP_TOOLKIT, "Launched Command"),
        EVENT_NAME_FORMAT % (GROUP_TOOLKIT, "Launched Software"),
        EVENT_NAME_FORMAT % (GROUP_TOOLKIT, "Loaded Published File"),
        EVENT_NAME_FORMAT % (GROUP_TOOLKIT, "Published"),
        EVENT_NAME_FORMAT % (GROUP_TOOLKIT, "New Workfile"),
        EVENT_NAME_FORMAT % (GROUP_TOOLKIT, "Opened Workfile"),
        EVENT_NAME_FORMAT % (GROUP_TOOLKIT, "Saved Workfile"),
        EVENT_NAME_FORMAT % (GROUP_TOOLKIT, "Executed websockets command"),
        EVENT_NAME_FORMAT % (GROUP_TOOLKIT, "Render & Submit Version"),
    ]

    # Event property keys
    KEY_ACTION_TITLE = "Action Title"
    KEY_APP = "App"
    KEY_APP_VERSION = "App Version"
    KEY_COMMAND = "Command"
    KEY_ENGINE = "Engine"
    KEY_ENGINE_VERSION = "Engine Version"
    KEY_ENTITY_TYPE = "Entity Type"
    KEY_HOST_APP = "Host App"
    KEY_HOST_APP_VERSION = "Host App Version"
    KEY_PUBLISH_TYPE = "Publish Type"
    KEY_CORE_VERSION = "Core Version"

    def __init__(self, group, name, properties=None):
        """
        Initialize a metric event with the given name for the given group.

        :param str group: A group or category this metric event falls into.
                          Any value can be used to implement your own taxonomy.
                          The "Toolkit" group name is reserved for internal use.
        :param str name: A short descriptive event name or performed action,
                         e.g. 'Launched Command', 'Opened Workfile', etc..
        :param dict properties: An optional dictionary of extra properties to be
                                attached to the metric event.
        """
        self._group = str(group)
        self._name = str(name)
        self._properties = properties or {}  # Ensure we always have a valid dict.

    def __repr__(self):
        """Official str representation of the user activity metric."""
        return EventMetric.EVENT_NAME_FORMAT % (self._group, self._name)

    def __str__(self):
        """Readable str representation of the metric."""
        return EventMetric.EVENT_NAME_FORMAT % (self.__class__, self.data)

    @property
    def data(self):
        """
        :returns: The underlying data this metric represents, as a dictionary.
        """
        return {
            "event_group": self._group,
            "event_name": self._name,
            "event_properties": deepcopy(self._properties),
        }

    @property
    def is_supported_event(self):
        """
        Determine whether the metric is supported by Toolkit by checking both
        the event name and group. We want some minimal filtering to prevent
        an overly large number of 3rd party events being sent to the endpoint.

        :return: ``True`` if this event is supported and handled by ToolKit, ``False`` otherwise.
        """
        return repr(self) in EventMetric.SUPPORTED_EVENTS

    @classmethod
    def log(cls, group, name, properties=None, log_once=False, bundle=None):
        """
        Queue a metric event with the given name for the given group on
        the :class:`MetricsQueueSingleton` dispatch queue.

        This method simply adds the metric event to the dispatch queue meaning that
        the metric has to be treated by a dispatcher to be posted.

        :param str group: A group or category this metric event falls into.
                          Any values can be used to implement your own taxonomy,
                          the "Toolkit" group name is reserved for internal use.
        :param str name: A short descriptive event name or performed action,
                         e.g. 'Launched Command', 'Opened Workfile', etc..
        :param dict properties: An optional dictionary of extra properties to be
                                attached to the metric event.
        :param bool log_once: ``True`` if this metric should be ignored if it has
                              already been logged. Defaults to ``False``.
        :param <TankBundle> bundle: A `TankBundle` based class e.g.:app, engine or framework.
                            This argument represents the current bundle where metrics are being logged.
                            If not supplied, this method will attempt to guess the current bundle.

                            Bundles provide additional metrics properties and this method will attempt
                            to gather those automatically to pass to the analytics service.

                            This saves the calling code from having to extract metrics properties
                            and supply them manually. Instead, the calling code can supply only
                            additional, non-standard properties that should be logged.
        """

        if not properties:
            properties = {}

        if not bundle:
            # No bundle specified, try guessing one
            try:
                # import here to prevent circular dependency
                from sgtk.platform.util import current_bundle

                bundle = current_bundle()
            except:
                pass

        if not bundle:
            # Still no bundle? Fallback to engine
            try:
                # import here to prevent circular dependency
                from ..platform.engine import current_engine

                bundle = current_engine()
            except:
                # Bailing out trying to guess bundle
                pass

        if bundle:
            # Add base properties to specified properties (if any)
            properties.update(bundle.get_metrics_properties())
        # else we won't get base properties

        # Now add basic platform information to the metric properties
        properties.update(PlatformInfo.get_platform_info())

        MetricsQueueSingleton().log(cls(group, name, properties), log_once=log_once)


###############################################################################
#
# metrics logging convenience functions (All deprecated)
#


def log_metric(metric, log_once=False):
    """
    This method is deprecated and shouldn't be used anymore.
    Please use the `EventMetric.log` method.
    """
    pass


def log_user_activity_metric(module, action, log_once=False):
    """
    This method is deprecated and shouldn't be used anymore.
    Please use the `EventMetric.log` method.
    """
    pass


def log_user_attribute_metric(attr_name, attr_value, log_once=False):
    """
    This method is deprecated and shouldn't be used anymore.
    Please use the `EventMetric.log` method.
    """
    pass
