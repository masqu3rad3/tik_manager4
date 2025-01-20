"""Main module for the Kitsu integration."""
import importlib
import logging
import sys
import os
from pathlib import Path
from copy import deepcopy
from datetime import datetime

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

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)
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
            except ConnectionError as exc:
                return None, f"Connection Error: {exc}"
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
                # self.gazu.log_in("admin@example.com", "mysecretpassword")
            except ConnectionError as exc:
                return None, f"Connection Error: {exc}"

        # TODO: Test if the gazu is authenticated
        self.is_authenticated = True

        return self.gazu, "Success"

    def logout(self):
        """Logout the user."""
        self.gazu.log_out()
        self.tik_main.user.resume.edit_property("kitsu_token", None)
        self.tik_main.user.resume.edit_property("kitsu_user", None)
        self.is_authenticated = False

    def get_projects(self, archived: bool = False, is_template: bool = False,
                     is_demo: bool = False) -> list:
        """Get all the projects from Shotgrid."""
        projects = self.gazu.project.all_projects()
        return projects

    def get_all_assets(self, project_id):
        """Get all the assets from a project."""
        return self.gazu.asset.all_assets_for_project(project_id)

    def get_all_shots(self, project_id):
        """Get all the shots from a project."""
        return self.gazu.shot.all_shots_for_project(project_id)

    def force_sync(self):
        """Force the sync of the project."""
        sync_stamp = self.date_stamp()

        project_id = self.tik_main.project.settings.get("host_project_id")
        if not project_id:
            raise Exception("Project is not linked to a Shotgrid project.")

        all_assets = self.get_all_assets(project_id)
        all_shots = self.get_all_shots(project_id)

        assets_sub = self._get_assets_sub()
        shots_sub = self._get_shots_sub()

        asset_categories, shot_categories = self._get_categories(project_id)

        for asset in all_assets:
            sync_block = SyncBlock(self.gazu, self.tik_main, project_id)
            sync_block.event_type = EventType.NEW_ASSET
            sync_block.kitsu_data = asset
            sync_block.subproject = assets_sub
            sync_block.categories = asset_categories
            sync_block.execute()

        for shot in all_shots:
            sync_block = SyncBlock(self.gazu, self.tik_main, project_id)
            sync_block.event_type = EventType.NEW_SHOT
            sync_block.kitsu_data = shot
            sync_block.subproject = shots_sub
            sync_block.categories = shot_categories
            sync_block.execute()

        self.tik_main.project.settings.edit_property("last_sync", sync_stamp)
        self.tik_main.project.settings.apply_settings(force=True)

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

        all_assets = self.get_all_assets(kitsu_project_id)
        all_shots = self.get_all_shots(kitsu_project_id)

        assets_sub = self._get_assets_sub()
        shots_sub = self._get_shots_sub()

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

        for asset in all_assets:
            sync_block = SyncBlock(self.gazu, self.tik_main, project)
            sync_block.event_type = EventType.NEW_ASSET
            sync_block.kitsu_data = asset
            sync_block.subproject = assets_sub
            sync_block.categories = asset_categories
            sync_block.execute()

        for shot in all_shots:
            sync_block = SyncBlock(self.gazu, self.tik_main, project)
            sync_block.event_type = EventType.NEW_SHOT
            sync_block.kitsu_data = shot
            sync_block.subproject = shots_sub
            sync_block.categories = shot_categories
            sync_block.execute()

        # tag the project as management driven
        self.tik_main.project.settings.edit_property("management_driven", True)
        self.tik_main.project.settings.edit_property("management_platform", "kitsu")
        self.tik_main.project.settings.edit_property("host_project_name", project["name"])
        self.tik_main.project.settings.edit_property("host_project_id", kitsu_project_id)
        self.tik_main.project.settings.edit_property("last_sync", sync_stamp)

        self.tik_main.project.settings.apply_settings(force=True)

        if not set_project: # switch back to the original project
            self.tik_main.set_project(current_project_path)

        return project_path

    def _get_sync_blocks(self, project, assets_sub, shots_sub, asset_categories, shot_categories):
        """Get the latest events and return the probable sync blocks."""
        last_sync = self.tik_main.project.settings.get("last_sync")
        parsed_time = datetime.strptime(last_sync,"%Y-%m-%dT%H:%M:%SZ")
        formatted_time = parsed_time.strftime("%Y-%m-%dT%H:%M:%S")
        events = self.gazu.sync.get_last_events(project=project, after=formatted_time)

        valid_event_types = ["asset:new", "shot:new", "asset:delete", "shot:delete",
                             "asset:update", "shot:update"]
        # pprint(events)
        for event in reversed(events):
            event_type = event.get("name")
            if event_type not in valid_event_types:
                continue
            sync_block = SyncBlock(self.gazu, self.tik_main, project)
            if event_type == "asset:new":
                sync_block.event_type = EventType.NEW_ASSET
                asset_data = self.gazu.asset.get_asset(event["data"]["asset_id"])
                sync_block.kitsu_data = asset_data
                sync_block.subproject = assets_sub
                sync_block.categories = asset_categories
            elif event_type == "shot:new":
                sync_block.event_type = EventType.NEW_SHOT
                shot_data = self.gazu.shot.get_shot(event["data"]["shot_id"])
                sync_block.kitsu_data = shot_data
                sync_block.subproject = shots_sub
                sync_block.categories = shot_categories
            elif event_type in ["asset:delete", "asset:update"]:
                sync_block.event_type = EventType.UPDATE_ASSET
                asset_data = self.gazu.asset.get_asset(event["data"]["asset_id"])
                sync_block.kitsu_data = asset_data
            elif event_type in ["shot:delete", "shot:update"]:
                sync_block.event_type = EventType.UPDATE_SHOT
                shot_data = self.gazu.shot.get_shot(event["data"]["shot_id"])
                sync_block.kitsu_data = shot_data
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
            return self.gazu.task.all_tasks_for_shot(entity_id)

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
        }

    def get_entity_url(self, entity_type, entity_id):
        """Return the URL of the entity."""
        url = None
        try:
            if entity_type.lower() == "asset":
                url = self.gazu.asset.get_asset_url(entity_id)
            else: # anything other than asset will be considered as shot
                url = self.gazu.shot.get_shot_url(entity_id)
        except ServerErrorException:
            LOG.warning("Server Error while getting the URL.")
        return url

