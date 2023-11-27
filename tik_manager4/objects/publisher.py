# pylint: disable=super-with-arguments
# pylint: disable=consider-using-f-string
"""Publisher Handler."""

from pathlib import Path

from tik_manager4.core import filelog

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")

from tik_manager4 import dcc
from tik_manager4.objects.publish import PublishVersion

class Publisher():
    _dcc_handler = dcc.Dcc()

    def __init__(self, project_object):
        """Initialize the Publisher object."""
        self._project_object = project_object
        self._work_object = None
        self._work_version = None

        # resolved variables
        self._resolved_extractors = {}
        self._resolved_validators = {}
        self._abs_publish_data_folder = None
        self._abs_publish_scene_folder = None
        self._publish_file_name = None
        self._publish_version = None

        # classs variables

        self._published_object = None

    @property
    def validators(self):
        """Return the validators."""
        return self._resolved_validators

    @property
    def extractors(self):
        """Return the extractors."""
        return self._resolved_extractors

    def resolve(self):
        """Resolve the validations, extracts, variables, etc."""
        self._work_object, self._work_version = self._project_object.get_current_work()

        if not self._work_object:
            LOG.warning("No work object found. Aborting.")
            return False

        _category_definitons = self._work_object.guard.category_definitions
        extracts = _category_definitons.properties.get(self._work_object.category, {}).get("extracts", [])
        validations = _category_definitons.properties.get(self._work_object.category, {}).get("validations", [])
        # collect the matching extracts and validations from the dcc_handler.
        for extract in extracts:
            if extract in list(self._dcc_handler.extracts.keys()):
                self._resolved_extractors[extract] = self._dcc_handler.extracts[extract]()
            else:
                LOG.warning("Extract {0} defined in category settings but it is not available on {1}".format(extract, self._dcc_handler.name))
        for validation in validations:
            print("validation", self._dcc_handler.validations.keys())
            if validation in list(self._dcc_handler.validations.keys()):
                self._resolved_validators[validation] = self._dcc_handler.validations[validation]()
            else:
                LOG.warning("Validation {0} defined in category settings but it is not available on {1}".format(validation, self._dcc_handler.name))

        latest_publish_version = self._work_object.publish.get_last_version()
        # # resolve the publish data path
        # _publishes = self._work_object.scan_publishes()
        #
        # # get the latest version of the publish
        #
        # # find the latest publish version
        # _publish_versions = [data.version for publish_path, data in _publishes.items()]
        #
        # latest_publish_version = 0 if not _publish_versions else max(_publish_versions)

        # self._abs_publish_data_folder = self._work_object.get_abs_database_path("publish", self._work_object.name)
        # self._abs_publish_scene_folder = self._work_object.get_abs_project_path("publish", self._work_object.name)
        self._abs_publish_data_folder = self._work_object.publish.get_publish_data_folder()
        self._abs_publish_scene_folder = self._work_object.publish.get_publish_scene_folder()
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

        self._published_object = PublishVersion(str(_publish_file_path))

        self._published_object.add_property("name", self._work_object.name)
        self._published_object.add_property("creator", self._work_object.guard.user)
        self._published_object.add_property("category", self._work_object.category)
        self._published_object.add_property("dcc", self._work_object.guard.dcc)
        self._published_object.add_property("publish_id", self._published_object.generate_id())
        self._published_object.add_property("version", self._publish_version)
        self._published_object.add_property("work_version", self._work_version)
        self._published_object.add_property("task_name", self._work_object.task_name)
        self._published_object.add_property("task_id", self._work_object.task_id)
        self._published_object.add_property("path", Path(self._work_object.path, "publish").as_posix())
        self._published_object.add_property("dcc_version", self._dcc_handler.get_dcc_version())
        self._published_object.add_property("elements", [])

        self._published_object.apply_settings() # make sure the file is created
        self._published_object.init_properties() # make sure the properties are initialized
        # add the publish to the work object
        # self._work_object


    def validate(self):
        """Validate the scene."""
        for val_name, val_object in self._resolved_validators.items():
            val_object.validate()


    def extract(self):
        """Extract the elements."""
        # first save the scene
        self._dcc_handler.save_scene()
        publish_path = Path(self._work_object.get_abs_project_path("publish", self._work_object.name))
        for extract_type_name, extract_object in self._resolved_extractors.items():
            extract_object.category = self._work_object.category # define the category
            extract_object.extract_folder = str(publish_path) # define the extract folder
            extract_object.extract_name = f"{self._work_object.name}_v{self._publish_version:03d}" # define the extract name
            extract_object.extract()


    def publish(self):
        """Finalize the publish by updating the reserved slot."""\

        # collect the validation states and log it into the publish object
        validations = {}
        for validation_name, validation_object in self._resolved_validators.items():
            validations[validation_name] = validation_object.state
        self._published_object.add_property("validations", validations)

        # collect the extracted elements information and add to the publish object
        for extract_type_name, extract_object in self._resolved_extractors.items():
            element = {
                "type": extract_object.name,
                # get the relative path to the project
                # "path": Path(extract_object.resolve_output()).relative_to(self._work_object.guard.project_root).as_posix()
                "path": Path(extract_object.resolve_output()).relative_to(self._published_object.get_abs_project_path()).as_posix()
            }
            self._published_object._elements.append(element)

        self._published_object.edit_property("elements", self._published_object._elements)
        self._published_object.apply_settings(force=True)

    @property
    def publish_version(self):
        """Return the resolved publish version."""
        return self._publish_version

    # @property
    # def extract_names(self):
    #     """Return the resolved extract names."""
    #     return list(self._resolved_extractors.keys())
    #
    # @property
    # def validation_names(self):
    #     """Return the resolved validation names."""
    #     return list(self._resolved_validators.keys())

    @property
    def publish_name(self):
        """Return the resolved publish name."""
        return self._publish_file_name

    @property
    def absolute_data_path(self):
        """Return the resolved absolute data path."""
        return self._abs_publish_data_folder

    @property
    def absolute_scene_path(self):
        """Return the resolved absolute scene path."""
        return self._abs_publish_scene_folder

    @property
    def relative_data_path(self):
        """Return the resolved relative path."""
        if self._work_object:
            return Path(self._abs_publish_data_folder).relative_to(self._work_object.guard.project_root).as_posix()
        else:
            return None

    @property
    def relative_scene_path(self):
        """Return the resolved relative path."""
        if self._work_object:
            return Path(self._abs_publish_scene_folder).relative_to(self._work_object.guard.project_root).as_posix()
        else:
            return None


