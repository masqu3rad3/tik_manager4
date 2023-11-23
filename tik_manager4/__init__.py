import os
from tik_manager4.objects import guard

def initialize(dcc_name, common_folder=None):
    os.environ["TIK_DCC"] = dcc_name
    guard.Guard.set_dcc(dcc_name) # force the guard to use the dcc name
    from tik_manager4.objects.main import Main
    return Main(common_folder=common_folder)