"""Main module for the Kitsu integration."""
import importlib
import logging
import sys
from pathlib import Path

from tik_manager4.management.management_core import ManagementCore


external_folder = Path(__file__).parents[2] / "external"

kitsu_folder = (external_folder / "kitsu").as_posix()

if kitsu_folder not in sys.path:
    sys.path.append(kitsu_folder)

# import gazu

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

class ProductionPlatform(ManagementCore):
    """Main class for Kitsu integration."""

    metadata_pairing = {
        "sg_cut_in": "start_frame",
        "sg_cut_out": "end_frame",
        "sg_head_in": "pre_handle",
        "sg_tail_out": "post_handle",
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
        self.gazu.log_in("admin@example.com", "mysecretpassword")

        # TODO: Test if the gazu is authenticated
        self.is_authenticated = True

        return self.gazu, "Success"


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