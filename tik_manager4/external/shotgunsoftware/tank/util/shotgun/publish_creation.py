# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Logic for publishing files to Shotgun.
"""
from __future__ import with_statement

import os
from tank_vendor.six.moves import urllib
import pprint

from .publish_util import (
    get_published_file_entity_type,
    get_cached_local_storages,
    find_publish,
)
from ..errors import ShotgunPublishError
from ...errors import TankError, TankMultipleMatchingTemplatesError
from ...log import LogManager
from ..shotgun_path import ShotgunPath
from .. import constants
from .. import login

try:
    from tank_vendor import sgutils
except ImportError:
    from tank_vendor import six as sgutils

log = LogManager.get_logger(__name__)


@LogManager.log_timing
def register_publish(tk, context, path, name, version_number, **kwargs):
    """
    Creates a Published File in Shotgun.

    **Introduction**

    The publish will be associated with the current context and point
    at the given file. The method will attempt to add the publish to
    Shotgun as a local file link, and failing that it will generate
    a ``file://`` url to represent the path.

    In addition to the path, a version number and a name needs to be provided.
    The version number should reflect the iteration or revision of the publish
    and will be used to populate the number field of the publish that is created
    in Shotgun. The name should represent the name of the item, without any version
    number. This is used to group together publishes in Shotgun and various
    integrations.

    If the path matches any local storage roots defined by the toolkit project,
    it will be uploaded as a local file link to Shotgun. If not matching roots
    are found, the method will retrieve the list of local storages from Shotgun
    and try to locate a suitable storage. Failing that, it will fall back on a
    register the path as a ``file://`` url. For more information on
    this resolution logic, see our
    `Admin Guide <https://help.autodesk.com/view/SGDEV/ENU/?guid=SGD_pg_integrations_admin_guides_integrations_admin_guide_html#configuring-published-file-path-resolution>`_.

    .. note:: Shotgun follows a convention where the name passed to the register publish method is used
              to control how things are grouped together. When Shotgun and Toolkit groups things together,
              things are typically grouped first by project/entity/task and then by publish name and version.

              If you create three publishes in Shotgun, all having the name 'foreground.ma' and version numbers
              1, 2 and 3, Shotgun will assume that these are three revisions of the same content and will
              group them together in a group called 'foreground.ma'.

              We recommend a convention where the ``name`` parameter reflects the filename passed in via
              the ``file_path`` parameter, but with the version number removed. For example:

              - ``file_path: /tmp/layout.v027.ma, name: layout.ma, version_number: 27``
              - ``file_path: /tmp/foreground_v002.%04d.exr, name: foreground.exr, version_number: 2``

    .. note:: When publishing file sequences, the method will try to normalize your path based on the
              current template configuration. For example, if you supply the path ``render.$F4.dpx``,
              it will translated to ``render.%04d.dpx`` automatically, assuming there is a matching
              template defined. If you are not using templates or publishing files that do not match
              any configured templates, always provide sequences on a ``%0xd`` or
              ``%xd`` `printf <https://en.wikipedia.org/wiki/Printf_format_string>`_ style
              pattern.

    **Examples**

    The example below shows a basic publish. In addition to the required parameters, it is
    recommended to supply at least a comment and a Publish Type::

        >>> file_path = '/studio/demo_project/sequences/Sequence-1/shot_010/Anm/publish/layout.v001.ma'
        >>> name = 'layout.ma'
        >>> version_number = 1
        >>>
        >>> sgtk.util.register_publish(
            tk,
            context,
            file_path,
            name,
            version_number,
            comment = 'Initial layout composition.',
            published_file_type = 'Maya Scene'
        )

        {'code': 'layout.v001.ma',
         'created_by': {'id': 40, 'name': 'John Smith', 'type': 'HumanUser'},
         'description': 'Initial layout composition.',
         'entity': {'id': 2, 'name': 'shot_010', 'type': 'Shot'},
         'id': 2,
         'published_file_type': {'id': 134, 'type': 'PublishedFileType'},
         'name': 'layout.ma',
         'path': {'content_type': None,
          'link_type': 'local',
          'local_path': '/studio/demo_project/sequences/Sequence-1/shot_010/Anm/publish/layout.v001.ma',
          'local_path_linux': '/studio/demo_project/sequences/Sequence-1/shot_010/Anm/publish/layout.v001.ma',
          'local_path_mac': '/studio/demo_project/sequences/Sequence-1/shot_010/Anm/publish/layout.v001.ma',
          'local_path_windows': 'c:\\studio\\demo_project\\sequences\\Sequence-1\\shot_010\\Anm\\publish\\layout.v001.ma',
          'local_storage': {'id': 1, 'name': 'primary', 'type': 'LocalStorage'},
          'name': 'layout.v001.ma',
          'url': 'file:///studio/demo_project/sequences/Sequence-1/shot_010/Anm/publish/layout.v001.ma'},
         'path_cache': 'demo_project/sequences/Sequence-1/shot_010/Anm/publish/layout.v001.ma',
         'project': {'id': 4, 'name': 'Demo Project', 'type': 'Project'},
         'published_file_type': {'id': 12, 'name': 'Layout Scene', 'type': 'PublishedFileType'},
         'task': None,
         'type': 'PublishedFile',
         'version_number': 1}

    When using the ``dry_run`` option, the returned data will look something like this::

        >>> file_path = '/studio/demo_project/sequences/Sequence-1/shot_010/Anm/publish/layout.v001.ma'
        >>> name = 'layout'
        >>> version_number = 1
        >>>
        >>> sgtk.util.register_publish(
            tk,
            context,
            file_path,
            name,
            version_number,
            comment='Initial layout composition.',
            published_file_type='Layout Scene'
            dry_run=True
        )

        {'code': 'layout.v001.ma',
         'description': 'Initial layout composition.',
         'entity': {'id': 2, 'name': 'shot_010', 'type': 'Shot'},
         'path': {'local_path': '/studio/demo_project/sequences/Sequence-1/shot_010/Anm/publish/layout.v001.ma'},
         'project': {'id': 4, 'name': 'Demo Project', 'type': 'Project'},
         'task': None,
         'type': 'PublishedFile',
         'version_number': 1}

    Be aware that the data may be different if the ``before_register_publish``
    hook has been overridden.

    **Parameters**

    :param tk: :class:`~sgtk.Sgtk` instance
    :param context: A :class:`~sgtk.Context` to associate with the publish. This will
                    populate the ``task`` and ``entity`` link in Shotgun.
    :param path: The path to the file or sequence we want to publish. If the
                 path is a sequence path it will be abstracted so that
                 any sequence keys are replaced with their default values.
    :param name: A name, without version number, which helps distinguish
               this publish from other publishes. This is typically
               used for grouping inside of Shotgun so that all the
               versions of the same "file" can be grouped into a cluster.
               For example, for a Maya publish, where we track only
               the scene name, the name would simply be that: the scene
               name. For something like a render, it could be the scene
               name, the name of the AOV and the name of the render layer.
    :param version_number: The version number of the item we are publishing.


    In addition to the above, the following optional arguments exist:

        - ``task`` - A shotgun entity dictionary with keys ``id`` and ``type`` (where type should always be ``Task``).
          This value will be used to populate the task field for the created Shotgun publish record.
          If no value is specified, the task will be determined based on the context parameter.

        - ``comment`` - A string containing a description of what is being published.

        - ``thumbnail_path`` - A path to a thumbnail (png or jpeg) which will be uploaded to shotgun
          and associated with the publish.

        - ``dependency_paths`` - A list of file system paths that should be attempted to be registered
          as dependencies. Files in this listing that do not appear as publishes in shotgun will be ignored.

        - ``dependency_ids`` - A list of publish ids which should be registered as dependencies.

        - ``published_file_type`` - A publish type in the form of a string. If the publish type does not
          already exist in Shotgun, it will be created.

        - ``update_entity_thumbnail`` - Push thumbnail up to the associated entity

        - ``update_task_thumbnail`` - Push thumbnail up to the associated task

        - ``created_by`` - Override for the user that will be marked as creating the publish.  This should
          be in the form of shotgun entity, e.g. {"type":"HumanUser", "id":7}. If not set, the user will
          be determined using :meth:`sgtk.util.get_current_user`.

        - ``created_at`` - Override for the date the publish is created at.  This should be a python
          datetime object

        - ``version_entity`` - The Shotgun review version that the publish should be linked to. This
          should be a dictionary of keys ``id`` and ``type`` (where type should always be ``Version``).
          This parameter is useful for workflows where a Shotgun Version has already been created for review
          purposes and you want to associate the publish created by this method.

          Note: For workflows where you have an existing review version and want to create a series of associated
          publishes, you may want to extract a :class:`~sgtk.Context` from the Version entity and pass that
          to the :meth:`register_publish` method in order to ensure consistency in how objects are associated
          in Shotgun.

        - ``sg_fields`` - Some additional Shotgun fields as a dict (e.g. ``{'sg_custom_field': 'hello'}``)

        - ``dry_run`` - Boolean. If set, do not actually create a database entry. Return the
          dictionary of data that would be supplied to Shotgun to create the PublishedFile entity.

    :raises: :class:`ShotgunPublishError` on failure.
    :returns: The created entity dictionary.
    """
    log.debug(
        "Publish: Begin register publish for context {0} and path {1}".format(
            context, path
        )
    )
    entity = None
    try:
        # get the task from the optional args, fall back on context task if not set
        task = kwargs.get("task")
        if task is None:
            task = context.task

        thumbnail_path = kwargs.get("thumbnail_path")
        comment = kwargs.get("comment")
        dependency_paths = kwargs.get("dependency_paths", [])
        dependency_ids = kwargs.get("dependency_ids", [])
        published_file_type = kwargs.get("published_file_type")
        if not published_file_type:
            # check for legacy name:
            published_file_type = kwargs.get("tank_type")
        update_entity_thumbnail = kwargs.get("update_entity_thumbnail", False)
        update_task_thumbnail = kwargs.get("update_task_thumbnail", False)
        created_by_user = kwargs.get("created_by")
        created_at = kwargs.get("created_at")
        version_entity = kwargs.get("version_entity")
        sg_fields = kwargs.get("sg_fields", {})
        dry_run = kwargs.get("dry_run", False)

        published_file_entity_type = get_published_file_entity_type(tk)

        log.debug("Publish: Resolving the published file type")
        sg_published_file_type = None
        # query shotgun for the published_file_type
        if published_file_type:
            if not isinstance(published_file_type, str):
                raise TankError("published_file_type must be a string")

            if published_file_entity_type == "PublishedFile":
                filters = [["code", "is", published_file_type]]
                sg_published_file_type = tk.shotgun.find_one(
                    "PublishedFileType", filters=filters
                )

                if not sg_published_file_type:
                    # create a published file type on the fly
                    sg_published_file_type = tk.shotgun.create(
                        "PublishedFileType", {"code": published_file_type}
                    )
            else:  # == TankPublishedFile
                filters = [
                    ["code", "is", published_file_type],
                    ["project", "is", context.project],
                ]
                sg_published_file_type = tk.shotgun.find_one(
                    "TankType", filters=filters
                )

                if not sg_published_file_type:
                    # create a tank type on the fly
                    sg_published_file_type = tk.shotgun.create(
                        "TankType",
                        {"code": published_file_type, "project": context.project},
                    )

        # create the publish
        log.debug("Publish: Creating publish in Flow Production Tracking")
        entity = _create_published_file(
            tk,
            context,
            path,
            name,
            version_number,
            task,
            comment,
            sg_published_file_type,
            created_by_user,
            created_at,
            version_entity,
            sg_fields,
            dry_run=dry_run,
        )

        if not dry_run:
            # upload thumbnails
            log.debug("Publish: Uploading thumbnails")
            if thumbnail_path and os.path.exists(thumbnail_path):

                # publish
                tk.shotgun.upload_thumbnail(
                    published_file_entity_type, entity["id"], thumbnail_path
                )

                # entity
                if update_entity_thumbnail == True and context.entity is not None:
                    tk.shotgun.upload_thumbnail(
                        context.entity["type"], context.entity["id"], thumbnail_path
                    )

                # task
                if update_task_thumbnail == True and task is not None:
                    tk.shotgun.upload_thumbnail("Task", task["id"], thumbnail_path)

            else:
                # no thumbnail found - instead use the default one
                this_folder = os.path.abspath(os.path.dirname(__file__))
                no_thumb = os.path.join(
                    this_folder, os.path.pardir, "resources", "no_preview.jpg"
                )
                tk.shotgun.upload_thumbnail(
                    published_file_entity_type, entity.get("id"), no_thumb
                )

            # register dependencies
            log.debug("Publish: Register dependencies")
            _create_dependencies(tk, entity, dependency_paths, dependency_ids)
            log.debug("Publish: Complete")

        return entity
    except Exception as e:
        # Log the exception so the original traceback is available
        log.exception(e)
        if "[Attachment.local_storage] does not exist" in str(e):
            raise ShotgunPublishError(
                "Local File Linking seems to be turned off. "
                "Turn it on on your Site Preferences Page.",
                entity,
            )
        else:
            # Raise our own exception with the original message and the created entity,
            # if any
            raise ShotgunPublishError(error_message="%s" % e, entity=entity)


def _create_published_file(
    tk,
    context,
    path,
    name,
    version_number,
    task,
    comment,
    published_file_type,
    created_by_user,
    created_at,
    version_entity,
    sg_fields=None,
    dry_run=False,
):
    """
    Creates a publish entity in shotgun given some standard fields.

    :param tk: :class:`~sgtk.Sgtk` instance
    :param context: A :class:`~sgtk.Context` to associate with the publish. This will
                    populate the ``task`` and ``entity`` link in Shotgun.
    :param path: The path to the file or sequence we want to publish. If the
                 path is a sequence path it will be abstracted so that
                 any sequence keys are replaced with their default values.
    :param name: A name, without version number, which helps distinguish
               this publish from other publishes. This is typically
               used for grouping inside of Shotgun so that all the
               versions of the same "file" can be grouped into a cluster.
               For example, for a Maya publish, where we track only
               the scene name, the name would simply be that: the scene
               name. For something like a render, it could be the scene
               name, the name of the AOV and the name of the render layer.
    :param version_number: The version number of the item we are publishing.
    :param task: Shotgun Task dictionary to associate with publish or ``None``
    :param comment: Comments string to associate with publish
    :param published_file_type: Shotgun publish type dictionary to
                associate with publish
    :param created_by_user: User entity to associate with publish or ``None``
                if current user (via :meth:`sgtk.util.get_current_user`)
                should be used.
    :param created_at: Timestamp to associate with publish or None for default.
    :param version_entity: Version dictionary to associate with publish or ``None``.
    :param sg_fields: Dictionary of additional data to add to publish.
    :param dry_run: Don't actually create the published file entry. Simply
                    return the data dictionary that would be supplied.

    :returns: The result of the shotgun API create method.
    """

    data = {
        "description": comment,
        "name": name,
        "task": task,
        "version_number": version_number,
    }

    # we set the optional additional fields first so we don't allow overwriting the standard parameters
    if sg_fields is None:
        sg_fields = {}
    data.update(sg_fields)

    if created_by_user:
        data["created_by"] = created_by_user
    else:
        # use current user
        sg_user = login.get_current_user(tk)
        if sg_user:
            data["created_by"] = sg_user

    if created_at:
        data["created_at"] = created_at

    published_file_entity_type = get_published_file_entity_type(tk)

    if published_file_type:
        if published_file_entity_type == "PublishedFile":
            data["published_file_type"] = published_file_type
        else:
            # using legacy type TankPublishedFile
            data["tank_type"] = published_file_type

    if version_entity:
        data["version"] = version_entity

    # Determine the value of the link field based on the given context
    if context.project is None:
        # when running toolkit as a standalone plugin, the context may be
        # empty and not contain a project. Publishes are project entities
        # in Shotgun, so we cannot proceed without a project.
        raise TankError(
            "Your context needs to at least have a project set in order to publish."
        )

    elif context.entity is None:
        # If the context does not have an entity, link it up to the project.
        # This happens for project specific workflows such as editorial
        # workflows, ingest and when running zero config toolkit plugins in
        # a generic project mode.
        data["entity"] = context.project

    else:
        data["entity"] = context.entity

    # set the associated project
    data["project"] = context.project

    # Check if path is a url or a straight file path.  Path
    # is assumed to be a url if it has a scheme:
    #
    #     scheme://netloc/path
    #
    path_is_url = False
    res = urllib.parse.urlparse(path)
    if res.scheme:
        # handle Windows drive letters - note this adds a limitation
        # but one that is not likely to be a problem as single-character
        # schemes are unlikely!
        if len(res.scheme) > 1 or not res.scheme.isalpha():
            path_is_url = True

    # naming and path logic is different depending on url
    if path_is_url:

        # extract name from url:
        #
        # scheme://hostname.com/path/to/file.ext -> file.ext
        # scheme://hostname.com -> hostname.com
        if res.path:
            # scheme://hostname.com/path/to/file.ext -> file.ext
            data["code"] = res.path.split("/")[-1]
        else:
            # scheme://hostname.com -> hostname.com
            data["code"] = res.netloc

        # make sure that the url is escaped property, otherwise
        # shotgun might not accept it.
        #
        # for quoting logic, see bugfix here:
        # http://svn.python.org/view/python/trunk/Lib/urllib.py?r1=71780&r2=71779&pathrev=71780
        #
        # note: by applying a safe pattern like this, we guarantee that already quoted paths
        #       are not touched, e.g. quote('foo bar') == quote('foo%20bar')
        data["path"] = {
            "url": urllib.parse.quote(path, safe="%/:=&?~#+!$,;'@()*[]"),
            "name": data["code"],  # same as publish name
        }

    else:

        # normalize the path to native slashes
        norm_path = ShotgunPath.normalize(path)
        if norm_path != path:
            log.debug("Normalized input path '%s' -> '%s'" % (path, norm_path))
            path = norm_path

        # convert the abstract fields to their defaults
        path = _translate_abstract_fields(tk, path)

        # name of publish is the filename
        data["code"] = os.path.basename(path)

        # Make path platform agnostic and determine if it belongs
        # to a storage that is associated with this toolkit config.
        root_name, path_cache = _calc_path_cache(tk, path)

        if path_cache:
            # there is a toolkit storage mapping defined for this storage
            log.debug(
                "The path '%s' is associated with config root '%s'." % (path, root_name)
            )

            # check if the shotgun server supports the storage and relative_path parameters which
            # allows us to specify exactly which storage to bind a publish to rather than relying on
            # Shotgun to compute this.
            supports_specific_storage_syntax = (
                hasattr(tk.shotgun, "server_caps")
                and tk.shotgun.server_caps.version
                and tk.shotgun.server_caps.version >= (7, 0, 1)
            )

            if supports_specific_storage_syntax:

                # get corresponding PTR local storage for the matching root name
                storage = tk.pipeline_configuration.get_local_storage_for_root(
                    root_name
                )

                if storage is None:
                    # there is no storage in Shotgun that matches the one toolkit expects.
                    # this *may* be ok because there may be another storage in Shotgun that
                    # magically picks up the publishes and associates with them. In this case,
                    # issue a warning and fall back on the server-side functionality
                    log.warning(
                        "Could not find the expected storage for required root "
                        "'%s' in PTR to associate publish '%s' with. "
                        "Falling back to Flow Production Tracking's built-in storage resolution "
                        "logic. It is recommended that you explicitly map a "
                        "local storage to required root '%s'."
                        % (root_name, path, root_name)
                    )
                    data["path"] = {"local_path": path}

                else:
                    data["path"] = {
                        "relative_path": path_cache,
                        "local_storage": storage,
                    }

            else:
                # use previous syntax where we pass the whole path to Shotgun
                # and shotgun will do the storage/relative path split server side.
                # This operation may do unexpected things if you have multiple
                # storages that are identical or overlapping
                data["path"] = {"local_path": path}

            # fill in the path cache field which is used for filtering in Shotgun
            # (because PTR does not support
            data["path_cache"] = path_cache

        else:

            # path does not map to any configured root - fall back gracefully:
            # 1. look for storages in Shotgun and see if we can create a local path
            # 2. failing that, just register the entry as a file:// resource.
            log.debug("Path '%s' does not have an associated config root." % path)
            log.debug("Will check PTR local storages to see if there is a match.")

            matching_local_storage = False
            for storage in get_cached_local_storages(tk):
                local_storage_path = ShotgunPath.from_shotgun_dict(storage).current_os
                # assume case preserving file systems rather than case sensitive
                if local_storage_path and path.lower().startswith(
                    local_storage_path.lower()
                ):
                    log.debug("Path matches PTR local storage '%s'" % storage["code"])
                    matching_local_storage = True
                    break

            if matching_local_storage:
                # there is a local storage matching this path
                # so use that when publishing
                data["path"] = {"local_path": path}

            else:
                # no local storage defined so publish as a file:// url
                log.debug(
                    "No local storage matching path '%s' - path will be "
                    "registered as a file:// url." % (path,)
                )

                # (see http://stackoverflow.com/questions/11687478/convert-a-filename-to-a-file-url)
                file_url = urllib.parse.urljoin(
                    "file:", urllib.request.pathname2url(path)
                )
                log.debug("Converting '%s' -> '%s'" % (path, file_url))
                data["path"] = {
                    "url": file_url,
                    "name": data["code"],  # same as publish name
                }

    # now call out to hook just before publishing
    data = tk.execute_core_hook(
        constants.TANK_PUBLISH_HOOK_NAME, shotgun_data=data, context=context
    )

    if dry_run:
        # add the publish type to be as consistent as possible
        data["type"] = published_file_entity_type
        log.debug(
            "Dry run. Simply returning the data that would be sent to PTR: %s"
            % pprint.pformat(data)
        )
        return data
    else:
        log.debug("Registering publish in Flow Production Tracking: %s" % pprint.pformat(data))
        return tk.shotgun.create(published_file_entity_type, data)


def _translate_abstract_fields(tk, path):
    """
    Translates abstract fields for a path into the default abstract value.
    For example, the path /foo/bar/xyz.0003.exr will be transformed into
    /foo/bar/xyz.%04d.exr

    :param tk: :class:`~sgtk.Sgtk` instance
    :param path: a normalized path with slashes matching os.path.sep

    :returns: the path with any abstract fields normalized.
    """
    try:
        template = tk.template_from_path(path)
    except TankMultipleMatchingTemplatesError:
        log.debug(
            "Path matches multiple templates. Not translating abstract fields: %s"
            % path
        )
    else:
        if template:
            abstract_key_names = [
                k.name for k in template.keys.values() if k.is_abstract
            ]

            if len(abstract_key_names) > 0:
                cur_fields = template.get_fields(path)
                # We want to use the default values for abstract keys. We could do this
                # by not passing the abstract keys to _apply_fields, set skip_defaults=False,
                # and let that method set the default values. But doing that would set default
                # values on all keys that have defaults. We only want to set defaults on keys
                # that were found in the current_path (the keys in cur_field)
                for abstract_key_name in abstract_key_names:
                    if abstract_key_name in cur_fields:
                        cur_fields[abstract_key_name] = template.keys[
                            abstract_key_name
                        ]._get_default()
                path = template._apply_fields(cur_fields, skip_defaults=True)
        else:
            log.debug(
                "Path does not match a template. Not translating abstract fields: %s"
                % path
            )
    return path


def _create_dependencies(tk, publish_entity, dependency_paths, dependency_ids):
    """
    Creates dependencies in shotgun from a given entity to
    a list of paths and ids. Paths not recognized are skipped.

    :param tk: API handle
    :param publish_entity: The publish entity to set the dependencies for. This is a dictionary
                           with keys type and id.
    :param dependency_paths: List of paths on disk. List of strings.
    :param dependency_ids: List of publish entity ids to associate. List of ints

    """
    published_file_entity_type = get_published_file_entity_type(tk)

    publishes = find_publish(tk, dependency_paths)

    # create a single batch request for maximum speed
    sg_batch_data = []

    for dependency_path in dependency_paths:

        # did we manage to resolve this file path against
        # a publish in shotgun?
        published_file = publishes.get(dependency_path)

        if published_file:
            if published_file_entity_type == "PublishedFile":

                req = {
                    "request_type": "create",
                    "entity_type": "PublishedFileDependency",
                    "data": {
                        "published_file": publish_entity,
                        "dependent_published_file": published_file,
                    },
                }
                sg_batch_data.append(req)

            else:  # == "TankPublishedFile"

                req = {
                    "request_type": "create",
                    "entity_type": "TankDependency",
                    "data": {
                        "tank_published_file": publish_entity,
                        "dependent_tank_published_file": published_file,
                    },
                }
                sg_batch_data.append(req)

    for dependency_id in dependency_ids:
        if published_file_entity_type == "PublishedFile":

            req = {
                "request_type": "create",
                "entity_type": "PublishedFileDependency",
                "data": {
                    "published_file": publish_entity,
                    "dependent_published_file": {
                        "type": "PublishedFile",
                        "id": dependency_id,
                    },
                },
            }
            sg_batch_data.append(req)

        else:  # == "TankPublishedFile"

            req = {
                "request_type": "create",
                "entity_type": "TankDependency",
                "data": {
                    "tank_published_file": publish_entity,
                    "dependent_tank_published_file": {
                        "type": "TankPublishedFile",
                        "id": dependency_id,
                    },
                },
            }
            sg_batch_data.append(req)

    # push to shotgun in a single xact
    if len(sg_batch_data) > 0:
        tk.shotgun.batch(sg_batch_data)


def _calc_path_cache(tk, path, project_names=None):
    r"""
    Calculates root path name and relative path (including project directory).
    returns (root_name, path_cache). The relative path is always using forward
    slashes.

    If the location cannot be computed, because the path does not belong
    to a valid root, (None, None) is returned.

    Examples:

        - Primary Root name: X:\mnt\projects
        - Project name: project_b
        - Path: X:\mnt\projects\project_b\path\to\file.ma
        - Returns: (Primary, 'project_b/path/to/file.ma')

        - Primary Root name: /mnt/projects
        - Project name: client_a/project_b
        - Path: /mnt/projects/client_a/project_b/path/to/file.ma
        - Returns: (Primary, 'client_a/project_b/path/to/file.ma')

    :param tk: Toolkit API instance
    :param str path: Path to normalize.
    :param list project_names: A list of project names used to find a matching
                               storage to calculate the path cache. If a list is
                               not provided, only the current project name will
                               be used.
    :returns: (root_name, path_cache)
    """
    # Note: paths may be c:/foo in Maya on Windows - don't rely on os.sep here!

    # normalize input path to remove double slashes etc.
    norm_path = ShotgunPath.normalize(path)

    # normalize to only use forward slashes
    norm_path = sgutils.ensure_str(norm_path.replace("\\", "/"))

    # get roots - dict keyed by storage name
    storage_roots = tk.pipeline_configuration.get_local_storage_roots()

    # get project name, typically a a-z string but can contain
    # forward slashes, e.g. 'my_project', or 'client_a/proj_b'
    if not project_names:
        project_names = [tk.pipeline_configuration.get_project_disk_name()]

    for root_name, root_path in storage_roots.items():

        root_path_obj = ShotgunPath.from_current_os_path(root_path)
        # normalize the root path
        norm_root_path = root_path_obj.current_os.replace(os.sep, "/")

        for project_name in project_names:

            # append project and normalize
            proj_path = root_path_obj.join(project_name).current_os
            proj_path = sgutils.ensure_str(proj_path.replace(os.sep, "/"))

            if norm_path.lower().startswith(proj_path.lower()):
                # our path matches this storage!

                # Remove parent dir plus "/" - be careful to handle the case where
                # the parent dir ends with a '/', e.g. 'T:/' for a Windows drive
                path_cache = norm_path[len(norm_root_path) :].lstrip("/")
                log.debug(
                    "Split up path '%s' into storage %s and relative path '%s'"
                    % (path, root_name, path_cache)
                )
                return root_name, path_cache

    # not found, return None values
    log.debug("Unable to split path '%s' into a storage and a relative path." % path)
    return None, None


def group_by_storage(tk, list_of_paths, only_current_project=True):
    r"""
    Given a list of paths on disk, groups them into a data structure suitable for
    shotgun. In shotgun, the path_cache field contains an abstracted representation
    of the publish field, with a normalized path and the storage chopped off.

    By default, paths are grouped only by storages matching the current project.
    Set only_current_project to False to group by storages matching any current
    active project in the pipeline config.

    This method aims to process the paths to make them useful for later shotgun processing.

    Returns a dictionary, keyed by storage name. Each storage in the dict contains another dict,
    with an item for each path_cache entry.

    Examples::

        ['/studio/project_code/foo/bar.0003.exr', '/secondary_storage/foo/bar']

        {'Tank':
            {'project_code/foo/bar.%04d.exr': ['/studio/project_code/foo/bar.0003.exr'] }

         'Secondary_Storage':
            {'foo/bar': ['/secondary_storage/foo/bar'] }
        }


        ['c:\studio\project_code\foo\bar', '/secondary_storage/foo/bar']

        {'Tank':
            {'project_code/foo/bar': ['c:\studio\project_code\foo\bar'] }

         'Secondary_Storage':
            {'foo/bar': ['/secondary_storage/foo/bar'] }
        }
    """
    storages_paths = {}

    # get a list of all the current tank names. We'll need it when trying to determine the root of the given paths
    if not only_current_project:
        sg_projects = tk.shotgun.find(
            "Project",
            [
                ["archived", "is", False],
                ["is_template", "is", False],
                ["tank_name", "is_not", None],
            ],
            ["tank_name"],
        )
        project_names = [p["tank_name"] for p in sg_projects]
    else:
        project_names = None

    for path in list_of_paths:

        # use abstracted path if path is part of a sequence
        abstract_path = _translate_abstract_fields(tk, path)
        root_name, dep_path_cache = _calc_path_cache(tk, abstract_path, project_names)

        # make sure that the path is even remotely valid, otherwise skip
        if dep_path_cache is None:
            continue

        # Update data for this storage
        storage_info = storages_paths.get(root_name, {})
        paths = storage_info.get(dep_path_cache, [])
        paths.append(path)
        storage_info[dep_path_cache] = paths
        storages_paths[root_name] = storage_info

    return storages_paths
