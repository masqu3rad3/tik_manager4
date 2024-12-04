# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Helper methods that extracts information about the current user.

"""

import os
import sys

from . import constants
from .platforms import is_windows


def get_login_name():
    """
    Retrieves the login name of the current user.
    Returns None if no login name was found
    """
    if is_windows():
        # http://stackoverflow.com/questions/117014/how-to-retrieve-name-of-current-windows-user-ad-or-local-using-python
        return os.environ.get("USERNAME", None)
    else:
        try:
            import pwd

            pwd_entry = pwd.getpwuid(os.geteuid())
            return pwd_entry[0]
        except:
            return None


# note! Because the shotgun caching method can return None, to indicate that no
# user was found, we cannot use a None value to indicate that the cache has not been
# populated.
g_shotgun_user_cache = "unknown"
g_shotgun_current_user_cache = "unknown"


def get_shotgun_user(sg):
    """

    ---- DEPRECATED ---- user get_current_user(tk) instead

    Retrieves a shotgun user dict
    for the current user. Returns None if the user is not found in shotgun.

    Returns the following fields:

    * id
    * type
    * email
    * login
    * name
    * image (thumbnail)

    This method connects to shotgun.
    """
    global g_shotgun_user_cache
    if g_shotgun_user_cache == "unknown":
        fields = ["id", "type", "email", "login", "name", "image"]
        local_login = get_login_name()
        g_shotgun_user_cache = sg.find_one(
            "HumanUser", filters=[["login", "is", local_login]], fields=fields
        )

    return g_shotgun_user_cache


def get_current_user(tk):
    """
    Retrieves the current user as a dictionary of metadata values. Note: This method connects to
    shotgun the first time around. The result is then cached to reduce latency.

    If a user has been authenticated via a login prompt, this method will return the credentials
    associated with that user. If Toolkit has been configured to use a script user to connect to
    Shotgun, a core hook will be executed to established which user is associated with the current
    session. This is usually based on the currently logged in user.

    :returns: None if the user is not found in Shotgun. Otherwise, it returns a dictionary
              with the following fields: id, type, email, login, name, image, firstname, lastname
    """
    global g_shotgun_current_user_cache
    if g_shotgun_current_user_cache != "unknown":
        return g_shotgun_current_user_cache

    # Avoids cyclic imports.
    from .. import api

    user = api.get_authenticated_user()

    # If an authenticated user has been set and it has a name, just use that as login for the
    # Shotgun query. If there is no user, that's probably because we're running in an old
    # script that doesn't use the authenticated user concept. In that case, we'll do what we've
    # always been doing in the past, which is run the hook. Obviously, if the user didn't
    # have a login name (which happens when the authenticated user is a script user), we'll also run
    # the hook as well.
    if user and user.login:
        current_login = user.login
    else:
        current_login = tk.execute_core_hook(constants.CURRENT_LOGIN_HOOK_NAME)

    if current_login is None:
        g_shotgun_current_user_cache = None
    else:
        fields = [
            "id",
            "type",
            "email",
            "login",
            "name",
            "image",
            "firstname",
            "lastname",
        ]
        g_shotgun_current_user_cache = tk.shotgun.find_one(
            "HumanUser", filters=[["login", "is", current_login]], fields=fields
        )

    return g_shotgun_current_user_cache
