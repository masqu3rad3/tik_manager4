"""Main module for Mari integration."""

import logging

from tik_manager4.dcc.main_core import MainCore
from tik_manager4.dcc.mari import validate
from tik_manager4.dcc.mari import extract
from tik_manager4.dcc.mari import ingest

LOG = logging.getLogger(__name__)
class Dcc(MainCore):
    """Mari class."""

    name = "mari"
    formats = [".mra"]  # File formats supported by the DCC
    preview_enabled = False  # Whether or not to enable the preview in the UI
    validations = validate.classes
    extracts = extract.classes
    ingests = ingest.classes

    # Override the applicable methods from the MainCore class