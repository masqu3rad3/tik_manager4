"""Some cross-platform / cross-dcc related static methods"""

import os
import platform

def get_home_dir():
    """expanduser does not always return the same result (in Maya it returns user/Documents).
    This returns the true user folder for all platforms and dccs"""
    if platform.system() == "Windows":
        return os.path.normpath(os.getenv("USERPROFILE"))
    else:
        return os.path.normpath(os.getenv("HOME"))



