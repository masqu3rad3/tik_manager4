# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from .descriptor import Descriptor
from .errors import TankDescriptorError, CheckVersionConstraintsError
from . import constants
from .. import LogManager
from ..util.version import is_version_older
from ..util import shotgun
from .. import pipelineconfig_utils

log = LogManager.get_logger(__name__)


class BundleDescriptor(Descriptor):
    """
    Descriptor that describes a Toolkit Bundle (App/Engine/Framework)
    """

    def __init__(self, sg_connection, io_descriptor):
        """
        Use the factory method :meth:`create_descriptor` when
        creating new descriptor objects.

        :param sg_descriptor: Connection to the current site.
        :param io_descriptor: Associated IO descriptor.
        """
        super(BundleDescriptor, self).__init__(io_descriptor)
        self._sg_connection = sg_connection

    @property
    def version_constraints(self):
        """
        A dictionary with version constraints. The absence of a key
        indicates that there is no defined constraint. The following keys can be
        returned: min_sg, min_core, min_engine and min_desktop

        :returns: Dictionary with optional keys min_sg, min_core,
                  min_engine and min_desktop
        """
        constraints = {}

        manifest = self._get_manifest()

        constraints["min_sg"] = (
            manifest.get("requires_shotgun_version") or constants.LOWEST_SHOTGUN_VERSION
        )

        if manifest.get("requires_core_version") is not None:
            constraints["min_core"] = manifest.get("requires_core_version")

        if manifest.get("requires_engine_version") is not None:
            constraints["min_engine"] = manifest.get("requires_engine_version")

        if manifest.get("requires_desktop_version") is not None:
            constraints["min_desktop"] = manifest.get("requires_desktop_version")

        return constraints

    @classmethod
    def _get_sg_version(cls, connection):
        """
        Returns the version of the studio shotgun server. It caches the result per site.

        :param connection: Connection to the Shotgun site.
        :type: :class:`shotgun_api3.Shotgun`

        :returns: a string on the form "X.Y.Z"
        :rtype: str
        """
        try:
            version_tuple = connection.server_info["version"]
        except Exception as e:
            raise TankDescriptorError(
                "Could not extract version number for site: %s" % e
            )

        return ".".join([str(x) for x in version_tuple])

    def _test_version_constraint(self, key, current_version, item_name, reasons):
        """
        Tests a version constraint by ensuring the user provided a version that is not older than the expected
        one.

        :param key: Name of the version constraint
        :param current_version: Version the user passed in.
        :param item_name: Pretty name for the version constraint.
        :param reasons: List of reasons errors will be added to.

        :returns: ``True`` if the constraint test passed, ``False`` if not.
        """

        constraints = self.version_constraints
        if key in constraints:
            minimum_version = constraints[key]
            if not current_version:
                reasons.append(
                    "Requires at least %s %s but no version was specified."
                    % (item_name, minimum_version)
                )
            elif is_version_older(current_version, minimum_version):
                reasons.append(
                    "Requires at least %s %s but currently installed version is %s."
                    % (item_name, minimum_version, current_version)
                )

    def check_version_constraints(
        self, core_version=None, engine_descriptor=None, desktop_version=None
    ):
        """
        Checks if there are constraints blocking an upgrade or install.

        :param core_version: Core version. If None, current core version will be used.
        :type core_version: str
        :param engine_descriptor: Descriptor of the engine this bundle will run under. None by default.
        :type engine_descriptor: :class:`~sgtk.bootstrap.DescriptorBundle`
        :param desktop_version: Version of the PTR desktop app. None by default.
        :type desktop_version: str

        :raises: Raised if one or multiple constraint checks has failed.
        :rtype: :class:`sgtk.descriptor.CheckVersionConstraintsError`
        """
        reasons = []

        self._test_version_constraint(
            "min_sg",
            self._get_sg_version(self._sg_connection),
            "Flow Production Tracking",
            reasons,
        )
        self._test_version_constraint(
            "min_core",
            core_version or pipelineconfig_utils.get_currently_running_api_version(),
            "Core API",
            reasons,
        )

        constraints = self.version_constraints

        if "min_engine" in constraints:
            if engine_descriptor is None:
                reasons.append(
                    "Requires a minimal engine version but no engine was specified."
                )
            else:
                curr_engine_version = engine_descriptor.version

                minimum_engine_version = constraints["min_engine"]
                if is_version_older(curr_engine_version, minimum_engine_version):
                    reasons.append(
                        "Requires at least Engine %s %s but currently "
                        "installed version is %s."
                        % (
                            engine_descriptor.display_name,
                            minimum_engine_version,
                            curr_engine_version,
                        )
                    )

        # for multi engine apps, validate the supported_engines list
        supported_engines = self.supported_engines
        if supported_engines is not None:
            if engine_descriptor is None:
                reasons.append(
                    "Bundle is compatible with a subset of engines but no engine was specified."
                )
            else:
                # this is a multi engine app!
                engine_name = engine_descriptor.system_name
                if engine_name not in supported_engines:
                    reasons.append(
                        "Not compatible with engine %s. "
                        "Supported engines are %s."
                        % (engine_name, ", ".join(supported_engines))
                    )

        self._test_version_constraint(
            "min_desktop", desktop_version, "FPTR desktop app", reasons
        )

        if len(reasons) > 0:
            raise CheckVersionConstraintsError(reasons)

    @property
    def required_context(self):
        """
        The required context, if there is one defined, for a bundle.
        This is a list of strings, something along the lines of
        ["user", "task", "step"] for an app that requires a context with
        user task and step defined.

        :returns: A list of strings, with an empty list meaning no items required.
        """
        manifest = self._get_manifest()
        rc = manifest.get("required_context")
        if rc is None:
            rc = []
        return rc

    @property
    def supported_platforms(self):
        """
        The platforms supported. Possible values
        are windows, linux and mac.

        Always returns a list, returns an empty list if there is
        no constraint in place.

        example: ["windows", "linux"]
        example: []
        """
        manifest = self._get_manifest()
        sp = manifest.get("supported_platforms")
        if sp is None:
            sp = []
        return sp

    @property
    def configuration_schema(self):
        """
        The manifest configuration schema for this bundle.
        Always returns a dictionary.

        :returns: Configuration dictionary as defined
                  in the manifest or {} if not defined
        """
        manifest = self._get_manifest()
        cfg = manifest.get("configuration")
        # always return a dict
        if cfg is None:
            cfg = {}
        return cfg

    @property
    def supported_engines(self):
        """
        The engines supported by this app or framework. Examples
        of return values:

            - ``None`` - Works in all engines.
            - ``["tk-maya", "tk-nuke"]`` - Works in Maya and Nuke.
        """
        manifest = self._get_manifest()
        return manifest.get("supported_engines")

    @property
    def required_frameworks(self):
        """
        A list of required frameworks for this item.

        Always returns a list - for example::

            [{'version': 'v0.1.0', 'name': 'tk-framework-widget'}]

        Each item contains a name and a version key.

        :returns: list of dictionaries
        """
        manifest = self._get_manifest()
        frameworks = manifest.get("frameworks")
        # always return a list
        if frameworks is None:
            frameworks = []
        return frameworks

    ###############################################################################################
    # compatibility accessors to ensure that all systems
    # calling this (previously internal!) parts of toolkit
    # will still work.
    def get_version_constraints(self):
        return self.version_constraints

    def get_required_context(self):
        return self.required_context

    def get_supported_platforms(self):
        return self.supported_platforms

    def get_configuration_schema(self):
        return self.configuration_schema

    def get_supported_engines(self):
        return self.supported_engines

    def get_required_frameworks(self):
        return self.required_frameworks  # noqa

    ###############################################################################################
    # helper methods

    def ensure_shotgun_fields_exist(self, tk=None):
        """
        Ensures that any shotgun fields a particular descriptor requires
        exists in shotgun. In the metadata (``info.yml``) for an app or an engine,
        it is possible to define a section for this::

            # the Shotgun fields that this app needs in order to operate correctly
            requires_shotgun_fields:
                Version:
                    - { "system_name": "sg_movie_type", "type": "text" }

        This method will retrieve the metadata and ensure that any required
        fields exists.

        .. warning::
            This feature may be deprecated in the future.

        :param tk: Core API instance to use for post install execution. This value
                   defaults to ``None`` for backwards compatibility reasons and in
                   the case a None value is passed in, the hook will not execute.
        """
        # if tk is None, exit early. This is to keep things backwards compatible
        # with earlier versions of the desktop startup framework (which never used
        # any post install functionality, so the fact that we don't execute anything
        # in that case should't affect the behavior).
        if tk is None:
            return

        # first fetch metadata
        manifest = self._get_manifest()
        sg_fields_def = manifest.get("requires_shotgun_fields")

        if sg_fields_def:  # can be defined as None from yml file

            log.debug("Processing requires_shotgun_fields manifest directive")

            for sg_entity_type in sg_fields_def:

                for field in sg_fields_def.get(sg_entity_type, []):

                    # attempt to create field!
                    sg_data_type = field["type"]
                    sg_field_name = field["system_name"]

                    log.debug(
                        "Field %s.%s (type %s) is required."
                        % (sg_entity_type, sg_field_name, sg_data_type)
                    )

                    # now check that the field exists
                    sg_field_schema = tk.shotgun.schema_field_read(sg_entity_type)
                    if sg_field_name not in sg_field_schema:

                        log.debug("Field does not exist - attempting to create it.")

                        if not sg_field_name.startswith("sg_"):
                            # the schema_field_create has got some magic when it creates
                            # fields. It for example always prefixes custom fields with sg_...
                            # any fields defined in the manifest that don't already exist
                            # can therefore not be created.
                            raise TankDescriptorError(
                                "Cannot create field '%s.%s' as required by app manifest. "
                                "Only fields starting with sg_ can be created"
                                % (sg_entity_type, sg_field_name)
                            )

                        # sg_my_awesome_field -> My Awesome Field
                        ui_field_name = " ".join(
                            word.capitalize() for word in sg_field_name[3:].split("_")
                        )

                        log.debug(
                            "Computed the field display name to be '%s'" % ui_field_name
                        )

                        log.debug("Creating field...")
                        tk.shotgun.schema_field_create(
                            sg_entity_type, sg_data_type, ui_field_name
                        )
                        log.debug("...field creation complete.")

                    else:
                        log.debug(
                            "Field %s.%s already exists in Flow Production Tracking."
                            % (sg_entity_type, sg_field_name)
                        )

    def run_post_install(self, tk=None):
        """
        If a post install hook exists in a descriptor, execute it. In the
        hooks directory for an app or engine, if a 'post_install.py' hook
        exists, the hook will be executed upon each installation.

        Errors reported in the post install hook will be reported to the error
        log but execution will continue.

        .. warning:: We no longer recommend using post install hooks. Should you
                     need to use one, take great care when designing it so that
                     it can execute correctly for all users, regardless of
                     their shotgun and system permissions.

        :param tk: Core API instance to use for post install execution. This value
                   defaults to ``None`` for backwards compatibility reasons and in
                   the case a None value is passed in, the hook will not execute.
        """
        # if tk is None, exit early. This is to keep things backwards compatible
        # with earlier versions of the desktop startup framework (which never used
        # any post install functionality, so the fact that we don't execute anything
        # in that case should't affect the behavior).
        if tk is None:
            return

        try:
            tk.pipeline_configuration.execute_post_install_bundle_hook(self.get_path())
        except Exception as e:
            log.error(
                "Could not run post-install hook for %s. Error reported: %s" % (self, e)
            )


