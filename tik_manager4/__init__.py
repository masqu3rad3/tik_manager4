import os
from importlib import reload
from tik_manager4.objects import guard

def initialize(dcc_name, common_folder=None):
    os.environ["TIK_DCC"] = dcc_name
    guard.Guard.set_dcc(dcc_name) # force the guard to use the dcc name
    # the reload is necessary to make sure the dcc is reloaded
    # this makes sure when different dcc's are used in the same python session
    # for example, Maya and trigger.
    import tik_manager4.objects.main
    reload(tik_manager4.objects.main)
    return tik_manager4.objects.main.Main(common_folder=common_folder)