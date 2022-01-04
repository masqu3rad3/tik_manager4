import os
from tik_manager4.objects import user, project


class Main(object):
    user = user.User()
    project = project.Project()

    def __init__(self):
        # set either the latest project or the default one
        if self.user.get_recent_projects():
            _project = self.user.get_recent_projects()[-1]
        else:
            _project = os.path.join(os.path.expanduser("~"), "TM4_default")
        self.project.set(_project)
        self.user.add_recent_project(_project)
