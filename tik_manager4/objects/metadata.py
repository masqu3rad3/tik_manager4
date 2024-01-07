"""Classes to hold and manage metadata."""
import dataclasses
from typing import Union


@dataclasses.dataclass
class Metaitem:
    """Hold the value and overridden status of a property."""
    value: Union[str, int, float, bool, list, dict, None]
    overridden: bool

class Metadata(dict):
    """Metadata class."""
    def __init__(self, data_dictionary):
        """Initialize Metadata object.
        Args:
            data_dictionary (dict): The dictionary to initialize the metadata with.
        """
        super(Metadata, self).__init__(data_dictionary)

        # create a Metaitem for each key in the data_dictionary
        for key, val in data_dictionary.items():
            self.add_item(key, val)

    def add_item(self, key, value, overridden=False):
        """Add an item to the metadata."""
        self[key] = Metaitem(value, overridden=overridden)
        return self[key]

    def get_all_items(self):
        """Return all items in the metadata."""
        for key, val in self.items():
            yield key, val.value

    def get_value(self, key, fallback_value=None):
        """Get the value of a key."""
        if key in self:
            return self[key].value
        return fallback_value

    def is_overridden(self, key):
        """Check if a key is overridden."""
        if key in self:
            return self[key].overridden
        return False

    def override(self, data_dictionary):
        """Override the metadata with a new dictionary."""
        # clear metadata
        for key, data in data_dictionary.items():
            self[key] = Metaitem(data, overridden=True)

    def exists(self, key):
        """Check if the key exists."""
        return key in self
