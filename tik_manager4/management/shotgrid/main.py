"""Main module for the Shotgrid integration."""

import os
import logging
from datetime import datetime, timezone
import sys
from pathlib import Path
from copy import deepcopy
from tik_manager4.core import utils
from tik_manager4.management.management_core import ManagementCore

# raise Exception("This module is not ready for use.")

# external_folder = os.getenv("TIK_EXTERNAL_SOURCES")
external_folder = Path(__file__).parents[2] / "external"
# if not external_folder:
#     raise Exception(
#         "TIK_EXTERNAL_SOURCES environment variable is not set. Please make sure the tik_manager4 is initialized."
#     )
# shotgun_folder = (Path(external_folder) / "shotgunsoftware").as_posix()
shotgun_folder = (external_folder / "shotgunsoftware").as_posix()

if shotgun_folder not in sys.path:
    sys.path.append(shotgun_folder)

import tank
from tank_vendor import shotgun_api3

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

class ProductionPlatform(ManagementCore):
    """Main class for the Shotgrid integration."""

    # define any metadata that needs to be paired with tik manager counterparts
    metadata_pairing = {
        "sg_cut_in": "start_frame",
        "sg_cut_out": "end_frame",
        "sg_head_in": "pre_handle",
        "sg_tail_out": "post_handle",
    }

    nice_name = "Autodesk Flow Production"
    name = "shotgrid"
    lock_subproject_creation = True
    lock_task_creation = True

    def __init__(self, tik_main_obj):
        self.tik_main = tik_main_obj
        self.sg = None
        self.is_authenticated = False

    def authenticate(self):
        """Connect to Shotgrid."""
        method = self.tik_main.user.commons.management_settings.get(
            "sg_authentication_method", "User"
        )
        if method == "User":
            self.sg, msg = self._user_authenticate()
        elif method == "Script":
            self.sg, msg = self._script_authenticate()
        else:
            self.sg = None
            msg = "Invalid authentication method."
        self.is_authenticated = bool(self.sg)
        return self.sg, msg

    def _user_authenticate(self):
        """Make a user based authentication."""
        try:
            tank.authentication.set_shotgun_authenticator_support_web_login(
                True)
            authenticator = tank.authentication.ShotgunAuthenticator()
            user = authenticator.get_user()
            sg_connection = user.create_sg_connection()
            # test connection
            sg_connection.find_one("Project", [])
            return sg_connection, "Success"
        except Exception as e:
            msg = f"User authentication failed: {e}"
            LOG.error(msg)
            return None, msg

    def _script_authenticate(self):
        """Make a script based authentication."""
        try:
            script_name = self.tik_main.user.commons.management_settings.get(
                "sg_script_name"
            )
            if not script_name:
                msg = "Script name not set in Settings -> Platform Settings."
                LOG.error(msg)
                return None, msg

            api_key = self.tik_main.user.commons.management_settings.get(
                "sg_api_key")
            if not api_key:
                msg = "API key not set in Settings -> Platform Settings."
                LOG.error(msg)
                return None, msg

            base_url = self.tik_main.user.commons.management_settings.get(
                "sg_url")
            if not base_url:
                msg = "URL not set in Settings -> Platform Settings."
                LOG.error(msg)
                return None, msg

            return shotgun_api3.Shotgun(
                base_url=base_url,
                script_name=script_name,
                api_key=api_key,
            ), "Success"
        except Exception as e:
            msg = f"Script authentication failed: {e}"
            LOG.error(msg)
            return None, msg

    def get_projects(self, archived: bool = False, is_template: bool = False,
                     is_demo: bool = False) -> list:
        """Get all the projects from Shotgrid."""
        fields = ["name", "sg_status", "start_date", "end_date", "image"]
        filters = [
            ["archived", "is", archived],
            ["is_template", "is", is_template],
            ["is_demo", "is", is_demo],
        ]
        projects = self.sg.find("Project", filters, fields)
        return projects

    def get_all_shots(self, project_id):
        """Get all the shots from Shotgrid.

        Args:
            project_id (int): The ID of the project.

        Returns:
            List[Dict[str, Any]]: A list of shots.
        """
        fields = [
            "id",
            "code",
            # "tasks",
            "sg_sequence",
            "sg_sequence.Sequence.episode",
            # "image",
        ]
        # we are adding the extra metadata fields here:
        fields.extend(self.metadata_pairing.keys())
        filters = [["project", "is", {"type": "Project", "id": project_id}]]
        shots = self.sg.find("Shot", filters, fields)
        return shots

    def get_all_assets(self, project_id):
        """Get all the assets from Shotgrid.

        Args:
            project_id (int): The ID of the project.

        Returns:
            List[Dict[str, Any]]: A list of assets.
        """
        fields = [
            "id",
            "code",
            # "tasks",
            "sg_asset_type"
        ]
        filters = [["project", "is", {"type": "Project", "id": project_id}]]
        assets = self.sg.find("Asset", filters, fields)
        return assets

    @staticmethod
    def date_stamp():
        """Return the current date stamp in ISO 8601 format."""
        # Get the current time in UTC and format it as ISO 8601
        return datetime.now(timezone.utc).strftime(
            '%Y-%m-%dT%H:%M:%SZ')


    def create_from_project(self, project_root, shotgrid_project_id, set_project=True):
        """Create a tik_manager4 project from the existing Shotgrid project."""
        current_project_path = self.tik_main.project.absolute_path
        project = self.sg.find_one(
            "Project", [["id", "is", shotgrid_project_id]], ["name"]
        )
        project_name = utils.sanitize_text(project["name"])
        project_path = Path(project_root) / project_name
        project_path.mkdir(exist_ok=True)
        ret = self.tik_main.create_project(
            project_path.as_posix(), structure_template="empty",
            set_after_creation=True # we ALWAYS set it for further operations
        )
        if ret == -1:
            return None

        all_assets = self.get_all_assets(shotgrid_project_id)
        all_shots = self.get_all_shots(shotgrid_project_id)

        assets_sub = self._get_assets_sub()
        shots_sub = self._get_shots_sub()

        asset_categories = self._get_asset_categories()
        shot_categories = self._get_shot_categories()

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

        ####

        for asset in all_assets:
            self._sync_new_asset(asset, assets_sub, asset_categories)

        for shot in all_shots:
            self._sync_new_shot(shot, shots_sub, shot_categories)

        # tag the project as management driven
        self.tik_main.project.settings.edit_property("management_driven", True)
        self.tik_main.project.settings.edit_property("management_platform", "shotgrid")
        self.tik_main.project.settings.edit_property("host_project_name", project["name"])
        self.tik_main.project.settings.edit_property("host_project_id", shotgrid_project_id)
        self.tik_main.project.settings.edit_property("last_sync", self.date_stamp())

        self.tik_main.project.settings.apply_settings(force=True)

        if not set_project: # switch back to the original project
            self.tik_main.set_project(current_project_path)

        return project_path

    def _get_changes_from_log(self):
        """Get what's changed in the project since last sync using the event logs.

        Example data:
            [
                {
                    'id': 1544,
                    'action': 'new_asset',
                    'sg_asset_type': 'Character',
                    'code': 'dragon'
                },
                {
                    'id': 1405,
                    'action': 'new_shot',
                    'sg_sequence': {'id': 108, 'name': 'AAA', 'type': 'Sequence'},
                    'sg_sequence.Sequence.episode': None,
                    'code': 'AAA_170'
                },
                {
                    'id': 1265,
                    'action': 'omitted'
                }
            ]

        Returns:
            list: A list of dictionaries containing the event data.
        """
        project_id = self.tik_main.project.settings.get("host_project_id")
        if not project_id:
            raise Exception("Project is not linked to a Shotgrid project.")

        # Get the last sync date
        last_sync = self.tik_main.project.settings.get("last_sync")

        filters = [
            ['event_type', 'in', [
                'Shotgun_Shot_New',
                'Shotgun_Asset_New',
                'Shotgun_Shot_Delete',
                'Shotgun_Asset_Delete',
                'Shotgun_Shot_Change',
                'Shotgun_Asset_Change'
            ]],
            ['created_at', 'greater_than', last_sync],
            ['project', 'is', {'type': 'Project', 'id': project_id}]
        ]
        fields = ['entity', 'event_type', 'meta']

        events = self.sg.find('EventLogEntry', filters, fields)

        # Initialize an empty list to hold event information
        event_list = []

        # Lists to hold IDs for additional data queries
        asset_ids = []
        shot_ids = []

        # Get keys from the metadata pairing dictionary
        metadata_keys = self.metadata_pairing.keys()

        for event in events:
            event_type = event.get('event_type')
            entity = event.get('entity')
            meta = event.get('meta', {})

            if entity and event_type:
                action = None
                event_data = {'id': entity['id']}

                # Determine the action and collect additional data
                if event_type == 'Shotgun_Asset_New' and entity[
                    'type'] == 'Asset':
                    action = 'new_asset'
                    asset_ids.append(entity['id'])
                elif event_type == 'Shotgun_Shot_New' and entity[
                    'type'] == 'Shot':
                    action = 'new_shot'
                    shot_ids.append(entity['id'])
                elif event_type == 'Shotgun_Asset_Delete' and entity[
                    'type'] == 'Asset':
                    action = 'deleted_asset'
                elif event_type == 'Shotgun_Shot_Delete' and entity[
                    'type'] == 'Shot':
                    action = 'deleted_shot'
                elif event_type in ['Shotgun_Asset_Change',
                                    'Shotgun_Shot_Change']:
                    if meta.get('attribute_name') == 'sg_status_list':
                        old_value = meta.get('old_value')
                        new_value = meta.get('new_value')
                        if old_value != 'omt' and new_value == 'omt':
                            action = 'omitted'
                        elif old_value == 'omt' and new_value != 'omt':
                            action = 'revived'
                    elif meta.get('attribute_name') in metadata_keys:
                        action = 'meta_change'
                        event_data.update(
                            {
                                "attribute_name": meta['attribute_name'],
                                "value": meta['new_value']
                             }
                            # {meta['attribute_name']: meta['new_value']}
                        )

                # Add the event to the list if an action was determined
                if action:
                    event_data['action'] = action
                    event_list.append(event_data)

        # Make additional queries if necessary
        asset_data_map = {}
        if asset_ids:
            asset_filters = [
                ["project", "is", {"type": "Project", "id": project_id}],
                ['id', 'in', asset_ids]
            ]
            asset_fields = ['id', 'sg_asset_type', 'code']
            asset_details = self.sg.find('Asset', asset_filters, asset_fields)
            # Map asset details by ID for quick lookup
            asset_data_map = {asset['id']: asset for asset in asset_details}

        shot_data_map = {}
        if shot_ids:
            shot_filters = [
                ["project", "is", {"type": "Project", "id": project_id}],
                ['id', 'in', shot_ids]
            ]
            shot_fields = ['id', 'sg_sequence', 'sg_sequence.Sequence.episode',
                           'code'] + list(metadata_keys)
            shot_details = self.sg.find('Shot', shot_filters, shot_fields)
            # Map shot details by ID for quick lookup
            shot_data_map = {shot['id']: shot for shot in shot_details}

        # Add additional data to events
        for event in event_list:
            event_id = event['id']
            if event['action'] == 'new_asset' and event_id in asset_data_map:
                event.update(asset_data_map[event_id])
            elif event['action'] == 'new_shot' and event_id in shot_data_map:
                event.update(shot_data_map[event_id])

        return event_list

    def _sync_new_asset(self, asset_data, assets_sub, asset_categories):
        """Sync a new asset from Shotgrid.

        Args:
            asset_data (dict): The data of the asset.
                Must contain the keys "id", "code", and "sg_asset_type".
            assets_sub (SubProject): The sub project to add the asset to.
            asset_categories (list): The categories of the asset.
        """
        asset_id = asset_data["id"]
        asset_code = asset_data["code"]
        asset_type = asset_data["sg_asset_type"]
        if asset_type:
            if assets_sub.subs.get(asset_type) is None:
                sub = self.tik_main.project.create_sub_project(
                    asset_type, parent_path="Assets"
                )
            else:
                sub = self.tik_main.project.subs["Assets"].subs[asset_type]
        else:
            sub = assets_sub
        asset_name = utils.sanitize_text(asset_code)
        task = sub.add_task(asset_name, categories=asset_categories, uid=asset_id)
        return task

    def _sync_new_shot(self, shot_data, shots_sub, shot_categories):
        """Sync a new shot from Shotgrid.

        Args:
            shot_data (dict): The data of the shot.
                Must contain the keys "id", "code", "sg_sequence", and "episode".
            shots_sub (SubProject): The sub project to add the shot to.
            shot_categories (list): The categories of the shot.
        """
        shot_id = shot_data["id"]
        shot_code = shot_data["code"]
        sequence = shot_data["sg_sequence"]
        is_episodic = shot_data.get("sg_sequence.Sequence.episode")
        query_sub = shots_sub

        if is_episodic:
            episode = is_episodic["name"]
            if query_sub.subs.get(episode) is None:
                query_sub = self.tik_main.project.create_sub_project(
                    episode,
                    parent_path=query_sub.path,
                    uid=is_episodic["id"],
                    mode="episode",
                )
            else:
                query_sub = query_sub.subs[episode]
        if sequence:
            if query_sub.subs.get(sequence["name"]) is None:
                query_sub = self.tik_main.project.create_sub_project(
                    sequence["name"],
                    parent_path=query_sub.path,
                    uid=sequence["id"],
                )
            else:
                query_sub = shots_sub.subs[sequence["name"]]
        shot_name = utils.sanitize_text(shot_code)

        metadata_overrides = {}
        # Map the metadata from Shotgrid to Tik Manager
        for sg_meta_key, tik_meta_key in self.metadata_pairing.items():
            meta_value = shot_data.get(sg_meta_key)
            if meta_value:
                metadata_overrides[tik_meta_key] = meta_value

        task = query_sub.add_task(
            shot_name,
            categories=shot_categories,
            uid=shot_id,
            metadata_overrides=metadata_overrides,
        )
        return task

    def _get_asset_categories(self):
        """Collect the steps for assets from the Shotgrid server."""
        asset_categories = [
            x["code"]
            for x in
            self.sg.find("Step", [["entity_type", "is", "Asset"]], ["code"])
        ]
        return asset_categories

    def _get_shot_categories(self):
        """Collect the steps for shots from the Shotgrid server."""
        shot_categories = [
            x["code"]
            for x in
            self.sg.find("Step", [["entity_type", "is", "Shot"]], ["code"])
        ]
        return shot_categories

    def _get_assets_sub(self):
        """Get the 'Assets' sub from the tik project.

        Creates if it doesn't exist.
        """
        assets_sub = self.tik_main.project.subs.get("Assets") or self.tik_main.project.create_sub_project(
            "Assets", parent_path="", mode="asset"
        )
        return assets_sub

    def _get_shots_sub(self):
        """Get the 'Shots' sub from the tik project.

        Creates if it doesn't exist.
        """
        shots_sub = self.tik_main.project.subs.get("Shots") or self.tik_main.project.create_sub_project(
            "Shots", parent_path="", mode="shot"
        )
        return shots_sub

    def _omit_task(self, entity_id):
        """Omit a task from the project."""
        # get the task
        task = self.tik_main.project.find_task_by_id(entity_id)
        if task == -1:
            return False
        # omit the task
        task.omit()
        return True

    def _revive_task(self, entity_id):
        task = self.tik_main.project.find_task_by_id(entity_id)
        if task == -1:
            return False
        task.revive()
        return True

    def _meta_change(self, data_dict):
        task = self.tik_main.project.find_task_by_id(data_dict["id"])
        # Map the metadata from Shotgrid to Tik Manager
        sg_meta_key = data_dict["attribute_name"]
        tik_meta_key = self.metadata_pairing.get(sg_meta_key)
        if not tik_meta_key:
            return False
        meta_value = data_dict["value"]
        # if the metadata is a new override add it to the task overrides.
        if meta_value:
            task._metadata_overrides[tik_meta_key] = meta_value
        # if the metadata is None and the override exists, remove it
        elif task._metadata_overrides.get(tik_meta_key):
            task._metadata_overrides.pop(tik_meta_key)

        task.edit_property("metadata_overrides", task._metadata_overrides)
        task.apply_settings()
        return task._metadata_overrides

    def sync_project(self):
        """Sync the project with Shotgrid."""
        # Get the changes from the log
        changes = self._get_changes_from_log()
        if not changes:
            return None
        asset_categories = self._get_asset_categories()
        shot_categories = self._get_shot_categories()

        assets_sub = self._get_assets_sub()
        shots_sub = self._get_shots_sub()

        # Process the changes
        for data_dict in changes:
            action = data_dict['action']
            entity_id = data_dict['id']

            if action == 'new_asset':
                self._sync_new_asset(data_dict, assets_sub, asset_categories)
            elif action == 'new_shot':
                self._sync_new_shot(data_dict, shots_sub, shot_categories)
            elif action == 'deleted_asset':
                # we don't delete anything. Let's omit instead.
                self._omit_task(entity_id)
            elif action == 'deleted_shot':
                # we don't delete anything. Let's omit instead.
                self._omit_task(entity_id)
            elif action == 'omitted':
                self._omit_task(entity_id)
            elif action == 'revived':
                self._revive_task(entity_id)
            elif action == 'meta_change':
                self._meta_change(data_dict)

        # Update the last sync date
        self.tik_main.project.settings.edit_property("last_sync", self.date_stamp())
        self.tik_main.project.settings.apply_settings(force=True)

        return changes

    def request_tasks(self, entity_id, entity_type, step=None, project_id=None):
        """Get all the tasks from a Shotgrid entity ID.

        Example output:
            [
                {'type': 'Task', 'id': 5981, 'content': 'Cloth'},
                {'type': 'Task', 'id': 5983, 'content': 'Rig'},
                {'type': 'Task', 'id': 5984, 'content': 'Muscle'}
            ]

        Args:
            entity_id (int): The ID of the entity.
            entity_type (str): The type of the entity. Asset or Shot.
            step (str, optional): The step of the task. Defaults to None.
            project_id (int, optional): The ID of the project. Defaults to None.
        """
        filters = [
            ["entity", "is", {"type": entity_type.capitalize(), "id": entity_id}]
        ]
        if step:
            # filters.append(["step.Step.code", "is", {"type": "Step", "id": step}])
            filters.append(["step.Step.code", "is", step])
        if project_id:
            filters.append(["project", "is", {"type": "Project", "id": project_id}])

        fields = [
            "content",
            # "sg_status_list",
            # "task_assignees",
            # "step"
        ]
        return self.sg.find("Task", filters, fields)

    @staticmethod
    def get_settings_ui():
        """Return the settings UI for the Shotgrid platform."""
        # Make sure the keys are unique accross all other platforms
        return {
            "_shotgrid": {
                "type": "separator",
                "display_name": "Autodesk Flow Production Settings",
            },
            "sg_url": {
                "display_name": "ShotGrid URL",
                "tooltip": "The URL of the ShotGrid server to connect to.",
                "type": "string",
                "value": "",
            },
            "sg_authentication_method": {
                "display_name": "Authentication Method",
                "tooltip": "Select the authentication method to use when connecting to ShotGrid.",
                "type": "combo",
                "items": ["User", "Script"],
                "value": "User",
                "disables": [["User", "sg_script_name"], ["User", "sg_api_key"]],
            },
            "sg_script_name": {
                "display_name": "Script Name",
                "tooltip": "The name of the script to use when connecting to ShotGrid.",
                "type": "string",
                "value": "",
            },
            "sg_api_key": {
                "display_name": "API Key",
                "tooltip": "The API key to use when connecting to ShotGrid.",
                "type": "string",
                "value": "",
            },
        }
