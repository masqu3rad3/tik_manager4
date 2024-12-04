import os
from pathlib import Path
from importlib import reload
from tik_manager4.objects import guard

def initialize(dcc_name, common_folder=None):
    os.environ["TIK_DCC"] = dcc_name
    parent_folder = Path(__file__).parent.parent / "tik_manager4" / "external"
    os.environ["TIK_EXTERNAL_SOURCES"] = parent_folder.as_posix()
    guard.Guard.set_dcc(dcc_name) # force the guard to use the dcc name
    # the reload is necessary to make sure the dcc is reloaded
    # this makes sure when different dcc's are used in the same python session
    # for example, Maya and trigger.
    import tik_manager4.objects.main
    reload(tik_manager4.objects.main)
    return tik_manager4.objects.main.Main(common_folder=common_folder)

    # get the installation folder of tik_manager4
    # this is necessary to get the default settings
    # and other resources
