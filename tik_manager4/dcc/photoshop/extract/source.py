"""Extract Photoshop file."""
from pathlib import Path
from win32com.client import Dispatch

from tik_manager4.dcc.extract_core import ExtractCore

class Source(ExtractCore):
    """Extract Source Photoshop file."""

    nice_name = "Source Photoshop"
    color = (255, 255, 255)

    def __init__(self):
        super(Source, self).__init__()

        self.com_link = Dispatch("Photoshop.Application")

        self.extension = ""

    def _extract_default(self):
        """Extract for any non-specified category."""
        _file_path = self.resolve_output() # this won't have an extension.
        # get the active document
        active_doc = self.com_link.Application.ActiveDocument
        self.extension = Path(active_doc.name).suffix
        if self.extension != ".psb":
            file_path = str(Path(_file_path).with_suffix(".psd"))
            save_options = Dispatch("Photoshop.PhotoshopSaveOptions")
            active_doc.SaveAs(file_path, save_options, True)  # True means its saving this as a copy.
        else:
            file_path = str(Path(_file_path).with_suffix(".psb"))
            desc19 = Dispatch("Photoshop.ActionDescriptor")
            desc20 = Dispatch("Photoshop.ActionDescriptor")
            desc20.PutBoolean(self.com_link.StringIDToTypeID('maximizeCompatibility'), True)
            desc19.PutObject(
                self.com_link.CharIDToTypeID('As  '), self.com_link.CharIDToTypeID('Pht8'), desc20)
            desc19.PutPath(self.com_link.CharIDToTypeID('In  '), file_path)
            desc19.PutBoolean(self.com_link.CharIDToTypeID('LwCs'), True)
            self.com_link.ExecuteAction(self.com_link.CharIDToTypeID('save'), desc19, 3)