class EngineDescriptor(BundleDescriptor):
    """
    Descriptor that describes a Toolkit Engine
    """

    def __init__(
        self, sg_connection, io_descriptor, bundle_cache_root_override, fallback_roots
    ):
        """
        .. note:: Use the factory method :meth:`create_descriptor` when
                  creating new descriptor objects.

        :param sg_connection: Connection to the current site.
        :param io_descriptor: Associated IO descriptor.
        :param bundle_cache_root_override: Override for root path to where
            downloaded apps are cached.
        :param fallback_roots: List of immutable fallback cache locations where
            apps will be searched for.
        """
        super(EngineDescriptor, self).__init__(sg_connection, io_descriptor)


class AppDescriptor(BundleDescriptor):
    """
    Descriptor that describes a Toolkit App
    """

    def __init__(
        self, sg_connection, io_descriptor, bundle_cache_root_override, fallback_roots
    ):
        """
        .. note:: Use the factory method :meth:`create_descriptor` when
                  creating new descriptor objects.

        :param sg_connection: Connection to the current site.
        :param io_descriptor: Associated IO descriptor.
        :param bundle_cache_root_override: Override for root path to where
            downloaded apps are cached.
        :param fallback_roots: List of immutable fallback cache locations where
            apps will be searched for.
        """
        super(AppDescriptor, self).__init__(sg_connection, io_descriptor)


class FrameworkDescriptor(BundleDescriptor):
    """
    Descriptor that describes a Toolkit Framework
    """

    def __init__(
        self, sg_connection, io_descriptor, bundle_cache_root_override, fallback_roots
    ):
        """
        .. note:: Use the factory method :meth:`create_descriptor` when
                  creating new descriptor objects.

        :param sg_connection: Connection to the current site.
        :param io_descriptor: Associated IO descriptor.
        :param bundle_cache_root_override: Override for root path to where
            downloaded apps are cached.
        :param fallback_roots: List of immutable fallback cache locations where
            apps will be searched for.
        """
        super(FrameworkDescriptor, self).__init__(sg_connection, io_descriptor)

    def is_shared_framework(self):
        """
        Returns a boolean indicating whether the bundle is a shared framework.
        Shared frameworks only have a single instance per instance name in the
        current environment.

        :returns: True if the framework is shared
        """
        manifest = self._get_manifest()
        shared = manifest.get("shared")
        # always return a bool
        if shared is None:
            # frameworks are now shared by default unless you opt out.
            shared = True
        return shared
