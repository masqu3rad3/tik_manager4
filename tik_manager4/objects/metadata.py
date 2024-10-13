"""Module to hold and manage metadata."""
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
        super().__init__(data_dictionary)

        # create a Metaitem for each key in the data_dictionary
        for key, val in data_dictionary.items():
            self.add_item(key, val)

    def add_item(self, key, value, overridden=False):
        """Add an item to the metadata.

        Args:
            key (str): The key to add.
            value (any): The value to add.
            overridden (bool): Whether the value is overridden or
                inheriting from the parent.

        Returns:
            Metaitem: The Metaitem object that was created.
        """
        self[key] = Metaitem(value, overridden=overridden)
        return self[key]

    def get_all_items(self):
        """Return all items in the metadata."""
        for key, val in self.items():
            yield key, val.value

    def get_value(self, key, fallback_value=None):
        """Get the value of a key.

        Args:
            key (str): The key to get the value of.
            fallback_value (any): The value to return if the key is not found.
        """
        if key in self:
            return self[key].value
        return fallback_value

    def is_overridden(self, key):
        """Check if a key is overridden.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if the key is overridden, False otherwise.
        """
        if key in self:
            return self[key].overridden
        return False

    def override(self, data_dictionary):
        """Override the metadata with a new dictionary.

        Args:
            data_dictionary (dict): The dictionary to override the metadata with.
        """
        # clear metadata
        for key, data in data_dictionary.items():
            self[key] = Metaitem(data, overridden=True)

    def copy(self):
        """Return a copy of the metadata."""
        return Metadata(dict(self.get_all_items()))

    def exists(self, key):
        """Check if the key exists."""
        return key in self

class FilteredData(dict):
    """Class to filter the overridden and new data."""
    def __init__(self, **kwargs):
        super(FilteredData, self).__init__()
        self.update(kwargs)

    def update_overridden_data(self, settings_data):
        for key, value in settings_data.get_data().items():
            # if it starts __override, skip
            if key.startswith("__override"):
                continue
            # if the key has a __override key, check if it is True
            _override_key = "__override_{}".format(key)
            if _override_key not in list(settings_data.get_data().keys()):
                self[key] = value
            else:
                if settings_data.get_property(_override_key):
                    self[key] = value

    def update_new_data(self, settings_data):
        for key, value in settings_data.get_data().items():
            if key.startswith("__new"):
                continue
            # if the new checked box is checked, add the key to the filtered_data
            _new_key = "__new_{}".format(key)
            if settings_data.get_property(_new_key):
                self[key] = value