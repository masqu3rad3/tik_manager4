"""Main module for the Kitsu integration."""
import importlib
import logging
import json
import sys
import os
from pathlib import Path
from copy import deepcopy
from datetime import datetime

from tik_manager4.core.cryptor import CryptorError
from tik_manager4.core.cryptor import Cryptor
from tik_manager4.core import utils
from tik_manager4.management.management_core import ManagementCore
from tik_manager4.management.enums import EventType
from tik_manager4.management.exceptions import AuthenticationError, SyncError

from tik_manager4.management.kitsu.ui import login


external_folder = Path(__file__).parents[2] / "external"

kitsu_folder = (external_folder / "kitsu").as_posix()

if kitsu_folder not in sys.path:
    sys.path.append(kitsu_folder)

from requests.exceptions import ConnectionError
from gazu.exception import ServerErrorException

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
CRYPTOR = Cryptor()

class ProductionPlatform(ManagementCore):
    """Main class for Kitsu integration."""

    metadata_pairing = {
        "frame_in": "start_frame",
        "frame_out": "end_frame",
        "fps": "fps",
    }

    nice_name = "Kitsu"
    name = "kitsu"
    lock_subproject_creation = True
    lock_task_creation = True

    def __init__(self, tik_main_obj):
        self.tik_main = tik_main_obj
        # self.sg = None
        self.gazu = None
        self.is_authenticated = False
        self.user = None

    @property
    def host(self):
        return self.tik_main.user.commons.management_settings.get("kitsu_url")

    @property
    def host_api(self):
        host = self.host
        # if it is ending with a slash, remove it
        if host.endswith("/"):
            host = host[:-1]
        return f"{host}/api"

    def authenticate(self):
        """Authenticate the user."""
        self.gazu = importlib.import_module("gazu")
        self.gazu.set_host(self.host_api)
        os.environ["CGWIRE_HOST"] = self.host_api
        # first check if there is a token stored in resume settings.
        token = self.tik_main.user.resume.get("kitsu_token")
        kitsu_user = self.tik_main.user.resume.get("kitsu_user") # this may not be the same with the tik user.
        if token and kitsu_user:
            try:
                self.gazu.log_in(kitsu_user, CRYPTOR.decrypt(token))
            except (ConnectionError, CryptorError) as exc:
                # get rid of the token and force the user to login again.
                self.logout()
                self.authenticate()
        else:
            try:
                login_widget = login.Login(self.gazu)
                ret = login_widget.exec_()
                if not ret:
                    return None, "Canceled by user."
                is_remember = login_widget.inputs["remember"].isChecked()
                if is_remember:
                    crypted_token = CRYPTOR.encrypt(login_widget.inputs["password"].text())
                    self.tik_main.user.resume.edit_property("kitsu_token", crypted_token)
                    self.tik_main.user.resume.edit_property("kitsu_user", login_widget.inputs["user"].text())
            except ConnectionError as exc:
                return None, f"Connection Error: {exc}"

        self.is_authenticated = self.gazu.user.is_authenticated()
        if not self.is_authenticated:
            return None, "Authentication Failed."

        return self.gazu, "Success"

    def logout(self):
        """Logout the user."""
        if self.is_authenticated:
            self.gazu.log_out()
        self.tik_main.user.resume.edit_property("kitsu_token", None)
        self.tik_main.user.resume.edit_property("kitsu_user", None)
        self.is_authenticated = False

    def get_projects(self, archived: bool = False, is_template: bool = False,
                     is_demo: bool = False) -> list:
        """Get all the projects from Kitsu."""
        projects = self.gazu.project.all_projects()
        # get the thumbnails and add the data to the dictionary
        status_mapping = self._get_status_mapping()
        for project_data in projects:
            project_data["image_authorization_headers"] = self.gazu.client.make_auth_header()
            project_data["image"] = f"{self.gazu.get_host()}/pictures/thumbnails/projects/{project_data['id']}.png"
            project_data["status"] = status_mapping.get(project_data["project_status_id"], "")

        return projects

    def _get_status_mapping(self, force=False):
        """Get the status mapping."""
        status_mapping = os.environ.get("TIK_KITSU_STATUS_MAPPING")
        # get it from the environment variable if its set.
        if status_mapping and not force:
            # replace all single quotes with double quotes
            status_mapping = status_mapping.replace("'", '"')
            return json.loads(status_mapping)
        all_status_list = self.gazu.project.all_project_status()
        status_mapping = {}
        for status_data in all_status_list:
            status_mapping[status_data["id"]] = status_data["name"]
        os.environ["TIK_KITSU_STATUS_MAPPING"] = json.dumps(status_mapping)

        return status_mapping

    def get_all_assets(self, project_id):
        """Get all the assets from a project."""
        return self.gazu.asset.all_assets_for_project(project_id)

    def get_all_episodes(self, project_id):
        """Get all the episodes from a project."""
        return self.gazu.shot.all_episodes_for_project(project_id)

    def get_all_sequences(self, project_id):
        """Get all the sequences from a project."""
        return self.gazu.shot.all_sequences_for_project(project_id)

    def get_all_shots(self, project_id):
        """Get all the shots from a project."""
        return self.gazu.shot.all_shots_for_project(project_id)

    def force_sync(self, project_id=None):
        """Force the sync of the project.

        Args:
            project_id (str, optional): The project ID to sync. If not provided,
                attempts to get it from the project database. Defaults to None.

        Raises:
            Exception: If the project is not linked to a Shotgrid project.
        """
        sync_stamp = self.date_stamp()

        project_id = project_id or self.tik_main.project.settings.get("host_project_id")
        if not project_id:
            LOG.error("Project is not linked to a Kitsu project.")
            return False, "Project is not linked to a Kitsu project."

        management_platform = self.tik_main.project.settings.get("management_platform")
        if management_platform != "kitsu":
            LOG.error("Project is not linked to a Kitsu project.")
            return False, "Project is not linked to a Kitsu project."

        all_assets = self.get_all_assets(project_id)
        all_episodes = self.get_all_episodes(project_id)
        all_sequences = self.get_all_sequences(project_id)
        all_shots = self.get_all_shots(project_id)

        assets_sub = self._get_assets_sub()
        shots_sub = self._get_shots_sub()

        for asset in all_assets:
            sync_block = SyncBlock(self.gazu, self.tik_main, project_id)
            sync_block.event_type = EventType.NEW_ASSET
            sync_block.kitsu_data = asset
            sync_block.subproject = assets_sub
            sync_block.execute()

        for episode in all_episodes:
            sync_block = SyncBlock(self.gazu, self.tik_main, project_id)
            sync_block.event_type = EventType.NEW_EPISODE
            sync_block.kitsu_data = episode
            sync_block.subproject = shots_sub
            sync_block.execute()

        for sequence in all_sequences:
            sync_block = SyncBlock(self.gazu, self.tik_main, project_id)
            sync_block.event_type = EventType.NEW_SEQUENCE
            sync_block.kitsu_data = sequence
            sync_block.subproject = shots_sub
            sync_block.execute()

        for shot in all_shots:
            sync_block = SyncBlock(self.gazu, self.tik_main, project_id)
            sync_block.event_type = EventType.NEW_SHOT
            sync_block.kitsu_data = shot
            sync_block.subproject = shots_sub
            sync_block.execute()

        self.tik_main.project.settings.edit_property("last_sync", sync_stamp)
        self.tik_main.project.settings.apply_settings(force=True)

        return True, "Success"

    def _get_assets_sub(self):
        """Get the 'Assets' sub from the tik project.

        Creates if it doesn't exist.
        """
        # TODO: should go to the base class
        assets_sub = self.tik_main.project.subs.get("Assets") or self.tik_main.project.create_sub_project(
            "Assets", parent_path="", mode="asset"
        )
        return assets_sub

    def _get_shots_sub(self):
        """Get the 'Shots' sub from the tik project.

        Creates if it doesn't exist.
        """
        # TODO: should go to the base class
        shots_sub = self.tik_main.project.subs.get("Shots") or self.tik_main.project.create_sub_project(
            "Shots", parent_path="", mode="shot"
        )
        return shots_sub

    def _get_categories(self, project):
        """Collect the categories from the kitsu server."""
        all_task_types = self.gazu.task.all_task_types_for_project(project)
        asset_categories = []
        shot_categories = []
        for task_type in all_task_types:
            for_entity = task_type.get("for_entity")
            if for_entity in ["Asset"]:
                name = task_type.get("short_name") or task_type.get("name")
                asset_categories.append(name)

            if for_entity in ["Shot", "Sequence"]:
                name = task_type.get("short_name") or task_type.get("name")
                shot_categories.append(name)

        return asset_categories, shot_categories

    def create_from_project(self, project_root, kitsu_project_id, set_project=True):
        """Create a tik manager project from a kitsu project."""

        # do the sync stamp earliest as possible not to miss any changes
        sync_stamp = self.date_stamp()

        current_project_path = self.tik_main.project.absolute_path
        project = self.gazu.project.get_project(kitsu_project_id)

        project_name = utils.sanitize_text(project["name"])
        project_path = Path(project_root) / project_name
        project_path.mkdir(exist_ok=True)
        ret = self.tik_main.create_project(
            project_path.as_posix(), structure_template="empty",
            set_after_creation=True # we ALWAYS set it for further operations
        )
        if ret == -1:
            return None

        # all_assets = self.get_all_assets(kitsu_project_id)
        # all_episodes = self.get_all_episodes(kitsu_project_id)
        # all_sequences = self.get_all_sequences(kitsu_project_id)
        # all_shots = self.get_all_shots(kitsu_project_id)
        #
        # assets_sub = self._get_assets_sub()
        # shots_sub = self._get_shots_sub()

        asset_categories, shot_categories = self._get_categories(project)

        ## TODO: move to the base class
        # Add the categories that doesnt exists in common
        _salvage_dict = deepcopy(
            self.tik_main.user.commons.category_definitions.get_data()
        )
        new_dict = {}
        for category in asset_categories + shot_categories:
            # if the category in both asset and shot categories, _type should be ""
            # if only in asset_categories, _type should be "asset" or "shot" if only in shot_categories
            if category in asset_categories and category in shot_categories:
                _type = ""
            elif category in asset_categories:
                _type = "asset"
            elif category in shot_categories:
                _type = "shot"

            if category in _salvage_dict.keys():
                new_dict[category] = _salvage_dict[category]
                new_dict[category]["type"] = _type
            else:
                new_dict[category] = {
                    "type": _type,
                    "validations": [],
                    "extracts": ["source"],
                }

        self.tik_main.project.category_definitions.set_data(new_dict)
        self.tik_main.project.category_definitions.apply_settings(force=True)
        # TODO: move to the base class [END]

        # tag the project as management driven
        self.tik_main.project.settings.edit_property("management_driven", True)
        self.tik_main.project.settings.edit_property("management_platform", "kitsu")
        self.tik_main.project.settings.edit_property("host_project_name", project["name"])
        self.tik_main.project.settings.edit_property("host_project_id", kitsu_project_id)
        self.tik_main.project.settings.edit_property("last_sync", sync_stamp)

        self.tik_main.project.settings.apply_settings(force=True)

        self.force_sync(project_id=kitsu_project_id)

        if not set_project: # switch back to the original project
            self.tik_main.set_project(current_project_path)

        return project_path

    def _get_sync_blocks(self, project, assets_sub, shots_sub, asset_categories, shot_categories):
        """Get the latest events and return the probable sync blocks."""
        last_sync = self.tik_main.project.settings.get("last_sync")
        parsed_time = datetime.strptime(last_sync,"%Y-%m-%dT%H:%M:%SZ")
        formatted_time = parsed_time.strftime("%Y-%m-%dT%H:%M:%S")
        events = self.gazu.sync.get_last_events(project=project, after=formatted_time)

        valid_event_types = ["asset:new", "shot:new", "sequence:new",
                             "asset:delete", "shot:delete", "sequence:delete",
                             "asset:update", "shot:update", "sequence:update",
                             "task:new", "task:delete"]
        for event in reversed(events):

            event_type = event.get("name")
            if event_type not in valid_event_types:
                continue
            try:
                sync_block = SyncBlock(self.gazu, self.tik_main, project)
                if event_type == "asset:new":
                    sync_block.event_type = EventType.NEW_ASSET
                    asset_data = self.gazu.asset.get_asset(event["data"]["asset_id"])
                    sync_block.kitsu_data = asset_data
                    sync_block.subproject = assets_sub
                    # sync_block.categories = asset_categories
                elif event_type == "shot:new":
                    sync_block.event_type = EventType.NEW_SHOT
                    shot_data = self.gazu.shot.get_shot(event["data"]["shot_id"])
                    sync_block.kitsu_data = shot_data
                    sync_block.subproject = shots_sub
                    # sync_block.categories = shot_categories
                elif event_type == "sequence:new":
                    sync_block.event_type = EventType.NEW_SEQUENCE
                    sequence_data = self.gazu.shot.get_sequence(event["data"]["sequence_id"])
                    sync_block.kitsu_data = sequence_data
                    sync_block.subproject = shots_sub
                elif event_type == "asset:update":
                    sync_block.event_type = EventType.UPDATE_ASSET
                    asset_data = self.gazu.asset.get_asset(event["data"]["asset_id"])
                    sync_block.kitsu_data = asset_data
                elif event_type == "shot:update":
                    sync_block.event_type = EventType.UPDATE_SHOT
                    shot_data = self.gazu.shot.get_shot(event["data"]["shot_id"])
                    sync_block.kitsu_data = shot_data
                elif event_type == "sequence:update":
                    sync_block.event_type = EventType.UPDATE_SEQUENCE
                    sequence_data = self.gazu.shot.get_sequence(event["data"]["sequence_id"])
                    sync_block.kitsu_data = sequence_data
                elif event_type == "asset:delete":
                    # if the asset deleted we cannot request the kitsu data.
                    sync_block.event_type = EventType.DELETE_ASSET
                    sync_block.kitsu_data = event
                elif event_type == "shot:delete":
                    # if the shot deleted we cannot request the kitsu data.
                    sync_block.event_type = EventType.DELETE_SHOT
                    sync_block.kitsu_data = event
                elif event_type == "sequence:delete":
                    # if the sequence deleted we cannot request the kitsu data.
                    sync_block.event_type = EventType.DELETE_SEQUENCE
                    sync_block.kitsu_data = event
                elif event_type == "task:new":
                    task_data = self.gazu.task.get_task(event["data"]["task_id"])
                    sync_block.event_type = EventType.NEW_TASK
                    sync_block.kitsu_data = task_data # this is the task data
                elif event_type == "task:delete":
                    # task_data = self.gazu.task.get_task(event["data"]["task_id"])
                    # if the tasks is deleted, we cannot reach the task data.
                    # in this case. we will use the event data.
                    sync_block.event_type = EventType.DELETE_TASK
                    sync_block.kitsu_data = event
            except self.gazu.exception.RouteNotFoundException:
                LOG.warning(f"Route not found for event: {event}", exc_info=True, stack_info=True)
                continue

            yield sync_block

    def sync_project(self):
        """Sync the project with the Kitsu project."""
        project_id = self.tik_main.project.settings.get("host_project_id")
        if not project_id:
            raise SyncError("Project is not linked to a Kitsu project.")
        project = self.gazu.project.get_project(project_id)
        if not project:
            raise SyncError(f"Project ID {project_id} not found in Kitsu host.")

        asset_categories, shot_categories = self._get_categories(project)

        assets_sub = self._get_assets_sub()
        shots_sub = self._get_shots_sub()

        sync_blocks = self._get_sync_blocks(project,
                                            assets_sub,
                                            shots_sub,
                                            asset_categories,
                                            shot_categories
                                            )

        for sync_block in sync_blocks:
            sync_block.execute()

        # Update the last sync date
        self.tik_main.project.settings.edit_property("last_sync", self.date_stamp())
        self.tik_main.project.settings.apply_settings(force=True)

        return sync_blocks

    def request_tasks(self, entity_id, entity_type, step=None, project_id=None):
        """Request the tasks from the Kitsu server."""
        if entity_type.lower() == "asset":
            return self.gazu.task.all_tasks_for_asset(entity_id)
        elif entity_type.lower() == "shot":
            # this can be a shot or a sequence
            try:
                return self.gazu.task.all_tasks_for_shot(entity_id)
            except self.gazu.exception.RouteNotFoundException:
                try:
                    return self.gazu.task.all_tasks_for_sequence(entity_id)
                except self.gazu.exception.RouteNotFoundException:
                    LOG.warning("Cannot find the tasks for the entity.", exc_info=True)
                    return []


    def get_available_status_lists(self, force=False):
        """Return the available status lists."""
        raw_dict_list = self.gazu.task.all_task_statuses()
        status_values = []
        for status_dict in raw_dict_list:
            if status_dict["is_artist_allowed"]:
                status_values.append(status_dict["name"])
        return status_values

    @staticmethod
    def get_settings_ui():
        """Return the settings UI for the Shotgrid platform."""
        # Make sure the keys are unique accross all other platforms
        return {
            "_kitsu": {
                "type": "separator",
                "display_name": "Kitsu Settings",
            },
            "kitsu_url": {
                "display_name": "Kitsu Host URL",
                "tooltip": "The URL of the Kitsu server to connect to.",
                "type": "string",
                "value": "",
            },
            "skip_empty_entity_names": {
                "display_name": "Skip Blank Entities During Sync",
                "tooltip": "If an Asset or Shot has an empty name, it will be skipped during initial project creation or sync. Otherwise, id will be used as the name.",
                "type": "boolean",
                "value": False,
            }
        }

    def get_entity_url(self, entity_type, entity_id):
        """Return the URL of the entity."""
        url = None
        try:
            if entity_type.lower() == "asset":
                url = self.gazu.asset.get_asset_url(entity_id)
            else:
                try:
                    url = self.gazu.shot.get_shot_url(entity_id)
                except self.gazu.exception.RouteNotFoundException:
                    try:
                        url = self.gazu.shot.get_sequence_url(entity_id)
                    except self.gazu.exception.RouteNotFoundException:
                        raise ValueError("Invalid entity type.")
        except (ServerErrorException, self.gazu.exception.RouteNotFoundException):
            LOG.warning("Server Error while getting the URL.", exc_info=True)
        return url

    def _get_status_id_from_name(self, status_name):
        """Get the status ID from the status name."""
        status_dict_list = self.gazu.task.all_task_statuses()
        for status_dict in status_dict_list:
            if status_dict["name"] == status_name:
                return status_dict["id"]
        return None

    def publish_version(self,
                        task_id,
                        status=None,
                        description="",
                        thumbnail=None,
                        preview: str =None,
                        publish_version: int = None,
                        **kwargs
                        ):
        """Publish a version to Kitsu using gazu.

        Args:
            task_id (str): The ID of the task.
            status (str, optional): The status that the task will be turned to.
                If not specified, current status stays.
            description (str, optional): The description of the version. Defaults to "".
            thumbnail (str, optional): The path to the thumbnail file. Defaults to None.
            preview (str, optional): The path to the preview file. Defaults to None.
            publish_version (int, optional): The version number to publish.
                Defaults to None.

        Returns:
            dict: The published version data.
        """
        # pylint: disable=too-many-arguments

        # we only need the task_id for the publish
        # get the status_id

        task_dict = self.gazu.task.get_task(task_id)
        status_id = self._get_status_id_from_name(status)

        if not status_id:
            status_id = task_dict["task_status_id"] # we are not changing the status

        new_comment = self.gazu.task.add_comment(
            task_dict,
            status_id,
            comment=description,
            person=self.gazu.client.get_current_user()
        )

        if thumbnail or preview:
            _preview_file = self.gazu.task.add_preview(
                task_dict,
                new_comment,
                preview_file_path = preview or thumbnail,
                normalize_movie = True,
                revision = publish_version
            )

        return {"id": new_comment["object_id"]}

