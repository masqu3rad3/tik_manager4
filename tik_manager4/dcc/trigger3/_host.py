"""The one place trigger3 imports Trigger: its version control host."""

from pathlib import Path


def host():
    """``tik.trigger.vcs.host``: the session, open, save and refresh."""
    from tik.trigger import vcs

    return vcs.host


def export_guides(session, path):
    """Write ``session``'s guides to ``path``, drawing them from the document.

    ``session.guides.export`` serialises the guide *joints in the scene*, and
    by the time an extract runs there usually are none: nothing draws on open
    or checkout, and a build deletes them -- ``kinematics.after_build``
    defaults to ``delete`` -- so the ``.trg`` would come out with no modules
    in it and be published anyway. The document still holds every pose, so
    draw it back, export that, and take the rendering away again when the
    scene had none: an export must not change what the rigger is looking at.

    This mirrors ``PublishAction._export_guides`` in
    ``tik.trigger.actions.publish.publish``.
    """
    from tik.trigger.guides.snapshot import snapshot

    was_drawn = bool(snapshot())
    session.guides.draw(poses="discard")
    session.guides.export(path)
    if not was_drawn:
        session.guides.clear_rendering()
