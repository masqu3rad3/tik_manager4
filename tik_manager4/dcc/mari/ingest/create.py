"""Create a new Mari project with the given object."""

from pathlib import Path

import mari

from tik_manager4.dcc.ingest_core import IngestCore


class Create(IngestCore):
    """Create a new Mari project with the given object."""

    nice_name = "Create Mari Project"
    valid_extensions = [".obj", ".fbx", ".abc", ".usd", ".usda", ".usdc", ".usdz", ".ptx"]
    bundled = False
    referencable = False

    def _bring_in_default(self):
        """Create Mari Project."""

        # This is the simplest project creation method with default settings.
        # Default method merges the objects and ASSUMES MULTI-UDIMs exists.

        project = mari.projects.current()
        if project:
            project.close()

        scalar_config = mari.ColorspaceConfig()
        scalar_config.setScalar(True)

        base_ch = mari.ChannelInfo("Base Color", 4096, 4096, mari.Image.DEPTH_HALF)
        spec_ch = mari.ChannelInfo("Specular", 4096, 4096, mari.Image.DEPTH_HALF, ColorspaceSettings=scalar_config)
        rough_ch = mari.ChannelInfo("Roughness", 4096, 4096, mari.Image.DEPTH_HALF, ColorspaceSettings=scalar_config)
        bump_ch = mari.ChannelInfo("Bump", 4096, 4096, mari.Image.DEPTH_HALF, ColorspaceSettings=scalar_config)

        empty_channels = [base_ch, spec_ch, rough_ch, bump_ch]

        project_meta_options = {}
        start_frame = self.metadata.get_value("start_frame", fallback_value=None)
        end_frame = self.metadata.get_value("end_frame", fallback_value=None)
        if start_frame:
            project_meta_options["StartFrame"] = start_frame
        if end_frame:
            project_meta_options["EndFrame"] = end_frame

        name = Path(self.ingest_path).stem
        mari.projects.create(name, self.ingest_path, empty_channels, [], project_meta_options)