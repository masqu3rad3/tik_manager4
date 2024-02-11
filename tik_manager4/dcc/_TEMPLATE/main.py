"""Main module for <template_dcc_name> DCC integration."""

import logging

from tik_manager4.dcc.main_core import MainCore
from tik_manager4.dcc._TEMPLATE import validate
from tik_manager4.dcc._TEMPLATE import extract
from tik_manager4.dcc._TEMPLATE import ingest

LOG = logging.getLogger(__name__)
class Dcc(MainCore):
    """<template_dcc_name> DCC class."""

    name = "<template_dcc_name>"
    formats = [".<template_dcc_extension>"]  # File formats supported by the DCC
    preview_enabled = False  # Whether or not to enable the preview in the UI
    validations = validate.classes
    extracts = extract.classes
    ingests = ingest.classes

    # Override the applicable methods from the MainCore class