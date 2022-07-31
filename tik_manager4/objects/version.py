
class Version(object):
    def __init__(self, path=None, user=None, workstation=None, note=None, thumbnail=None, preview=None, ranges=None):
        super(Version, self).__init__()

        self._relative_path = path
        self._user = user
        self._workstation = workstation
        self._note = note
        self._thumbnail = thumbnail
        self._preview = preview or {}
        self._ranges = ranges
