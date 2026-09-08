"""Extract the Trigger session as a self-contained bundle (folder)."""

from pathlib import Path

from tik_manager4.dcc.extract_core import ExtractCore
from tik_manager4.dcc.trigger3._host import export_guides, host

BUNDLE_MATCH_ID = 31
STORE_DIR = "_store"


class Source(ExtractCore):
    """The ``.tr`` with its paths rewritten, its dependencies deduplicated."""

    nice_name = "Trigger Session"
    color = (255, 255, 255)
    bundled = True
    bundle_match_id = BUNDLE_MATCH_ID

    def __init__(self):
        super().__init__()
        self.extension = ""
        self.publish_set = None

    def set_publish_set(self, publish_set):
        """Use a set the publish action already built instead of collecting."""
        self.publish_set = publish_set

    @classmethod
    def resolve_output_for(cls, folder, name, version):
        """The bundle folder for a name and version, without touching state.

        The same string ``resolve_output`` gives once the properties are set.
        """
        return (Path(folder) / f"{cls.name.upper()}_{name}_{version}").as_posix()

    def _collect(self):
        """Collect a publish set from the host session (no set was handed in)."""
        from tik.trigger.core.publish_set import PublishSet

        session = host().session
        if session is None or session.file_path is None:
            raise RuntimeError("No saved Trigger session to publish.")
        guides = (
            Path(self.extract_folder)
            / f"{self.extract_name}_{self.version_string}.trg"
        )
        export_guides(session, guides)
        return PublishSet.collect(session.file_path, session.document, guides=guides)

    def _extract_default(self):
        from tik.trigger.core.publish_set import write_bundle

        publish_set = self.publish_set or self._collect()
        target = Path(self.resolve_output())
        write_bundle(
            publish_set, target, store_root=Path(self.extract_folder) / STORE_DIR
        )

    def _collect_bundle_info(self):
        """Every file in the bundle, keyed by its name.

        The inherited fallback keys on the name *without* the extension, so a
        bundle whose session and guides share a stem -- ``hero.tr`` beside
        ``hero.trg``, which is the normal case -- would list only one of them.
        """
        root = Path(self.resolve_output())
        info = {}
        for item in sorted(root.rglob("*")):
            if not item.is_file():
                continue
            relative = item.relative_to(root).as_posix()
            info[relative] = {
                "extension": item.suffix,
                "path": relative,
                "sequential": False,
            }
        self.bundle_info = info
