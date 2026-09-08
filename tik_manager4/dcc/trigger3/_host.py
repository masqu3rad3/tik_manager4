"""The one place trigger3 imports Trigger: its version control host."""


def host():
    """``tik.trigger.vcs.host``: the session, open, save and refresh."""
    from tik.trigger import vcs

    return vcs.host
