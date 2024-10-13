# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Implements a caching mechanism to avoid loading the same yaml file multiple times
unless it's changed on disk.
"""

from __future__ import with_statement

import os
import copy
import threading
from tank_vendor import six

from tank_vendor import yaml
from ..errors import TankError, TankUnreadableFileError, TankFileDoesNotExistError


class CacheItem(object):
    """
    Represents a single item in the global yaml cache.

    Each item carries with it a set of data, an stat from the .yml file that
    it was sourced from (in os.stat form), and the path to the .yml file that
    was sourced.
    """

    def __init__(self, path, data=None, stat=None):
        """
        Initializes the item.

        :param path:    The path to the .yml file on disk.
        :param data:    The data sourced from the .yml file.
        :param stat:    The stat of the file on disk. If not provided, an os.stat
                        will be run and the result stored.
        :raises:        tank.errors.TankUnreadableFileError: File stat failure.
        """
        self._path = os.path.normpath(path)
        self._data = data

        if stat is None:
            try:
                self._stat = os.stat(self.path)
            except Exception as exc:
                raise TankUnreadableFileError(
                    "Unable to stat file '%s': %s" % (self.path, exc)
                )
        else:
            self._stat = stat

    def _get_data(self):
        """The item's data."""
        return self._data

    def _set_data(self, config_data):
        self._data = config_data

    data = property(_get_data, _set_data)

    @property
    def path(self):
        """The path to the file on disk that the item was sourced from."""
        return self._path

    @property
    def stat(self):
        """The stat of the file on disk that the item was sourced from."""
        return self._stat

    def given_item_newer(self, other):
        """
        Tests whether the given item is newer than this.

        :param other:   The CacheItem to test against.
        :raises:        TypeError: Given item is not a CacheItem.
        :returns:       bool, True if other is newer, False if not.
        """
        if not isinstance(other, CacheItem):
            raise TypeError("Given item must be of type CacheItem.")
        return other.stat.st_mtime > self.stat.st_mtime

    def size_differs(self, other):
        """
        Tests whether the file size of the given item differs from this item.

        :param other:   The CacheItem to test against.
        :raises:        TypeError: Given item is not a CacheItem.
        :returns:       bool, True if other is a different size on disk, False if not.
        """
        if not isinstance(other, CacheItem):
            raise TypeError("Given item must be of type CacheItem.")
        return other.stat.st_size != self.stat.st_size

    def __eq__(self, other):
        if not isinstance(other, CacheItem):
            raise TypeError("Given item must be of type CacheItem.")
        return other.stat.st_mtime == self.stat.st_mtime and not self.size_differs(
            other
        )

    def __getitem__(self, key):
        # Backwards compatibility just in case something outside
        # of this module is expecting the old dict structure.
        if key == "modified_at":
            return self.stat.st_mtime
        elif key == "file_size":
            return self.stat.st_size
        elif key == "data":
            return self._data
        else:
            return getattr(self._data, key)

    def __str__(self):
        return str(self.path)


class YamlCache(object):
    """
    Main yaml cache class
    """

    def __init__(self, cache_dict=None, is_static=False):
        """
        Construction
        """
        self._cache = cache_dict or dict()
        self._lock = threading.Lock()
        self._is_static = is_static

    def _get_is_static(self):
        """
        Whether the cache is considered static or not. If the cache is static,
        CacheItems in the cache will not be invalidated based on file mtime
        and size when they are requested from the cache.
        """
        return self._is_static

    def _set_is_static(self, state):
        self._is_static = bool(state)

    is_static = property(_get_is_static, _set_is_static)

    def invalidate(self, path):
        """
        Invalidates the cache for a given path. This is usually called when writing
        to a yaml file.
        """
        with self._lock:
            if path in self._cache:
                del self._cache[path]

    def get(self, path, deepcopy_data=True):
        """
        Retrieve the yaml data for the specified path.  If it's not already
        in the cache of the cached version is out of date then this will load
        the Yaml file from disk.

        :param path:            The path of the yaml file to load.
        :param deepcopy_data:   Return deepcopy of data. Default is True.
        :returns:               The raw yaml data loaded from the file.
        """
        # Adding a new CacheItem to the cache will cause the file mtime
        # and size on disk to be checked against existing cache data,
        # then the loading of the yaml data if necessary before returning
        # the appropriate item back to us, which will be either the new
        # item we have created here with the yaml data stored within, or
        # the existing cached data.
        item = self._add(CacheItem(path))

        # If asked to, return a deep copy of the cached data to ensure that
        # the cached data is not updated accidentally!
        if deepcopy_data:
            return copy.deepcopy(item.data)
        else:
            return item.data

    def get_cached_items(self):
        """
        Returns a list of all CacheItems stored in the cache.
        """
        return list(self._cache.values())

    def merge_cache_items(self, cache_items):
        """
        Merges the given CacheItem objects into the cache if they are newer
        or of a different size on disk than what's already in the cache.

        :param cache_items: A list of CacheItem objects.
        """
        for item in cache_items:
            self._add(item)

    def _add(self, item):
        """
        Adds the given item to the cache in a thread-safe way. If the given item
        is older (by file mtime) than the existing cache data for that file then
        the already-cached item will be returned. If the item is identical in
        file mtime and file size to what's cached, the already-cached item will be
        returned. Otherwise the item will be added to the cache and returned to
        the caller. If the given item is added to the cache and it has not already
        been populated with the yaml data from disk, that data will be read prior
        to the item being added to the cache.

        :param item:    The CacheItem to add to the cache.
        :returns:       The cached CacheItem.
        """
        self._lock.acquire()

        try:
            path = item.path
            cached_item = self._cache.get(path)

            # If this is a static cache, we won't do any checks on
            # mod time and file size. If it's in the cache we return
            # it, otherwise we populate the item data from disk, cache
            # it, and then return it.
            if self.is_static:
                if cached_item:
                    return cached_item
                else:
                    if not item.data:
                        self._populate_cache_item_data(item)
                    self._cache[path] = item
                    return item
            else:
                # Since this isn't a static cache, we need to make sure
                # that we don't need to invalidate and recache this item
                # based on mod time and file size on disk.
                if cached_item and cached_item == item:
                    # It's already in the cache and matches mtime
                    # and file size, so we can just return what we
                    # already have. It's technically identical in
                    # terms of data of what we got, but it's best
                    # to return the instance we have since that's
                    # what previous logic in the cache did.
                    return cached_item
                else:
                    # Load the yaml data from disk. If it's not already populated.
                    if not item.data:
                        self._populate_cache_item_data(item)
                    self._cache[path] = item
                    return item
        finally:
            self._lock.release()

    def _populate_cache_item_data(self, item):
        """
        Loads the CacheItem's YAML data from disk.
        """
        path = item.path
        try:
            if six.PY2:
                with open(path, "r") as fh:
                    raw_data = yaml.load(fh, Loader=yaml.FullLoader)
            else:
                # For Python 3 or above use the 'utf8' encoding to avoid
                # 'UnicodeDecodeError' when using non utf-8
                # special encoding standards.
                with open(path, "r", encoding="utf8") as fh:
                    raw_data = yaml.load(fh, Loader=yaml.FullLoader)
        except IOError:
            raise TankFileDoesNotExistError("File does not exist: %s" % path)
        except Exception as e:
            raise TankError(
                "Could not open file '%s'. Error reported: '%s'" % (path, e)
            )
        # Populate the item's data before adding it to the cache.
        item.data = raw_data


# The global instance of the YamlCache.
g_yaml_cache = YamlCache()
