import sys
from pathlib import Path
import importlib
import inspect
from tik_manager4.dcc.extract_core import ExtractCore

classes = {}

_FROZEN = getattr(sys, "frozen", False)
if _FROZEN:
    from tik_manager4.dcc.photoshop.extract import source
    from tik_manager4.dcc.photoshop.extract import image

    classes = {
        source.Source.name: source.Source,
        image.Image.name: image.Image
    }
else:
    DIRECTORY = Path(__file__).parent
    modules = DIRECTORY.glob("*.py")

    exceptions = ["__init__.py"]

    for mod in modules:
        file_name = str(Path(mod).name)
        if file_name not in exceptions and not file_name.startswith("_"):
            module_name = file_name[:-3]
            module = importlib.import_module(f"{__name__}.{module_name}")
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, ExtractCore)
                    and obj != ExtractCore
                ):
                    classes[obj.name] = obj
