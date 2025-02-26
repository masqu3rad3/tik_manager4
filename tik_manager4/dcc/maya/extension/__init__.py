from pathlib import Path
import importlib
import inspect
# from tik_manager4.objects import guard
from tik_manager4.dcc.extension_core import ExtensionCore

# guard_obj = guard.Guard()
classes = {}
modules = list(Path(__file__).parent.glob("*.py"))
# common_modules = guard_obj.commons.collect_common_modules("maya", "extension")

exceptions = ["__init__.py"]

# for mod in modules + common_modules:
for mod in modules:
    file_name = mod.name
    if file_name not in exceptions and not file_name.startswith("_"):
        module_name = mod.stem
        module = importlib.import_module(f"{__name__}.{module_name}")

        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, ExtensionCore) and obj != ExtensionCore:
                classes[module_name] = obj
