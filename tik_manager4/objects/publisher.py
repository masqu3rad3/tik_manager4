# pylint: disable=super-with-arguments
# pylint: disable=consider-using-f-string
"""Publisher Handler."""

import pathlib

from tik_manager4.core import filelog

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")

from tik_manager4 import dcc
from tik_manager4.objects.publish import Publish

class Publisher():
    _dcc_handler = dcc.Dcc()

    def __init__(self, project_object):
        """Initialize the Publisher object."""
        self._project_object = project_object
        self._work_object, self._work_version = project_object.get_current_work()

        # resolved variables
        self._resolved_extracts = {}
        self._resolved_validations = {}
        self._abs_publish_data_folder = None
        self._publish_file_name = None

        # classs variables

        self._published_object = None

    def resolve(self):
        """Resolve the validations, extracts, variables, etc."""

        if not self._work_object:
            LOG.warning("No work object found. Aborting.")
            return False

        _category_definitons = self._work_object.guard.category_definitions
        extracts = _category_definitons.get(self._work_object.category, {}).get("extracts", [])
        validations = _category_definitons.get(self._work_object.category, {}).get("validations", [])
        # collect the matching extracts and validations from the dcc_handler.
        for extract in extracts:
            if extract in self._dcc_handler.extracts.keys():
                self._resolved_extracts[extract] = self._dcc_handler.extracts[extract]
            else:
                LOG.warning("Extract {0} defined in category settings but it is not available on {1}".format(extract, self._dcc_handler.name))
        for validation in validations:
            if validation in self._dcc_handler.validations.keys():
                self._resolved_validations[validation] = self._dcc_handler.validations[validation]
            else:
                LOG.warning("Validation {0} defined in category settings but it is not available on {1}".format(validation, self._dcc_handler.name))

        # resolve the publish data path
        _publishes = self._work_object.scan_publishes()

        # get the latest version of the publish

        # find the latest publish version
        _publish_versions = [data.version for publish_path, data in _publishes.items()]

        latest_publish_version = 0 if not _publish_versions else max(_publish_versions)

        # self._abs_publish_data_folder = self._work_object.get_abs_database_path("publish", self._work_object.name)
        #
        # # if the folder exists, get the highest version and increment it by 1
        # if pathlib.Path(self._abs_publish_data_folder).exists():
        #     _publishes = self.get_publishes_in_folder(self._abs_publish_data_folder)
        #     _publish_versions = [publish.version for publish in _publishes]
        #     latest_publish_version = max(_publish_versions) if _publish_versions else 0
        # else:
        #     latest_publish_version = 0

        self._publish_file_name = f"{self._work_object.name}_v{latest_publish_version+1:03d}.tpub"


    def reserve(self):
        """Reserve the slot for publish.

        Makes sure that the publish is not overriden by other users during the process.
        """
        # make sure the publish file is not already exists
        _publish_file_path = pathlib.Path(self._abs_publish_data_folder) / self._publish_file_name
        if _publish_file_path.exists():
            raise ValueError(f"Publish file already exists. {_publish_file_path}")

        # add the publish to the work object
        # self._work_object


    def validate(self):
        """Validate the scene."""
        pass

    def extract(self):
        """Extract the elements."""
        for extract_name, extract_class in self._dcc_handler.extracts.items():
            extractor = extract_class() # initialize the extractor
            extractor.category = self._work_object.category # define the category


    def publish(self):
        """Finalize the publish by updating the reserved slot."""
        pass


    def get_publishes_in_folder(self, folder_path):
        """Get the publishes in the given folder path."""
        _publishes = []
        for _file in pathlib.Path(folder_path).glob("*.tpub"):
            _publishes.append(Publish(_file))
        return _publishes