import sys
import importlib
from pathlib import Path
from .management_core import ManagementCore

# Dictionary to store platform classes
platforms = {}

# # Path to the directory containing platform folders
# _FROZEN = getattr(sys, "frozen", False)
# if _FROZEN:
#     platform_folder = Path(sys.executable).parents[2] / "management"
# else:
#     platform_folder = Path(__file__).parent
#
# # Iterate over each directory in the platform folder
# for folder in platform_folder.iterdir():
#     # Check if it's a directory and contains a main.py file
#     main_file = folder / "main.py"
#     if folder.is_dir() and main_file.exists():
#         # Import the main module dynamically
#         module_name = f".{folder.name}.main"
#         module = importlib.import_module(module_name, package=__package__)
#
#         # Get the ProductionPlatform class if it exists
#         platform_class = getattr(module, "ProductionPlatform", None)
#
#         # Add to dictionary if class is found and inherits from ManagementCore
#         if platform_class and issubclass(platform_class, ManagementCore):
#             platforms[folder.name] = platform_class
#

# test
from tik_manager4.management.shotgrid.main import ProductionPlatform
platforms["shotgrid"] = ProductionPlatform

# Optional: Explicitly make platforms accessible from the management package
__all__ = ["platforms"]
