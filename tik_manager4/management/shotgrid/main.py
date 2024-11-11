"""Main module for the Shotgrid integration."""

import os
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


class ProductionPlatform(ManagementCore):
    """Main class for the Shotgrid integration."""

    name = "ShotGrid"
    lock_subproject_creation = True
    lock_task_creation = True

    def __init__(self, tik_main_obj):
        self.tik_main = tik_main_obj
        self.sg = self.authenticate()

    def authenticate(self):
        """Connect to Shotgrid."""
        method = self.tik_main.user.commons.management_settings.get(
            "sg_authentication_method", "User"
        )
        if method == "User":
            return self._user_authenticate()
        elif method == "Script":
            return self._script_authenticate()
        else:
            raise Exception("Invalid authentication method.")

    def _user_authenticate(self):
        """Make a user based authentication."""
        tank.authentication.set_shotgun_authenticator_support_web_login(True)
        self.authenticator = tank.authentication.ShotgunAuthenticator()
        user = self.authenticator.get_user()
        return user.create_sg_connection()

    def _script_authenticate(self):
        """Make a script based authentication."""
        script_name = self.tik_main.user.commons.management_settings.get(
            "sg_script_name"
        )
        if not script_name:
            raise Exception("Script name not set in Settings -> Platform Settings.")
        api_key = self.tik_main.user.commons.management_settings.get("sg_api_key")
        if not api_key:
            raise Exception("Api key not set in Settings -> Platform Settings.")
        base_url = self.tik_main.user.commons.management_settings.get("sg_url")
        if not api_key:
            raise Exception("Url not set in Settings -> Platform Settings.")
        return shotgun_api3.Shotgun(
            base_url=base_url,
            script_name=script_name,
            api_key=api_key,
        )

    def get_projects(self, archived=False, is_template=False, is_demo=False):
        """Get all the projects from Shotgrid."""
        fields = ["name", "sg_status", "start_date", "end_date", "image"]
        filters = [
            # ["archived", "is", archived],
            # ["is_template", "is", is_template],
            # ["is_demo", "is", is_demo],
        ]
        projects = self.sg.find("Project", filters, fields)
        return projects

    def get_all_shots(self, project_id):
        """Get all the shots from Shotgrid."""
        fields = [
            "id",
            "code",
            "image",
            "sg_cut_in",
            "sg_cut_out",
            "tasks",
            "sg_sequence",
            "sg_sequence.Sequence.episode",
            "image",
        ]
        filters = [["project", "is", {"type": "Project", "id": project_id}]]
        shots = self.sg.find("Shot", filters, fields)
        return shots

    def get_all_assets(self, project_id):
        """Get all the assets from Shotgrid."""
        fields = ["id", "code", "tasks", "sg_asset_type"]
        filters = [["project", "is", {"type": "Project", "id": project_id}]]
        assets = self.sg.find("Asset", filters, fields)
        return assets

    # def set_project_by_name(self, project_name):
    #     """Set the project by name."""
    #     project = self.sg.find_one("Project", [["name", "is", project_name]])
    #     self.sg.set_project(project["id"])
    #     return project

    def create_from_project(self, project_root, shotgrid_project_id, set_project=True):
        """Create a tik_manager4 project from the existing Shotgrid project."""
        current_project_path = self.tik_main.project.absolute_path
        project = self.sg.find_one(
            "Project", [["id", "is", shotgrid_project_id]], ["name"]
        )
        # project_name = re.sub('[^\w_.)( -]', '', project["name"])
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

        assets_sub = self.tik_main.project.create_sub_project(
            "Assets", parent_path="", mode="asset"
        )
        shots_sub = self.tik_main.project.create_sub_project(
            "Shots", parent_path="", mode="shot"
        )

        # Match the project categories to shotgrid categories
        asset_categories = [
            x["code"]
            for x in self.sg.find("Step", [["entity_type", "is", "Asset"]], ["code"])
        ]
        shot_categories = [
            x["code"]
            for x in self.sg.find("Step", [["entity_type", "is", "Shot"]], ["code"])
        ]

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
            if asset["sg_asset_type"]:
                if assets_sub.subs.get(asset["sg_asset_type"]) is None:
                    sub = self.tik_main.project.create_sub_project(
                        asset["sg_asset_type"], parent_path="Assets"
                    )
                else:
                    sub = self.tik_main.project.subs["Assets"].subs[
                        asset["sg_asset_type"]
                    ]
            else:
                sub = self.tik_main.project.subs["Assets"]
            asset_name = utils.sanitize_text(asset["code"])

            sub.add_task(asset_name, categories=asset_categories, uid=asset["id"])

        for shot in all_shots:
            # does it belong to an episode?
            query_sub = shots_sub
            if shot["sg_sequence.Sequence.episode"]:
                episode = shot["sg_sequence.Sequence.episode"]["name"]
                if query_sub.subs.get(episode) is None:
                    query_sub = self.tik_main.project.create_sub_project(
                        episode,
                        parent_path=query_sub.path,
                        uid=shot["sg_sequence.Sequence.episode"]["id"],
                        mode="episode",
                    )
                else:
                    query_sub = query_sub.subs[episode]
            if shot["sg_sequence"]:
                if query_sub.subs.get(shot["sg_sequence"]["name"]) is None:
                    query_sub = self.tik_main.project.create_sub_project(
                        shot["sg_sequence"]["name"],
                        parent_path=query_sub.path,
                        uid=shot["sg_sequence"]["id"],
                    )
                else:  # do not attempt to create the sequence if it already exists
                    query_sub = self.tik_main.project.subs["Shots"].subs[
                        shot["sg_sequence"]["name"]
                    ]
            shot_name = utils.sanitize_text(shot["code"])

            # sub.add_task(shot_name, categories=categories, uid=shot["id"])
            metadata_overrides = {
                "start_frame": shot["sg_cut_in"],
                "end_frame": shot["sg_cut_out"],
            }
            query_sub.add_task(
                shot_name,
                categories=shot_categories,
                uid=shot["id"],
                metadata_overrides=metadata_overrides,
            )

        if not set_project: # switch back to the original project
            self.tik_main.set_project(current_project_path)

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
