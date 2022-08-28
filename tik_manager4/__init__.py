import os
from tik_manager4.objects import guard
from tik_manager4.core import filelog

def initialize(dcc_name):
    os.environ["TIK_DCC"] = dcc_name
    guard.Guard.set_dcc(dcc_name) # force the guard to use the dcc name
    from tik_manager4.objects.main import Main
    return Main()