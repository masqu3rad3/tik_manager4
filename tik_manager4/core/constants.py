"""Constants used in the Tik Manager application."""

from dataclasses import dataclass
from enum import Enum

class ColorCodes(Enum):
    """Enumeration of color codes."""
    DELETED = "#FF0000"  # Red
    # bright green
    PROMOTED = "#00FF00"  # Green
    # bright purple
    LIVE = "#CA75FF"  # Purple
    # regular white
    NORMAL = "#FFFFFF"  # White

class ObjectType(Enum):
    """Enumeration of object types."""
    ENTITY = "entity"
    WORK_VERSION = "work_version"
    PUBLISH_VERSION = "publish_version"
    WORK = "work"
    PUBLISH = "publish"
    CATEGORY = "category"
    TASK = "task"
    SUBPROJECT = "subproject"
    PROJECT = "project"
    USER = "user"

class ValidationState(Enum):
    """Enumeration of validation states."""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

@dataclass
class ValidationResult:
    """Dataclass to store validation results."""
    state: ValidationState
    message: str
    allow_proceed: bool = False # Allow the user to proceed with the action

class DataTypes(Enum):
    """Widget Data Types."""
    BOOLEAN = "boolean"
    STRING = "string"
    COMBO = "combo"
    INTEGER = "integer"
    FLOAT = "float"
    SPINNERINT = "spinnerInt"
    SPINNERFLOAT = "spinnerFloat"
    LIST = "list"
    DROPLIST = "dropList"
    CATEGORYLIST = "categoryList"
    VALIDATEDSTRING = "validatedString"
    VECTOR2INT = "vector2Int"
    VECTOR2FLOAT = "vector2Float"
    VECTOR3INT = "vector3Int"
    VECTOR3FLOAT = "vector3Float"
    PATHBROWSER = "pathBrowser"
    FILEBROWSER = "fileBrowser"
    SUBPROJECTBROWSER = "subprojectBrowser"
    MULTI = "multi"
    GROUP = "group"
    INFO = "info"
    SEPARATOR = "separator"
    BUTTON = "button"

    @property
    def is_numeric(self):
        return self in [DataTypes.INTEGER, DataTypes.FLOAT, DataTypes.SPINNERINT, DataTypes.SPINNERFLOAT]

    @property
    def is_storable(self):
        """Return True if the data type is storable in the database."""
        return self not in [DataTypes.INFO, DataTypes.SEPARATOR, DataTypes.BUTTON]

    @staticmethod
    def get_storable_types():
        """Return a list of storable data types values."""
        return [dt.value for dt in DataTypes if dt.is_storable]

class BranchingModes(Enum):
    """Enumeration of branching modes."""
    ACTIVE = "Active Branches"
    PASSIVE = "Passive Branches"
