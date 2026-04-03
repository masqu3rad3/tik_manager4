from pathlib import Path
import importlib
import inspect
from tik_manager4.dcc.extract_core import ExtractCore

classes = {}
modules = list(Path(__file__).parent.glob("*.py"))

exceptions = ["__init__.py"]

for mod in modules:
    file_name = mod.name
    if file_name not in exceptions and not file_name.startswith("_"):
        module_name = mod.stem
        module = importlib.import_module(f"{__name__}.{module_name}")

        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, ExtractCore) and obj != ExtractCore:
                classes[module_name] = obj
