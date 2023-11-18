# pylint: disable=super-with-arguments
# pylint: disable=consider-using-f-string
"""Publisher Handler."""

from pathlib import Path

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
        self._publish_version = None

        # classs variables

        self._published_object = None


    def resolve(self):
        """Resolve the validations, extracts, variables, etc."""

        if not self._work_object:
            LOG.warning("No work object found. Aborting.")
            return False

        _category_definitons = self._work_object.guard.category_definitions
        extracts = _category_definitons.properties.get(self._work_object.category, {}).get("extracts", [])
        validations = _category_definitons.properties.get(self._work_object.category, {}).get("validations", [])
        # collect the matching extracts and validations from the dcc_handler.
        for extract in extracts:
            if extract in list(self._dcc_handler.extracts.keys()):
                self._resolved_extracts[extract] = self._dcc_handler.extracts[extract]()
            else:
                LOG.warning("Extract {0} defined in category settings but it is not available on {1}".format(extract, self._dcc_handler.name))
        for validation in validations:
            print("validation", self._dcc_handler.validations.keys())
            if validation in list(self._dcc_handler.validations.keys()):
                self._resolved_validations[validation] = self._dcc_handler.validations[validation]()
            else:
                LOG.warning("Validation {0} defined in category settings but it is not available on {1}".format(validation, self._dcc_handler.name))

        # resolve the publish data path
        _publishes = self._work_object.scan_publishes()

        # get the latest version of the publish

        # find the latest publish version
        _publish_versions = [data.version for publish_path, data in _publishes.items()]

        latest_publish_version = 0 if not _publish_versions else max(_publish_versions)

        self._abs_publish_data_folder = self._work_object.get_abs_database_path("publish", self._work_object.name)
        #
        # # if the folder exists, get the highest version and increment it by 1
        # if pathlib.Path(self._abs_publish_data_folder).exists():
        #     _publishes = self.get_publishes_in_folder(self._abs_publish_data_folder)
        #     _publish_versions = [publish.version for publish in _publishes]
        #     latest_publish_version = max(_publish_versions) if _publish_versions else 0
        # else:
        #     latest_publish_version = 0
        self._publish_version = latest_publish_version + 1
        self._publish_file_name = f"{self._work_object.name}_v{self._publish_version:03d}.tpub"
        return self._publish_file_name

    def reserve(self):
        """Reserve the slot for publish.

        Makes sure that the publish is not overriden by other users during the process.
        """
        # make sure the publish file is not already exists
        _publish_file_path = Path(self._abs_publish_data_folder) / self._publish_file_name
        if _publish_file_path.exists():
            raise ValueError(f"Publish file already exists. {_publish_file_path}")

        self._published_object = Publish(str(_publish_file_path))

        self._published_object.add_property("name", self._work_object.name)
        self._published_object.add_property("creator", self._work_object.guard.user)
        self._published_object.add_property("category", self._work_object.category)
        self._published_object.add_property("dcc", self._work_object.guard.dcc)
        self._published_object.add_property("publish_id", self._published_object.generate_id())
        self._published_object.add_property("version", self._publish_version)
        self._published_object.add_property("task_name", self._work_object.task_name)
        self._published_object.add_property("task_id", self._work_object.task_id)
        self._published_object.add_property("path", Path(self._work_object.path, "publish").as_posix())
        # self._published_object.add_property("softwareVersion", self._dcc_handler.version)
        self._published_object.add_property("elements", [])

        self._published_object.apply_settings() # make sure the file is created
        # add the publish to the work object
        # self._work_object


    def validate(self):
        """Validate the scene."""
        print(self._dcc_handler.validations)

        for val_name, val_object in self._resolved_validations.items():
            # print(val)
            # validator = self._resolved_validations[val]()
            # self._validator_objects[val] = validator
            # validator.category = self._work_object.category
            val_object.validate()
            print(val_object.state)


    def extract(self):
        """Extract the elements."""
        # first save the scene
        self._dcc_handler.save_scene()
        # scene_file = self._dcc_handler.get_scene_file()
        publish_path = Path(self._work_object.get_abs_project_path("publish", self._work_object.name))
        print("publish_path", publish_path)

        for extract_type_name, extract_object in self._resolved_extracts.items():
            extract_object.category = self._work_object.category.lower() # define the category
            extract_object.extract_folder = str(publish_path) # define the extract folder
            extract_object.extract_name = f"{self._work_object.name}_v{self._publish_version:03d}" # define the extract name
            extract_object.extract()


    def publish(self):
        """Finalize the publish by updating the reserved slot."""
        # collect the extracted elements information and add to the publish object
        for extract_type_name, extract_object in self._resolved_extracts.items():
            element = {
                "type": extract_object.name,
                # get the relative path to the project
                "path": Path(extract_object.resolve_output()).relative_to(self._work_object.guard.project_root).as_posix()
            }
            self._published_object._elements.append(element)

        self._published_object.edit_property("elements", self._published_object._elements)
        self._published_object.apply_settings(force=True)