class SyncBlock:
    """Class to store and execute sync blocks."""
    metadata_pairing = {
        "frame_in": "start_frame",
        "frame_out": "end_frame",
        "fps": "fps",
    }

    def __init__(self, gazu_instance, tik_main, project):
        self.gazu = gazu_instance
        self.tik_main = tik_main
        self.project = project
        self._event_type = None
        self._kitsu_data = None
        self._subproject = None
        self._categories = None

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

        This can be a shot or an asset.
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
        if self.event_type == EventType.UPDATE_ASSET:
            self._update_asset()
        elif self.event_type == EventType.UPDATE_SHOT:
            self._update_shot()
        elif self.event_type == EventType.NEW_ASSET:
            self._new_asset()
        elif self.event_type == EventType.NEW_SHOT:
            self._new_shot()

    def _new_asset(self):
        """Create a new asset in the tik project from the Kitsu data."""
        # this requires the asset data, asset subproject and asset categories to be defined.
        # TODO: Validate the data

        asset_id = self.kitsu_data["id"]
        asset_name = self.kitsu_data["name"]
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
        task = sub.find_task_by_id(asset_id)
        if task:
            self._update_asset()
        else:
            task = sub.add_task(asset_name, categories=self.categories, uid=asset_id)
        if self.kitsu_data["canceled"]:
            task.omit()

        return task

    def _new_shot(self):
        """Create a new shot in the tik project from the Kitsu data."""
        # this requires the shot data, shot subproject and shot categories to be defined.
        # TODO: Validate the data
        shot_id = self.kitsu_data["id"]
        shot_name = self.kitsu_data["name"]
        sequence = self.gazu.entity.get_entity(self.kitsu_data["parent_id"])
        is_episodic = sequence.get("parent_id", None)
        query_sub = self.subproject
        if is_episodic:
            episode_data = self.gazu.entity.get_entity(sequence["parent_id"])
            episode = episode_data["name"]
            if query_sub.subs.get(episode) is None:
                query_sub = self.tik_main.project.create_sub_project(
                    episode,
                    parent_path=query_sub.path,
                    uid=episode_data["id"],
                    mode="episode",
                )
            else:
                query_sub = query_sub.subs[episode]

        # looks like kitsu requires a sequence for all shots
        if query_sub.subs.get(sequence["name"]) is None:
            query_sub = self.tik_main.project.create_sub_project(
                sequence["name"],
                parent_path=query_sub.path,
                uid=sequence["id"],
            )
        else:
            query_sub = self.subproject.subs[sequence["name"]]
        shot_name = utils.sanitize_text(shot_name)

        metadata_overrides = self._retrieve_metadata_overrides(self.kitsu_data.get("data"))

        task = query_sub.find_task_by_id(shot_id)
        if task:
            self._update_shot()
        else:
            task = query_sub.add_task(
                shot_name,
                categories=self.categories,
                uid=shot_id,
                metadata_overrides=metadata_overrides,
            )
        if self.kitsu_data["canceled"]:
            task.omit()

        return task

    def _update_asset(self):
        """"Sync the properties of the asset with the one in Kitsu Server.

        This function assumes that the asset is already in the tik project.
        """
        asset_id = self.kitsu_data["id"]
        tik_task = self.tik_main.project.find_task_by_id(asset_id)

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

    def _retrieve_metadata_overrides(self, data):
        """Retrieve the metadata overrides from the data."""
        if not data:
            return {}
        metadata_overrides = {}
        for key, value in data.items():

            if key in self.metadata_pairing.keys():
                metadata_overrides[self.metadata_pairing[key]] = value

        return metadata_overrides

