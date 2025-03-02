from .management_core import ManagementCore

# Dictionary to store platform classes
platforms = {}
ui_extensions = {}

from tik_manager4.management.shotgrid.main import ProductionPlatform as sg_platform
from tik_manager4.management.shotgrid.ui_extension import UiExtensions as sg_ui_extension
platforms["shotgrid"] = sg_platform
ui_extensions["shotgrid"] = sg_ui_extension

from tik_manager4.management.kitsu.main import ProductionPlatform as kitsu_platform
from tik_manager4.management.kitsu.ui_extension import UiExtensions as kitsu_ui_extension
platforms["kitsu"] = kitsu_platform
ui_extensions["kitsu"] = kitsu_ui_extension

__all__ = ["platforms"]
