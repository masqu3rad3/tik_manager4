"""Check for the UVs crossing the UDIM boundaries."""

import logging
from collections import defaultdict

from maya import cmds
from maya.api import OpenMaya as om

from tik_manager4.dcc.validate_core import ValidateCore

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

class UdimCrossingUvs(ValidateCore):
    """Validation for overlapping UVs."""

    nice_name = "UVs Crossing UDIM Boundaries"

    def __init__(self):
        super().__init__()
        self.autofixable: bool = False
        self.ignorable: bool = False
        self.selectable: bool = True

        self.fail_dictionary: dict = {} # {mesh: [overlapping faces]}
        self.collection: list = []

    def collect(self):
        """Collect all meshes in the scene."""
        self.collection = cmds.ls(type="mesh", long=True)

    def validate(self):
        """Validate."""
        self.fail_dictionary.clear()
        self.collect()

        LOG.info("Collected %d meshes for validation",
                 len(self.collection))

        selection_list = om.MSelectionList()
        for mesh in self.collection:
            selection_list.add(mesh)

        self.fail_dictionary = self.get_udim_crossing(selection_list)
        if self.fail_dictionary:
            self.failed(msg=f"UVs crossing UDIM boundaries found on meshes: "
                            f"{cmds.ls(list(self.fail_dictionary.keys()))}")
        else:
            LOG.info("No UV boundary issues found.")
            self.passed()

    def select(self):
        """Select the failed faces."""
        cmds.select(clear=True)
        for uuid, component_list in self.fail_dictionary.items():
            cmds.select(self.parse(uuid, component_list), add=True)

    @staticmethod
    def parse(uuid, component_list):
        """Parsing generator for the selection list."""
        node = cmds.ls(uuid)[0]
        if not node:
            return
        for component in component_list:
            yield f"{node}.f[{component}]"

    def get_udim_crossing(self, selection_list):
        """Check for UVs crossing the UDIM boundaries."""
        fail_dict = defaultdict(list)
        sel_it = om.MItSelectionList(selection_list)

        while not sel_it.isDone():
            uuid, face_it = self._get_mesh_iterator_and_uuid(sel_it)
            self._process_faces(face_it, fail_dict[uuid])
            sel_it.next()

        return {k: v for k, v in fail_dict.items() if v}

    def _get_mesh_iterator_and_uuid(self, sel_it):
        """Retrieve mesh iterator and UUID from the current selection."""
        dag_path = sel_it.getDagPath()
        face_it = om.MItMeshPolygon(dag_path)
        fn_node = om.MFnDependencyNode(dag_path.node())
        uuid = fn_node.uuid().asString()
        return uuid, face_it

    def _process_faces(self, face_it, fail_list):
        """Iterate through faces and detect UDIM crossing."""
        while not face_it.isDone():
            try:
                if self._is_border_face(face_it):
                    fail_list.append(face_it.index())
            except RuntimeError:
                LOG.debug("Skipping face without UVs. -> %s", face_it.index())
                pass  # Skip faces without UVs
            face_it.next()

    def _is_border_face(self, face_it):
        """Determine if the face crosses UDIM boundaries."""
        uvs = face_it.getUVs()
        u_set, v_set = set(), set()

        for u, v in zip(uvs[0], uvs[1]):
            u_set.add(int(u) if u > 0 else int(u) - 1)
            v_set.add(int(v) if v > 0 else int(v) - 1)

        return len(u_set) > 1 or len(v_set) > 1