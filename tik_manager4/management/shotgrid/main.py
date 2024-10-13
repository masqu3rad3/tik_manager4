"""Main module for the Shotgrid integration."""

import re
import os
import sys
from pathlib import Path
from copy import deepcopy

external_folder = os.getenv("TIK_EXTERNAL_SOURCES")
if not external_folder:
    raise Exception(
        "TIK_EXTERNAL_SOURCES environment variable is not set. Please make sure the tik_manager4 is initialized."
    )
shotgun_folder = (Path(external_folder) / "shotgunsoftware").as_posix()
print(shotgun_folder)

if shotgun_folder not in sys.path:
    sys.path.append(shotgun_folder)

import tank


class ProductionPlatform(object):
    """Main class for the Shotgrid integration."""

    lock_subproject_creation = True
    lock_task_creation = True

    def __init__(self, tik_main_obj):
        self.tik_main = tik_main_obj
        tank.authentication.set_shotgun_authenticator_support_web_login(True)
        self.authenticator = tank.authentication.ShotgunAuthenticator()

        self.user = self.authenticator.get_user()
        self.sg = self.user.create_sg_connection()

    def get_projects(self):
        """Get all the projects from Shotgrid."""
        fields = ["name", "sg_status", "start_date", "end_date", "image"]
        filters = [
            ["archived", "is", False],
            ["is_template", "is", False],
            ["is_demo", "is", False],
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

    def create_from_project(self, project_root, shotgrid_project_id):
        """Create a tik_manager4 project from the existing Shotgrid project."""
        project = self.sg.find_one("Project", [["id", "is", shotgrid_project_id]], ["name"])
        project_name = re.sub('[^\w_.)( -]', '', project["name"])
        project_path = Path(project_root) / project_name
        project_path.mkdir(exist_ok=True)
        self.tik_main.create_project(
            project_path.as_posix(), structure_template="empty"
        )

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

        _salvage_dict = deepcopy(self.tik_main.user.commons.category_definitions.get_data())
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
                    "extracts": ["source"]
                }

        self.tik_main.project.category_definitions.set_data(new_dict)
        self.tik_main.project.category_definitions.apply_settings(force=True)

        ####

        for asset in all_assets:
            if asset["sg_asset_type"]:
                if assets_sub.subs.get(asset["sg_asset_type"]) is None:
                    sub = self.tik_main.project.create_sub_project(asset["sg_asset_type"], parent_path="Assets")
                else:
                    sub = self.tik_main.project.subs["Assets"].subs[asset["sg_asset_type"]]
            else:
                sub = self.tik_main.project.subs["Assets"]
            asset_name = asset["code"]

            # collect the pipeline steps (categories) from the sg tasks
            # categories = []
            # for task in asset["tasks"]:
            #     task_data = self.sg.find_one("Task", [["id", "is", task["id"]]], ["step"])
            #     if not task_data:
            #         continue
            #     step = task_data["step"]["name"]
            #     if step and step not in categories:
            #         categories.append(step)
            # sub.add_task(asset_name, categories=categories, uid=asset["id"])
            sub.add_task(asset_name, categories=asset_categories, uid=asset["id"])
            # sub.add_task(asset_name, categories=asset_categories)

        for shot in all_shots:
            if shot["sg_sequence"]:
                if shots_sub.subs.get(shot["sg_sequence"]["name"]) is None:
                    sub = self.tik_main.project.create_sub_project(shot["sg_sequence"]["name"], parent_path="Shots")
                else:
                    sub = self.tik_main.project.subs["Shots"].subs[shot["sg_sequence"]["name"]]
            else:
                sub = self.tik_main.project.subs["Shots"]
            shot_name = shot["code"]

            # collect the pipeline steps (categories) from the sg tasks
            # categories = []
            # for task in shot["tasks"]:
            #     task_data = self.sg.find_one("Task", [["id", "is", task["id"]]], ["step"])
            #     if not task_data:
            #         continue
            #     step = task_data["step"]["name"]
            #     if step and step not in categories:
            #         categories.append(step)

            # sub.add_task(shot_name, categories=categories, uid=shot["id"])
            sub.add_task(shot_name, categories=shot_categories, uid=shot["id"])
