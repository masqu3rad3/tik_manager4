"""Ingest using Katana's Importomatic node."""

from pathlib import Path

from Katana import NodegraphAPI  # pylint: disable=import-error
from tik_manager4.dcc.ingest_core import IngestCore


class Importomatic(IngestCore):
    """Ingest using Katana's Importomatic node."""

    nice_name = "Ingest To Importomatic"
    # TODO: Currently only Alembic is supported. Check if there are other file types that can be ingested.
    valid_extensions = [".abc"]
    referencable = False
    def __init__(self):
        super(Importomatic, self).__init__()

    def _bring_in_default(self):
        """Import File to Importomatic."""

        # check the file extenstion and call the appropriate function
        extension = Path(self.ingest_path).suffix
        if extension == ".abc":
            self.__bring_in_alembic()

    def __bring_in_alembic(self):
        # reuse if there is already an importomatic node
        impo_node = NodegraphAPI.GetNode('importomatic_tik_manager')
        if not impo_node:
            impo_node = NodegraphAPI.CreateNode("Importomatic", NodegraphAPI.GetRootNode())
            impo_node.setName("importomatic_tik_manager")

        # Create alembic group node
        abc_grp = NodegraphAPI.CreateNode('Group', NodegraphAPI.GetRootNode())
        # this is a quick and dirty way to identify the group node name.
        # TODO: Find a better way to identify the group node name.
        group_node_name = (Path(self.ingest_path).name).split("_", 1)[-1]
        abc_grp.setName(group_node_name)
        abc_grp.setType('Alembic')
        abc_grp.addOutputPort('out')
        abc_grp_port = abc_grp.getReturnPort('out')

        # Build group node params for importomatic
        assetinfo_page = abc_grp.getParameters().createChildGroup('assetInfo')

        abc_in_node = NodegraphAPI.CreateNode('Alembic_In', abc_grp)
        abc_in_node.setName(group_node_name)
        abc_in_node.getParameter('abcAsset').setValue(self.ingest_path, 0)
        abc_node_port = abc_in_node.getOutputPort('out')

        # Connect ports
        abc_node_port.connect(abc_grp_port)

        # Add to importomatic
        impo_node.insertNodeIntoOutputMerge(abc_grp, 'default')  # (node, importomatic output name)