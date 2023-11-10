"""Project management related tests for Maya."""

import pytest
from pathlib import Path
from tik_manager4.core import utils

from maya import cmds
@pytest.mark.usefixtures("clean_user")
@pytest.mark.usefixtures("prepare")
class TestMayaProject():
    """Uses a fresh mockup_common folder and test_project under user directory for all tests"""

    def test_sphere(self, tik):
        """Tests creating a sphere"""
        # tik.maya.create_sphere()
        sph = cmds.polySphere()
        assert(sph)
        # assert tik.maya.get_selected_nodes() == ["pSphere1"]

    def test_create_a_work(self, tik):
        """Tests creating a work"""
        project_path = str(Path(utils.get_home_dir(), "TM4_default"))
        tik.set_project(project_path)
        # assert tik.maya.get_selected_nodes() == ["work"]