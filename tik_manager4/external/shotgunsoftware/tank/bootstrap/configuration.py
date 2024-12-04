# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import inspect
import os

from .import_handler import CoreImportHandler

from ..log import LogManager
from .. import pipelineconfig_utils
from .. import constants
from ..authentication import (
    get_shotgun_authenticator_support_web_login,
    serialize_user,
    ShotgunSamlUser,
)

log = LogManager.get_logger(__name__)


class Configuration(object):
    """
    An abstraction representation around a toolkit configuration.
    """

    LOCAL_CFG_UP_TO_DATE = "LOCAL_CFG_UP_TO_DATE"
    LOCAL_CFG_MISSING = "LOCAL_CFG_MISSING"
    LOCAL_CFG_DIFFERENT = "LOCAL_CFG_DIFFERENT"
    LOCAL_CFG_INVALID = "LOCAL_CFG_INVALID"

    def __init__(self, path, descriptor):
        """
        :param path: :class:`~sgtk.util.ShotgunPath` object describing the path to this configuration
        :param descriptor: :class:`~sgtk.descriptor.Descriptor` object associated with this
            configuration.
        """
        self._path = path
        self._descriptor = descriptor

    def verify_required_shotgun_fields(self):
        """
        Checks so that all shotgun fields required by the configuration
        are present and valid.

        Depending on the configuration, different checks are carried out.

        :raises: :class:`TankBootstrapError` if checks fail.
        """
        # default implementation does not carry out any checks.
        pass

    def status(self):
        """
        Compares the actual configuration installed on disk against the
        associated configuration described by the descriptor passed in via
        the class constructor.

        :returns: LOCAL_CFG_UP_TO_DATE, LOCAL_CFG_MISSING,
                  LOCAL_CFG_DIFFERENT, or LOCAL_CFG_INVALID
        """
        raise NotImplementedError

    def update_configuration(self):
        """
        Ensure that the configuration is up to date with the one
        given by the associated descriptor.
        """
        raise NotImplementedError

    @property
    def descriptor(self):
        """
        Gets the descriptor object associated with the configuration.
        :rtype: :class:`~sgtk.descriptor.Descriptor`
        """
        return self._descriptor

    @property
    def path(self):
        """
        Gets the path to the pipeline configuration on disk.
        :rtype: :class:`~sgtk.util.ShotgunPath`
        """
        return self._path

    def get_tk_instance(self, sg_user):
        """
        Returns a tk instance for this configuration.

        It swaps the core out if needed and ensure we use the right login.

        :param sg_user: Authenticated Shotgun user to associate
                        the tk instance with.

        :returns: A tuple of (:class:`Sgtk` and :class:`ShotgunUser`) representing
            the new current user and the Toolkit instance.
        """
        path = self._path.current_os
        python_core_path = pipelineconfig_utils.get_core_python_path_for_config(path)

        # Get the user before the core swapping and serialize it.
        serialized_user = serialize_user(sg_user)

        # Caching support for the Web authentication flow.
        support_web_login = get_shotgun_authenticator_support_web_login()
        log.debug(
            "Caching the old core's support of the Unified Login Flow: %s"
            % support_web_login
        )

        # Stop claims renewal before swapping core, but only if the claims loop
        # is actually active.
        if isinstance(sg_user, ShotgunSamlUser) and sg_user.is_claims_renewal_active():
            uses_claims_renewal = True
            log.debug("Stopping claims renewal before swapping core.")
            sg_user.stop_claims_renewal()
        else:
            uses_claims_renewal = False

        if self._swap_core_if_needed(python_core_path):
            log.debug("Core swapped, authenticated user will be set.")
        else:
            log.debug("Core didn't need to be swapped, authenticated user will be set.")

        sg_user = self._set_authenticated_user(sg_user, sg_user.login, serialized_user)

        if support_web_login:
            try:
                from ..authentication import set_shotgun_authenticator_support_web_login

                log.debug("This core fully supports the Unified Login Flow.")
                set_shotgun_authenticator_support_web_login(support_web_login)
            except ImportError:
                log.warning(
                    "This swapped core does not support the Unified Login Flow,"
                    "but the original core did. This may lead to problems with"
                    "session renewal or re-authentication."
                )

        # If we're swapping into a core that supports authentication, restart claims renewal. Note
        # that here we're not testing that the API supports claims renewal as to not complexify this
        # code any further. We're assuming it does support claims renewal. If it doesn't that's a
        # user configuration error and they need to upgrade their project.
        #
        # Also make sure that we have a HumanUser and not a ScriptUser by checking the login
        # attribute. Some exotic setup or old project might have people authenticate on startup
        # with a user but then when actually running a project they are switching to script-based
        # authentication, so we have to be mindful that we still are using login based
        # authentication.
        if sg_user and sg_user.login and uses_claims_renewal:
            log.debug("Restarting claims renewal.")
            sg_user.start_claims_renewal()

        return self._tank_from_path(path), sg_user

    def cache_bundles(self, pipeline_configuration, engine_constraint, progress_cb):
        """
        Caches bundles for the configuration.

        Default implementation is valid for a configuration which has an already pre-populated
        local bundle cache.
        """
        log.debug("Configuration has local bundle cache, skipping bundle caching.")

    def _tank_from_path(self, path):
        """
        Perform a tank_from_path for the given pipeline config path.

        :param str path: A pipeline config path for the current os.
        :returns: A :class:`Sgtk` instance.
        """
        # Perform a local import here to make sure we are getting
        # the newly swapped in core code, if it was swapped
        from .. import api
        from .. import pipelineconfig

        log.debug("Executing tank_from_path('%s')" % path)

        # now bypass some of the very extensive validation going on
        # by creating a pipeline configuration object directly
        # and pass that into the factory method.

        # Previous versions of the PipelineConfiguration API didn't support having a descriptor
        # passed in, so we'll have to be backwards compatible with these. If the pipeline
        # configuration does support the get_configuration_descriptor method however, we can
        # pass the descriptor in.
        if hasattr(
            pipelineconfig.PipelineConfiguration, "get_configuration_descriptor"
        ):
            pc = pipelineconfig.PipelineConfiguration(path, self.descriptor)
        else:
            pc = pipelineconfig.PipelineConfiguration(path)
        tk = api.tank_from_path(pc)

        log.debug(
            "Bootstrapped into tk instance %r (%r)" % (tk, tk.pipeline_configuration)
        )
        log.debug("Core API code located here: %s" % inspect.getfile(tk.__class__))

        return tk

    def _swap_core_if_needed(self, target_python_core_path):
        """
        Swap the current tk-core with the one at the given path if their paths
        are not identical.

        :param str target_core_path: Full path to the required tk-core.
        :returns: A bool, True if core was swapped, False otherwise.
        """
        current_python_core_path = self._get_current_core_python_path()

        if target_python_core_path != current_python_core_path:
            CoreImportHandler.swap_core(target_python_core_path)
            return True

        log.debug(
            "Avoided core swap on identical paths: '%s' (current) vs '%s' (target)"
            % (current_python_core_path, target_python_core_path)
        )
        return False

    def _get_current_core_python_path(self):
        """
        Returns the path to the python folder where the current core is.

        :returns: a string.
        """
        import sgtk

        # Remove sgtk/__init__.py from the module name to get the "python" folder.
        return os.path.abspath(os.path.dirname(os.path.dirname(sgtk.__file__)))

    def _set_authenticated_user(
        self, bootstrap_user, bootstrap_user_login, serialized_user
    ):
        """
        Sets the authenticated user.

        If the project that is being bootstrapped into is configured to use a script user inside
        shotgun.yml, the passed in user will be ignored.

        If the new core API can't deserialize the user, the error will be logged and passed in
        user will be used instead.

        :param user: User that was used for bootstrapping.
        :param bootstrap_user_login: Login of the user.
        :param serialized_user: Serialized version of the user.

        :returns: If authentication is supported, a :class:`ShotgunUser` will be returned. Otherwise
            ``None``.
        """
        # perform a local import here to make sure we are getting
        # the newly swapped in core code

        # It's possible we're bootstrapping into a core that doesn't support the authentication
        # module, so try to import.
        try:
            # Use backwards compatible imports.
            from tank_vendor.shotgun_authentication import (
                ShotgunAuthenticator,
                deserialize_user,
            )
            from ..util import CoreDefaultsManager
        except ImportError:
            log.debug("Using pre-0.16 core, no authenticated user will be set.")
            return None

        from .. import api

        log.debug("The project's core supports the authentication module.")

        # Retrieve the user associated with the current project.
        default_user = ShotgunAuthenticator(CoreDefaultsManager()).get_default_user()

        # By default, we'll assume we couldn't find a user with the authenticator.
        project_user = None

        # If the project core's authentication code found a user...
        # (Note that in the following code, a user with no login is a script user.)
        if default_user:
            # If the project uses a script user, we'll use that.
            if not default_user.login:
                log.debug("User retrieved for the project is a script user.")
                project_user = default_user
            # If the project didn't use a script, but the bootstrap did, we'll keep using it.
            elif not bootstrap_user_login:
                # We'll keep using the bootstrap user. This is because configurations like tk-
                # config-basic or tk-config-default are meant to be used with whatever credentials
                # were used during bootstrapping when used with a CachedDescriptor. The bootstrap
                # user is a script user and the project's user is not a script user, so we'll keep
                # using the script user.

                # If the host server is different in the project, for example someone might have set
                # up a server to answer queries for the webapp and another to answer API requests,
                # it means that we'll not be using the correct server with the project. This seems
                # to be an edge-case and more likely a misconfiguration error, so we'll keep the
                # code simple. We're logging the user being used at the end of this method, so it
                # will be clear during support what actually happened.
                log.debug(
                    "User retrieved for the project is not a script, but bootstrap was. Using the "
                    "bootsraps's user."
                )
            elif default_user.login == bootstrap_user_login:
                # In theory, the login should be the same, but they might not be. This is because
                # when core swapping between a more recent version of core to an older one,
                # there might be new ways to retrieve credentials that the older core's
                # ShotgunAuthenticator might not be aware of.
                #
                # This also handle the case where a local install has a server dedicated to the webapp
                # traffic and another for API traffic.
                log.debug(
                    "User retrieved for the project (%r) is the same as for the bootstrap.",
                    default_user,
                )
                project_user = default_user
            else:
                # At this point, different human users are returned by the two cores. We will log
                # a warning.
                log.warning(
                    "It appears the user '%s' used for bootstrap is different than the one for the "
                    "project '%s'. Toolkit will use the user from the bootstrap for coherence.",
                    bootstrap_user_login,
                    default_user.login,
                )
                pass
        else:
            log.debug(
                "No user associated with the project was found. Falling back on the bootstrap user."
            )

        # If we couldn't find a relevant user with the project's authentication module...
        if not project_user:
            try:
                # Try to deserialize the bootstrap user.
                project_user = deserialize_user(serialized_user)
            except Exception:
                log.exception(
                    "Couldn't deserialize the user object with the new core API. "
                    "Current user will be used."
                )
                log.error(
                    "Startup will continue, but you should look into what caused this issue and fix it. "
                    "Please contact support at %s to troubleshoot this issue.",
                    constants.SUPPORT_URL,
                )
                project_user = bootstrap_user

        # Dump all authentication information.
        log.debug("Authenticated host: %s.", project_user.host)
        log.debug("Authenticated login: %s.", project_user.login)
        log.debug("Authenticated http proxy: %s.", project_user.http_proxy)

        api.set_authenticated_user(project_user)
        return project_user
