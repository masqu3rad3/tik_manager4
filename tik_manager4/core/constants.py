"""Constants used in the Tik Manager application."""

from dataclasses import dataclass
from enum import Enum

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
