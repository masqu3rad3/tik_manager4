__version__ = "6.9.2"
__version_info__ = (6, 9, 2, "", "")
__minimum_python_version__ = (3, 9)
__maximum_python_version__ = (3, 13)

# PYSIDE-932: Python 2 cannot import 'zipfile' for embedding while being imported, itself.
# We simply pre-load all imports for the signature extension.
# Also, PyInstaller seems not always to be reliable in finding modules.
# We explicitly import everything that is needed:
import sys
import os
import zipfile
import base64
import marshal
import io
import contextlib
import textwrap
import traceback
import types
import struct
import re
import tempfile
import keyword
import functools
import typing

from shiboken6.Shiboken import *
