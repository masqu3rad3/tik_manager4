"""Gate keeper of heavens and earth."""


class Purgatory(object):
    """Purgatory is the place where all entities go to be deleted."""

    def __init__(self, main_object):
        super().__init__()
        self.main = main_object

    def get_lost_versions(self):
        """Returns all the lost souls in purgatory"""
        pass

    def terminate(self, entity):
        """Sends the entity to the heaven. There is no turning back"""
        pass

    def resurrect(self, entity):
        """Brings the entity back to life"""
        pass
