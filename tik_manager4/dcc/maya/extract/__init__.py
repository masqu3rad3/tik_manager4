import os
import glob
import importlib
import inspect
from tik_manager4.dcc.extract_core import ExtractCore

classes = {}
modules = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))

exceptions = ["__init__.py"]

for mod in modules:
    file_name = os.path.basename(mod)
    if file_name not in exceptions and not file_name.startswith("_"):
        module_name = file_name[:-3]
        module_path = os.path.join(os.path.dirname(__file__), module_name)
        module = importlib.import_module(f"{__name__}.{module_name}")

        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, ExtractCore) and obj != ExtractCore:
                classes[module_name] = obj

