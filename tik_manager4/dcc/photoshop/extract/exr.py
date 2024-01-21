"""Extract Png file."""
from win32com.client import Dispatch

from tik_manager4.dcc.extract_core import ExtractCore

class Exr(ExtractCore):
    """Extract Exr from Photoshop file."""

    nice_name = "Exr"
    color = (0, 255, 221)
    def __init__(self):
        super(Exr, self).__init__()

        self.com_link = Dispatch("Photoshop.Application")

        self.extension = ".tif"

    def _extract_default(self):
        """Extract Tif."""
        file_path = self.resolve_output()
        # active_doc = self.com_link.Application.ActiveDocument
        idsave = self.com_link.CharIDToTypeID("save")
        desc182 = Dispatch("Photoshop.ActionDescriptor")
        id_as = self.com_link.CharIDToTypeID("As  ")
        desc183 = Dispatch("Photoshop.ActionDescriptor")
        id_bt_dp = self.com_link.CharIDToTypeID("BtDp")
        desc183.PutInteger(id_bt_dp, 16);
        id_cmpr = self.com_link.CharIDToTypeID("Cmpr")
        desc183.PutInteger(id_cmpr, 1)
        id_a_chn = self.com_link.CharIDToTypeID("AChn")
        desc183.PutInteger(id_a_chn, 0)
        id_ex_rf = self.com_link.CharIDToTypeID("EXRf")
        desc182.PutObject(id_as, id_ex_rf, desc183)
        id_in = self.com_link.CharIDToTypeID("In  ")
        desc182.PutPath(id_in, (file_path))
        id_doc_i = self.com_link.CharIDToTypeID("DocI")
        desc182.PutInteger(id_doc_i, 340)
        id_cpy = self.com_link.CharIDToTypeID("Cpy ")
        desc182.PutBoolean(id_cpy, True)
        idsave_stage = self.com_link.StringIDToTypeID("saveStage")
        idsave_stage_type = self.com_link.StringIDToTypeID("saveStageType")
        idsave_succeeded = self.com_link.StringIDToTypeID("saveSucceeded")
        desc182.PutEnumerated(idsave_stage, idsave_stage_type, idsave_succeeded)
        self.com_link.ExecuteAction(idsave, desc182, 3)
