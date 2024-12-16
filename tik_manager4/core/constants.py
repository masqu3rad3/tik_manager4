"""Constants used in the Tik Manager application."""

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
