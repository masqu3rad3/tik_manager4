"""Main module for the Kitsu integration."""
import importlib
import logging
import sys
from pathlib import Path
from copy import deepcopy


from tik_manager4.core import utils
from tik_manager4.management.management_core import ManagementCore


external_folder = Path(__file__).parents[2] / "external"

kitsu_folder = (external_folder / "kitsu").as_posix()

if kitsu_folder not in sys.path:
    sys.path.append(kitsu_folder)

# import gazu
from requests.exceptions import ConnectionError

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

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
        # FIXME: This is a temporary solution. The user should be able to login
        try:
            self.gazu.log_in("admin@example.com", "mysecretpassword")
        except ConnectionError as e:
            return None, f"Connection Error: {e}"


        # TODO: Test if the gazu is authenticated
        self.is_authenticated = True

        return self.gazu, "Success"

    def get_projects(self, archived: bool = False, is_template: bool = False,
                     is_demo: bool = False) -> list:
        """Get all the projects from Shotgrid."""
        # fields = ["name", "sg_status", "start_date", "end_date", "image"]
        # filters = [
        #     ["archived", "is", archived],
        #     ["is_template", "is", is_template],
        #     ["is_demo", "is", is_demo],
        # ]
        projects = self.gazu.project.all_projects()
        return projects

    def get_all_assets(self, project_id):
        """Get all the assets from a project."""
        return self.gazu.asset.all_assets_for_project(project_id)

    def get_all_shots(self, project_id):
        """Get all the shots from a project."""
        return self.gazu.shot.all_shots_for_project(project_id)

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

    def _get_asset_categories(self):
        """Collect the asset task types from kitsu."""
        return self.gazu.task.all_task_types_for_asset()

    def _get_shot_categories(self):
        """Collect the steps for shots from the Shotgrid server."""
        shot_categories = [
            x["code"]
            for x in
            self.sg.find("Step", [["entity_type", "is", "Shot"]], ["code"])
        ]
        return shot_categories

    def _sync_new_asset(self, asset_data, assets_sub, asset_categories):
        """Sync a new asset from Shotgrid.

        Args:
            asset_data (dict): The data of the asset.
                Must contain the keys "id", "name", and "entity_type_id".
            assets_sub (SubProject): The sub project to add the asset to.
            asset_categories (list): The categories of the asset.
        """
        asset_id = asset_data["id"]
        asset_name = asset_data["name"]
        asset_type = self.gazu.entity.get_entity_type(asset_data["entity_type_id"])
        if asset_type:
            if assets_sub.subs.get(asset_type) is None:
                sub = self.tik_main.project.create_sub_project(
                    asset_type, parent_path="Assets"
                )
            else:
                sub = self.tik_main.project.subs["Assets"].subs[asset_type]
        else:
            sub = assets_sub
        asset_name = utils.sanitize_text(asset_name)
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
        shot_name = shot_data["name"]
        sequence = self.gazu.get_entity(shot_data["parent_id"])
        is_episodic = sequence.get("parent_id")
        query_sub = shots_sub
        if is_episodic:
            episode_data = self.gazu.get_entity(sequence["parent_id"])
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
            query_sub = shots_sub.subs[sequence["name"]]
        shot_name = utils.sanitize_text(shot_name)

        metadata_overrides = {}
        # FIXME: Continue from here



    def create_from_project(self, project_root, kitsu_project_id, set_project=True):
        """Create a tik manager project from a kitsu project."""
        current_project_path = self.tik.main.project.absolute_path
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

# gazu.set_host("http://localhost/api")
# gazu.log_in("admin@example.com", "mysecretpassword")
#
# projects = gazu.project.all_open_projects()
# print("projects", projects)