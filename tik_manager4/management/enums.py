"""Enumeration of object types."""

from enum import Enum

class EventType(Enum):
    """Enumeration of object types."""
    NEW_ASSET = "new_asset"
    NEW_SHOT = "new_shot"
    NEW_SEQUENCE = "new_sequence"
    NEW_EPISODE = "new_episode"
    UPDATE_ASSET = "update_asset"
    UPDATE_SHOT = "update_shot"
    UPDATE_SEQUENCE = "update_sequence"
    UPDATE_EPISODE = "update_episode"
    DELETE_ASSET = "delete_asset"
    DELETE_SHOT = "delete_shot"
    DELETE_SEQUENCE = "delete_sequence"
    DELETE_EPISODE = "delete_episode"
    NEW_TASK = "new_task"
    DELETE_TASK = "delete_task"

