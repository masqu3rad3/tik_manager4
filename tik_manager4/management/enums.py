"""Enumeration of object types."""

from enum import Enum

class EventType(Enum):
    """Enumeration of object types."""
    NEW_ASSET = "new_asset"
    NEW_SHOT = "new_shot"
    UPDATE_ASSET = "update_asset"
    UPDATE_SHOT = "update_shot"
