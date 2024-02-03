import sys
from pathlib import Path
import importlib
import inspect
from tik_manager4.dcc.ingest_core import IngestCore

classes = {}

_FROZEN = getattr(sys, 'frozen', False)

if _FROZEN:
    from tik_manager4.dcc.photoshop.ingest import source
    classes = {
        source.Source.name: source.Source,
    }
else:
    modules = Path(__file__).parent.glob("*.py")
    exceptions = ["__init__.py"]

    for mod in modules:
        file_name = str(Path(mod).name)
        if file_name not in exceptions and not file_name.startswith("_"):
            module_name = file_name[:-3]
            module = importlib.import_module(f"{__name__}.{module_name}")

            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, IngestCore) and obj != IngestCore:
                    classes[obj.name] = obj