class SyncBlock:
    """Class to store and execute sync blocks."""
    metadata_pairing = {
        "frame_in": "start_frame",
        "frame_out": "end_frame",
        "fps": "fps",
    }

    def __init__(self, gazu_instance, tik_main, project):

        self.function_mapping = {
            EventType.NEW_ASSET: self._new_asset,
            EventType.NEW_SHOT: self._new_shot,
            EventType.NEW_SEQUENCE: self._new_sequence,
            EventType.NEW_EPISODE: self._new_episode,
            EventType.UPDATE_ASSET: self._update_asset,
            EventType.UPDATE_SHOT: self._update_shot,
            EventType.UPDATE_SEQUENCE: self._update_sequence,
            EventType.UPDATE_EPISODE: self._update_episode,
            EventType.DELETE_ASSET: self._delete_asset,
            EventType.DELETE_SHOT: self._delete_shot,
            EventType.DELETE_SEQUENCE: self._delete_sequence,
            EventType.DELETE_EPISODE: self._delete_episode,
            EventType.NEW_TASK: self._new_task,
            EventType.DELETE_TASK: self._delete_task
        }

        self.gazu = gazu_instance
        self.tik_main = tik_main
        self.project = project
        self._event_type = None
        self._kitsu_data = None
        self._subproject = None
        self._categories = None
        self._skip_empty_entity_names = self.tik_main.user.commons.management_settings.get("skip_empty_entity_names")
        self._validate_hierarchy = True # if True, it will validate existing of the parent entities

    @property
    def event_type(self):
        return self._event_type

    @event_type.setter
    def event_type(self, value):
        # Error if its not a valid event type
        if value not in EventType:
            raise ValueError("Invalid event type.")
        self._event_type = value

    @property
    def kitsu_data(self):
        """The data represented as in Kitsu.

        This can be a kitsu-shot, kitsu-asset or kitsu-task.
        """
        return self._kitsu_data

    @kitsu_data.setter
    def kitsu_data(self, value):
        """Set the Kitsu data."""
        self._kitsu_data = value

    @property
    def subproject(self):
        """The subproject that the sync block is associated with.

        Usually the "Assets" or "Shots" subproject.
        """
        return self._subproject

    @subproject.setter
    def subproject(self, value):
        """Set the subproject."""
        self._subproject = value

    @property
    def categories(self):
        """The categories that will be used when creating a new tik task.

        Can be asset or shot categories.
        """
        return self._categories

    @categories.setter
    def categories(self, value):
        """Set the categories."""
        self._categories = value

    def execute(self):
        """Execute the sync block."""
        self.function_mapping[self.event_type]()

    def _new_asset(self):
        """Create a new asset in the tik project from the Kitsu data."""
        # this requires the asset data, asset subproject and asset categories to be defined.
        # TODO: Validate the data

        asset_id = self.kitsu_data["id"]
        asset_name = self.kitsu_data["name"]
        if not asset_name:
            if self._skip_empty_entity_names:
                return None
            asset_name = asset_id
        asset_type_dict = self.gazu.entity.get_entity_type(self.kitsu_data["entity_type_id"])
        asset_type = asset_type_dict.get("name", None)

        if asset_type:
            if self.subproject.subs.get(asset_type) is None:
                sub = self.tik_main.project.create_sub_project(
                    asset_type, parent_path="Assets"
                )
            else:
                sub = self.tik_main.project.subs["Assets"].subs[asset_type]
        else:
            sub = self.subproject

        asset_name = utils.sanitize_text(asset_name)

        metadata_overrides = self._retrieve_metadata_overrides(
            self.kitsu_data.get("data"))

        task = sub.find_task_by_id(asset_id, query_all=True)

        if task == -1:
            category_names = self.__get_asset_categories(asset_id)
            task = sub.add_task(
                asset_name,
                categories=category_names,
                metadata_overrides=metadata_overrides,
                uid=asset_id,
                force_edit=True
            )
        else:
            self._update_asset()

        if task == -1:
            LOG.warning(f"Task creation failed for {asset_name}")
            return None

        if self.kitsu_data["canceled"]:
            task.omit()
        else:
            task.revive()

        return task

    def _new_shot(self):
        """Create a new shot in the tik project from the Kitsu data."""
        # this requires the shot data, shot subproject and shot categories to be defined.
        # TODO: Validate the data
        shot_id = self.kitsu_data["id"]
        shot_name = self.kitsu_data["name"]
        if not shot_name:
            if self._skip_empty_entity_names:
                return None
            shot_name = shot_id
        # sequence = self.gazu.entity.get_entity(self.kitsu_data["parent_id"])
        kitsu_sequence = self.gazu.shot.get_sequence(self.kitsu_data["parent_id"])
        query_sub = self.subproject

        # check the sequence tik-task is there or not. Assume the subs are created if the task is there.
        sequence_tik_task = query_sub.find_task_by_id(self.kitsu_data["parent_id"], query_all=True)
        if sequence_tik_task == -1:
            # create the sequence
            sequence_task, query_sub = self._new_sequence(data=kitsu_sequence)
        else:
            query_sub = sequence_tik_task.parent_sub

        metadata_overrides = self._retrieve_metadata_overrides(self.kitsu_data.get("data"))
        metadata_overrides.update({"mode": "shot"})

        task = query_sub.find_task_by_id(shot_id, query_all=True)

        if task == -1:
            category_names = self.__get_shot_categories(shot_id)
            task = query_sub.add_task(
                shot_name,
                categories=category_names,
                metadata_overrides=metadata_overrides,
                uid=shot_id,
                force_edit=True
            )
        else:
            self._update_shot()

        if task == -1:
            LOG.warning(f"Task creation failed for {shot_name}")
            return None

        if self.kitsu_data["canceled"]:
            task.omit()
        else:
            task.revive()

        return task

    def _new_sequence(self, data=None):
        """Create a new sequence in the tik project from the Kitsu data.

        Args:
            data (dict, optional): The data of the episode. If not provided the
                class variable will be used instead. Defaults to None.
        """
        data = data or self.kitsu_data
        # check if the sequence is episodic or not
        episode_id = data.get("parent_id", None)
        query_sub = self.subproject
        if episode_id:
            episode = self.gazu.shot.get_episode(episode_id)
            episode_tik_task = self.tik_main.project.find_task_by_id(episode_id)
            if episode_tik_task == -1:
                episode_tik_task, query_sub = self._new_episode(data=episode)
            else:
                query_sub = episode_tik_task.parent_sub

        return self.__new_supreme_entity(
            data["name"],
            data["id"],
            "Sequence",
            query_sub,
            metadata_overrides=self._retrieve_metadata_overrides(
                data.get("data")),
            is_canceled=data.get("canceled", False)
        )

    def _new_episode(self, data=None):
        """Create a new episode in the tik project from the Kitsu data.

        Args:
            data (dict, optional): The data of the episode. If not provided the
                class variable will be used instead. Defaults to None.

        """
        data = data or self.kitsu_data

        return self.__new_supreme_entity(
            data["name"],
            data["id"],
            "Episode",
            self.subproject,
            metadata_overrides=self._retrieve_metadata_overrides(data.get("data")),
            is_canceled=data.get("canceled", False)
        )


    def __new_supreme_entity(self,
                             entity_name,
                             entity_id,
                             entity_type,
                             query_sub,
                             metadata_overrides=None,
                             is_canceled=False
                             ):
        """Convenience function for creating new supreme entities (episode and sequence)"""
        metadata_overrides = metadata_overrides or {}
        if not entity_name:
            if self._skip_empty_entity_names:
                return None

        tik_subproject_name = utils.sanitize_text(entity_name)
        if query_sub.subs.get(tik_subproject_name) is None:
            query_sub = self.tik_main.project.create_sub_project(
                tik_subproject_name,
                parent_path=query_sub.path,
                mode=entity_type.lower()
            )
        else:
            query_sub = query_sub.subs[tik_subproject_name]

        # we override the episode tik-task to be a shot.
        metadata_overrides.update({"mode": "shot"})

        query_sub.scan_tasks()
        task = query_sub.all_tasks.get(tik_subproject_name, None)
        if not task:
            category_names = self._get_entity_categories(entity_id, entity_type)
            task = query_sub.add_task(
                entity_name,
                categories=category_names,
                uid=entity_id,
                metadata_overrides=metadata_overrides,
            )
            if task == -1:
                return None

        if is_canceled:
            task.omit()
        else:
            task.revive()
        return task, query_sub

    def _update_asset(self):
        """"Sync the properties of the asset with the one in Kitsu Server.

        This function assumes that the asset is already in the tik project.
        """
        asset_id = self.kitsu_data["id"]
        tik_task = self.tik_main.project.find_task_by_id(asset_id)

        category_names = self.__get_asset_categories(asset_id)
        existing_categories = tik_task.categories.keys()
        for category in category_names:
            if category not in existing_categories:
                tik_task.add_category(category)

        if self.kitsu_data["canceled"]:
            tik_task.omit()
        else:
            tik_task.revive()

    def _update_shot(self):
        """Sync the properties of the shot with the one in Kitsu Server.

        This function assumes that the shot is already in the tik project.
        """
        shot_id = self.kitsu_data["id"]
        tik_task = self.tik_main.project.find_task_by_id(shot_id)

        category_names = self.__get_shot_categories(shot_id)
        existing_categories = tik_task.categories.keys()
        for category in category_names:
            if category not in existing_categories:
                tik_task.add_category(category)

        if self.kitsu_data["canceled"]:
            tik_task.omit()
        else:
            tik_task.revive()

        metadata_overrides = self._retrieve_metadata_overrides(self.kitsu_data.get("data"))

        for key, value in metadata_overrides.items():
            if value:
                tik_task._metadata_overrides[key] = value
            elif tik_task._metadata_overrides.get(key):
                tik_task._metadata_overrides.pop(key)

        tik_task.edit_property("metadata_overrides", tik_task._metadata_overrides)
        tik_task.apply_settings()

    def _update_sequence(self):
        """Sync the properties of the sequence with the one in Kitsu Server."""
        sequence_id = self.kitsu_data["id"]
        tik_task = self.tik_main.project.find_task_by_id(sequence_id)

        category_names = self.__get_sequence_categories(sequence_id)
        existing_categories = tik_task.categories.keys()
        for category in category_names:
            if category not in existing_categories:
                tik_task.add_category(category)

        if self.kitsu_data["canceled"]:
            tik_task.omit()
        else:
            tik_task.revive()

        metadata_overrides = self._retrieve_metadata_overrides(self.kitsu_data.get("data"))

        for key, value in metadata_overrides.items():
            if value:
                tik_task._metadata_overrides[key] = value
            elif tik_task._metadata_overrides.get(key):
                tik_task._metadata_overrides.pop(key)

        tik_task.edit_property("metadata_overrides", tik_task._metadata_overrides)
        tik_task.apply_settings()

    def _update_episode(self):
        """Sync the properties of the episode with the one in Kitsu Server."""
        pass

    def _delete_asset(self):
        """Omit the asset-task from the tik project."""
        entity_id = self.kitsu_data["data"]["asset_id"]
        tik_task = self.tik_main.project.find_task_by_id(entity_id)
        if tik_task == -1:
            return
        tik_task.omit()

    def _delete_shot(self):
        """Omit the shot-task from the tik project.
        Example kitsu_data (coming from the event):
        {
        'created_at': '2025-02-20T01:47:14',
              'data': {
                  'project_id': '359f08e0-8905-4c21-a37f-9b1b5bcfebe0',
                  'shot_id': '2e158c17-f46b-4339-848a-63e077e9dbe4'
                  },
              'id': '1a89bf60-4922-48a6-9bb5-01275ee6bcc8',
              'name': 'shot:delete',
              'user_id': 'fd16bb80-3bb2-45e2-ac72-877ecdc7a3a7'
        }
        """
        entity_id = self.kitsu_data["data"]["shot_id"]
        tik_task = self.tik_main.project.find_task_by_id(entity_id)
        if tik_task == -1:
            return
        tik_task.omit()

    def _delete_sequence(self):
        """Omit the shot-task from the tik project.
        Example kitsu_data (coming from the event):
        {
        'created_at': '2025-02-20T01:47:14',
              'data': {
                  'project_id': '359f08e0-8905-4c21-a37f-9b1b5bcfebe0',
                  'sequence_id': 'a8e4198e-8894-4da3-950c-80c598303ef6'
                  },
              'id': '94559de1-fd95-4867-89b8-fc68fe8b6c46',
              'name': 'sequence:delete',
              'user_id': 'fd16bb80-3bb2-45e2-ac72-877ecdc7a3a7'
        }
        """
        entity_id = self.kitsu_data["data"]["sequence_id"]
        tik_task = self.tik_main.project.find_task_by_id(entity_id)
        if tik_task == -1:
            return
        tik_task.omit()

    def _delete_episode(self):
        """Omit the episode-task from the tik project."""
        entity_id = self.kitsu_data["data"]["episode_id"]
        tik_task = self.tik_main.project.find_task_by_id(entity_id)
        if tik_task == -1:
            return
        tik_task.omit()

    def __get_tik_task_from_kitsu_task_data(self, entity_id, entity_type=None):
        """Get the corresponding tik task (one level up) from the kitsu task."""
        # it the entity type is not provided, we will try to both asset and shot
        if not entity_type:
            try:
                parent_kitsu_entity = self.gazu.asset.get_asset(entity_id)
            except self.gazu.exception.RouteNotFoundException:
                try:
                    parent_kitsu_entity = self.gazu.shot.get_shot(entity_id)
                except self.gazu.exception.RouteNotFoundException:
                    try:
                        parent_kitsu_entity = self.gazu.shot.get_sequence(entity_id)
                    except self.gazu.exception.RouteNotFoundException:
                        LOG.error(f"Entity with id:{entity_id} not found in Kitsu.")
                        return None
        else:
            if entity_type == "Asset":
                parent_kitsu_entity = self.gazu.asset.get_asset(entity_id)
            elif entity_type == "Shot":
                parent_kitsu_entity = self.gazu.shot.get_shot(entity_id)
            elif entity_type == "Sequence":
                parent_kitsu_entity = self.gazu.shot.get_sequence(entity_id)
            else:
                LOG.error(f"Unknown entity type ({entity_type}). Skipping the task with id:{entity_id}.")
                return None
        tik_task = self.tik_main.project.find_task_by_id(parent_kitsu_entity["id"])
        if tik_task == -1:
            return None
        return tik_task

    def _new_task(self):
        """Create a new category under the corresponding tik-task for the new kitsu-task."""

        # Kitsu tasks are equivalent to tik categories
        entity_name = self.kitsu_data["task_type"]["name"]
        entity_id = self.kitsu_data["entity_id"]
        entity_type = self.kitsu_data["task_type"]["for_entity"]
        tik_task = self.__get_tik_task_from_kitsu_task_data(entity_id, entity_type)
        if not tik_task:
            return
        tik_task.add_category(entity_name)

    def _delete_task(self):
        """Omit everything under the category when the kitsu-task deleted.
        Example kitsu_data (coming from the event):
        {'created_at': '2025-02-19T22:45:54',
        'data': {
                'entity_id': '8308c5a6-966a-43c7-bcf6-7f8c113119ba',
                'project_id': '359f08e0-8905-4c21-a37f-9b1b5bcfebe0',
                'task_id': '20986a22-1a45-46d4-9791-fcec982f0c2d',
                'task_type_id': 'c58805e4-7e38-4b35-bb9b-89c2e5ea4569'
                },
        'id': 'bf114c1b-c970-4b8a-969d-b4b3c28a042e',
        'name': 'task:delete',
        'user_id': 'fd16bb80-3bb2-45e2-ac72-877ecdc7a3a7'}
        """
        # We are not deleting anything. Instead, we omit any work associated with the task.
        # This is because we don't want to delete the work done by the artists.
        entity_id = self.kitsu_data["data"]["entity_id"]
        tik_task = self.__get_tik_task_from_kitsu_task_data(entity_id=entity_id)
        if not tik_task:
            return
        # get the kitsu task type by task_type_id
        kitsu_task_type = self.gazu.task.get_task_type(self.kitsu_data["data"]["task_type_id"])
        if not kitsu_task_type:
            LOG.error(f"Task type with id:{self.kitsu_data['data']['task_type_id']} not found in Kitsu.")
            return
        category_name = kitsu_task_type["name"]
        category_obj = tik_task.categories.get(category_name, None)
        if not category_obj:
            return

        for work in category_obj.works.values():
            work.omit()


    def _get_entity_categories(self, entity_id, entity_type):
        """Get the categories of the entity."""
        if entity_type.lower() == "asset":
            return self.__get_asset_categories(entity_id)
        elif entity_type.lower() == "shot":
            return self.__get_shot_categories(entity_id)
        elif entity_type.lower() == "sequence":
            return self.__get_sequence_categories(entity_id)
        elif entity_type.lower() == "episode":
            return self.__get_episode_categories(entity_id)
        else:
            raise ValueError("Invalid entity type.")

    def __get_asset_categories(self, asset_id):
        """Get the asset categories from the Kitsu server."""
        all_tasks = self.gazu.task.all_tasks_for_asset(asset_id)
        return [task["task_type_name"] for task in all_tasks]

    def __get_shot_categories(self, shot_id):
        """Get the shot categories from the Kitsu server."""
        all_tasks = self.gazu.task.all_tasks_for_shot(shot_id)
        return [task["task_type_name"] for task in all_tasks]

    def __get_sequence_categories(self, sequence_id):
        """Get the sequence categories from the Kitsu server."""
        all_tasks = self.gazu.task.all_tasks_for_sequence(sequence_id)
        return [task["task_type_name"] for task in all_tasks]

    def __get_episode_categories(self, episode_id):
        """Get the episode categories from the Kitsu server."""
        all_tasks = self.gazu.task.all_tasks_for_episode(episode_id)
        return [task["task_type_name"] for task in all_tasks]

    def _retrieve_metadata_overrides(self, data):
        """Retrieve the metadata overrides from the data."""
        if not data:
            return {}
        metadata_overrides = {}
        for key, value in data.items():

            if key in self.metadata_pairing.keys():
                metadata_overrides[self.metadata_pairing[key]] = value

        return metadata_overrides

