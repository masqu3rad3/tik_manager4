"""Preview Module."""


class PreviewContext:
    """Data class to hold the preview context."""
    def __init__(self):
        """Initialize the PreviewContext object."""
        self._enabled: bool = True
        self._camera: str = None
        self._resolution: (list, tuple) = None
        self._frame_range: (list, tuple) = None

    @property
    def enabled(self):
        """Preview context enabled."""
        return self._enabled

    def set_enabled(self, value):
        """Set the enabled state.

        Args:
            value (bool): The enabled state.
        """
        self._enabled = value

    @property
    def camera(self):
        """Preview context camera."""
        return self._camera

    def set_camera(self, value):
        """Set the camera.

        Args:
            value (str): The camera name.
        """
        self._camera = value

    @property
    def resolution(self):
        """Preview context resolution."""
        return self._resolution

    def set_resolution(self, value):
        """Set the resolution.

        Args:
            value (list, tuple): The resolution.
        """
        self._resolution = value

    @property
    def frame_range(self):
        """Preview context frame range."""
        return self._frame_range

    def set_frame_range(self, value):
        """Set the frame range.

        Args:
            value (list, tuple): The frame range.
        """
        self._frame_range = value

# TODO:  Move the preview functions from work object here and make it available to be used by work and publishes (or maybe more)
