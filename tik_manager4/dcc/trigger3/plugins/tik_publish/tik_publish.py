"""Publish the built rig into the Tik Manager work the session lives in."""

from tik.trigger.actions.publish.publish import PublishAction
from tik.trigger.core import register_action
from tik.trigger.core.exceptions import ActionExecutionError

DCC_NAME = "trigger3"
ELEMENTS = ("source", "rig", "guides")


def _tik():
    """A tik_manager4 main object bound to the trigger3 DCC.

    ``initialize`` sets the global DCC and reloads ``objects.main``, so inside
    a Maya that also runs tik_manager's Maya integration this is re-done
    before every operation, as the provider does.
    """
    import tik_manager4

    return tik_manager4.initialize(DCC_NAME)


def _installed() -> bool:
    """True when tik_manager4 can be imported at all."""
    try:
        import tik_manager4  # noqa: F401  pylint: disable=unused-import
    except ImportError:
        return False
    return True


@register_action("tik_publish", category="finish", icon="tik_publish", scope="publish")
class TikPublish(PublishAction):
    """Publish to Tik Manager: the session bundle, the rig scene and the guides.

    The session must be saved as a version of a Tik Manager work, and the
    work's category must list source, rig and guides among its extracts.
    """

    label = "Tik Publish"

    def _work(self, ctx):
        """The Tik Manager work the session file belongs to, or None."""
        session = ctx.session
        if session is None or session.file_path is None:
            return None
        work, _version = _tik().project.find_work_by_absolute_path(
            str(session.file_path)
        )
        return work or None

    def validate(self, ctx):
        problems = super().validate(ctx)
        if problems:
            return problems
        if not _installed():
            return ["tik_publish: Tik Manager is not installed"]
        if self._work(ctx) is None:
            return ["tik_publish: the session is not saved in a Tik Manager work"]
        return []

    def deliver(self, publish_set, ctx):
        from tik.trigger import vcs
        from tik_manager4.objects.publisher import Publisher

        # Publisher.resolve reads the current work through the DCC handler,
        # which asks the host for the session path; a script driving the
        # action without the window has attached nothing yet.
        if vcs.host.session is None:
            vcs.host.attach(session=ctx.session)
        tik = _tik()
        publisher = Publisher(tik.project)
        if not publisher.resolve():
            raise ActionExecutionError("the session is not saved in a Tik Manager work")
        missing = [name for name in ELEMENTS if name not in publisher.extractors]
        if missing:
            raise ActionExecutionError(
                "the work's category definition must list these extracts: "
                + ", ".join(missing)
            )
        publisher.reserve()
        for extractor in publisher.extractors.values():
            extractor.set_publish_set(publish_set)
        publisher.extract()
        failed = [
            name
            for name, extractor in publisher.extractors.items()
            if extractor.state == "failed"
        ]
        if failed:
            raise ActionExecutionError(
                "extract failed: "
                + "; ".join(
                    f"{name}: {publisher.extractors[name].message}" for name in failed
                )
            )
        published = publisher.publish(notes=self.notes or "Published by Trigger")
        ctx.log(f"Published to Tik Manager: {published.name} v{published.version:03d}")
