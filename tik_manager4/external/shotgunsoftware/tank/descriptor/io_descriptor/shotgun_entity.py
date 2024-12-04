# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
from tank_vendor.six.moves import urllib

from .downloadable import IODescriptorDownloadable
from ...util import filesystem, shotgun
from ...util.shotgun_entity import get_sg_entity_name_field
from ...util.errors import ShotgunAttachmentDownloadError
from ..errors import TankDescriptorError
from ... import LogManager

log = LogManager.get_logger(__name__)


class IODescriptorShotgunEntity(IODescriptorDownloadable):
    """
    Represents a shotgun entity to which apps have been attached.
    This can be an attachment field on any entity. Typically it will be
    a pipeline configuration. In that configuration, the descriptor represents
    a 'cloud based configuration'. It could also be a custom entity or non-project
    entity in the case you want to store a descriptor (app, engine or config)
    that can be easily accessed from any project.

    There are two ways of addressing an entity.

    {
     type: shotgun,
     entity_type: CustomEntity01,   # entity type
     name: tk-foo,                  # name of the record in shotgun (i.e. 'code' field)
     project_id: 123,               # optional project id. If omitted, name is assumed to be unique.
     field: sg_config,              # attachment field where payload can be found
     version: 456                   # attachment id of particular attachment
    }

    or

    {
     type: shotgun,
     entity_type: CustomEntity01,   # entity type
     id: 123,                       # id of the record in shotgun (i.e. 'id' field)
     field: sg_config,              # attachment field where payload can be found
     version: 456                   # attachment id of particular attachment
    }

    This can for example be used for attaching items to a pipeline configuration.
    Create an attachment field named sg_config, upload a zip file, and use the following
    descriptor:

    {type: shotgun, entity_type: PipelineConfiguration,
     name: primary, project_id: 123, field: sg_config, version: 1341}

    When a new zip file is uploaded, the attachment id (e.g. version) changes, resulting in
    a new descriptor.

    The latest version is defined as the current record available in Shotgun.
    """

    (_MODE_ID_BASED, _MODE_NAME_BASED) = range(2)

    def __init__(self, descriptor_dict, sg_connection, bundle_type):
        """
        Constructor

        :param descriptor_dict: descriptor dictionary describing the bundle
        :param sg_connection: Shotgun connection to associated site.
        :param bundle_type: Either AppDescriptor.APP, CORE, ENGINE or FRAMEWORK.
        :return: Descriptor instance
        """
        super(IODescriptorShotgunEntity, self).__init__(
            descriptor_dict, sg_connection, bundle_type
        )

        # ensure project id is an int if specified
        self._project_link = None
        self._project_id = None
        self._entity_id = None

        if "id" in descriptor_dict:
            self._mode = self._MODE_ID_BASED
            self._validate_descriptor(
                descriptor_dict,
                required=["type", "entity_type", "id", "version", "field"],
                optional=[],
            )

            # convert to int
            try:
                self._entity_id = int(descriptor_dict["id"])
            except ValueError:
                raise TankDescriptorError(
                    "Invalid id in descriptor %s" % descriptor_dict
                )

            if "name" in descriptor_dict:
                raise TankDescriptorError(
                    "PTR descriptor cannot contain both name and id tokens: %s"
                    % descriptor_dict
                )

        else:
            self._mode = self._MODE_NAME_BASED
            self._validate_descriptor(
                descriptor_dict,
                required=["type", "entity_type", "name", "version", "field"],
                optional=["project_id"],
            )

            self._name = descriptor_dict.get("name")

            if "project_id" in descriptor_dict:
                # convert to int
                try:
                    project_id_int = int(descriptor_dict["project_id"])
                except ValueError:
                    raise TankDescriptorError(
                        "Invalid project id in descriptor %s" % descriptor_dict
                    )

                self._project_link = {"type": "Project", "id": project_id_int}
                self._project_id = project_id_int

        self._sg_connection = sg_connection
        self._bundle_type = bundle_type
        self._entity_type = descriptor_dict.get("entity_type")
        self._field = descriptor_dict.get("field")

        # ensure version is an int if specified
        try:
            self._version = (
                int(descriptor_dict["version"])
                if "version" in descriptor_dict
                else None
            )
        except ValueError:
            raise TankDescriptorError(
                "Invalid version in descriptor %s" % descriptor_dict
            )

    def _get_bundle_cache_path(self, bundle_cache_root):
        """
        Given a cache root, compute a cache path suitable
        for this descriptor, using the 0.18+ path format.

        :param bundle_cache_root: Bundle cache root path
        :return: Path to bundle cache location
        """
        #
        # format for these paths will be
        #
        # bundle_cache/sg/SITE_NAME/AttachmentId
        #
        # bundle_cache/sg/wintermute/v25283

        # Firstly, because the bundle cache can be global, make sure we include the sg site name.
        # first, get site only; https://www.FOO.com:8080 -> www.foo.com
        base_url = (
            urllib.parse.urlparse(self._sg_connection.base_url)
            .netloc.split(":")[0]
            .lower()
        )
        # make it as short as possible for hosted sites
        base_url = base_url.replace(".shotgunstudio.com", "")

        return os.path.join(bundle_cache_root, "sg", base_url, self.get_version())

    def get_system_name(self):
        """
        Returns a short name, suitable for use in configuration files
        and for folders on disk, e.g. 'tk-maya'
        """
        if self._mode == self._MODE_NAME_BASED:
            if self._project_id:
                name = "p%s_%s" % (self._project_id, self._name)
            else:
                name = self._name

        elif self._mode == self._MODE_ID_BASED:
            # e.g. 'PipelineConfiguration_1234'
            name = "%s_%s" % (self._entity_type, self._entity_id)

        return filesystem.create_valid_filename(name)

    def get_version(self):
        """
        Returns the version number string for this item.
        In this case, this is the linked shotgun attachment id.
        """
        return "v%s" % self._version

    def _download_local(self, destination_path):
        """
        Retrieves this version to local repo.
        Will exit early if app already exists local.

        :param destination_path: The directory path to which the shotgun entity is to be
        downloaded to.
        """
        try:
            # while downloading, enable the auto detect flag. This provides
            # some additional structural flexibility, allowing for multiple
            # ways to zip up a bundle attachment.
            shotgun.download_and_unpack_attachment(
                self._sg_connection,
                self._version,
                destination_path,
                auto_detect_bundle=True,
            )
        except ShotgunAttachmentDownloadError as e:
            raise TankDescriptorError(
                "Failed to download %s from %s. Error: %s"
                % (self, self._sg_connection.base_url, e)
            )

    def get_latest_version(self, constraint_pattern=None):
        """
        Returns a descriptor object that represents the latest version.

        .. note:: The concept of constraint patterns doesn't apply to
                  shotgun attachment ids and any data passed via the
                  constraint_pattern argument will be ignored by this
                  method implementation.

        :param constraint_pattern: This parameter is unused and remains here to be compatible
            with the expected signature for this method.

        :returns: IODescriptorShotgunEntity object
        """
        if constraint_pattern:
            log.warning("%s does not support version constraint patterns." % self)

        log.debug("Finding latest version of %s..." % self)

        if self._mode == self._MODE_NAME_BASED:
            name_field = get_sg_entity_name_field(self._entity_type)

            filters = [[name_field, "is", self._name]]

            if self._project_link:
                filters.append(["project", "is", self._project_link])

        elif self._mode == self._MODE_ID_BASED:
            filters = [["id", "is", self._entity_id]]

        data = self._sg_connection.find_one(self._entity_type, filters, [self._field])

        if data is None:
            raise TankDescriptorError(
                "Cannot resolve descriptor %s in Flow Production Tracking!" % self
            )

        # attachment field is on the following form in the case a file has been
        # uploaded:
        #  {'name': 'v1.2.3.zip',
        #  'url': 'https://sg-media-usor-01.s3.amazonaws.com/...',
        #  'content_type': 'application/zip',
        #  'type': 'Attachment',
        #  'id': 139,
        #  'link_type': 'upload'}

        if data[self._field].get("link_type") != "upload":
            raise TankDescriptorError(
                "Latest version of %s is not an uploaded file: %s" % (self, data)
            )

        attachment_id = data[self._field].get("id")

        # make a descriptor dict
        if self._mode == self._MODE_NAME_BASED:
            descriptor_dict = {
                "type": "shotgun",
                "entity_type": self._entity_type,
                "field": self._field,
                "name": self._name,
                "version": attachment_id,
            }

            if self._project_link:
                descriptor_dict["project_id"] = self._project_id

        elif self._mode == self._MODE_ID_BASED:
            descriptor_dict = {
                "type": "shotgun",
                "entity_type": self._entity_type,
                "field": self._field,
                "id": self._entity_id,
                "version": attachment_id,
            }

        # and return a descriptor instance
        desc = IODescriptorShotgunEntity(
            descriptor_dict, self._sg_connection, self._bundle_type
        )
        desc.set_cache_roots(self._bundle_cache_root, self._fallback_roots)

        log.debug("Latest version resolved to %s" % desc)
        return desc

    def get_latest_cached_version(self, constraint_pattern=None):
        """
        Returns a descriptor object that represents the latest version
        that is locally available in the bundle cache search path.

        .. note:: The concept of constraint patterns doesn't apply to
                  shotgun attachment ids and any data passed via the
                  constraint_pattern argument will be ignored by this
                  method implementation.

        :param constraint_pattern: This parameter is unused and remains here to be compatible
            with the expected signature for this method.

        :returns: instance deriving from IODescriptorBase or None if not found
        """
        if constraint_pattern:
            log.warning("%s does not support version constraint patterns." % self)

        # not possible to determine what 'latest' means in this case
        # so check if the current descriptor exists on disk and in this
        # case return it
        if self.get_path():
            return self
        else:
            # no cached version exists
            return None

    def has_remote_access(self):
        """
        Probes if the current descriptor is able to handle
        remote requests. If this method returns, true, operations
        such as :meth:`download_local` and :meth:`get_latest_version`
        can be expected to succeed.

        :return: True if a remote is accessible, false if not.
        """
        # check if we can connect to Shotgun
        can_connect = True
        try:
            log.debug("%r: Probing if a connection to PTR can be established..." % self)
            self._sg_connection.connect()
            log.debug("...connection established!")
        except Exception as e:
            log.debug("...could not establish connection: %s" % e)
            can_connect = False
        return can_connect
