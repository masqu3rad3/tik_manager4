# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
System settings management.
"""


from tank_vendor.six.moves import urllib


class SystemSettings(object):
    """
    Handles loading the system settings.
    """

    @property
    def http_proxy(self):
        """
        Retrieves the operating system http proxy.

        First, the method scans the environment for variables named http_proxy, in case insensitive way.
        If both lowercase and uppercase environment variables exist (and disagree), lowercase is preferred.

        When the method cannot find such environment variables:
        - for Mac OS X, it will look for proxy information from Mac OS X System Configuration,
        - for Windows, it will look for proxy information from Windows Systems Registry.

        .. note:: There is a restriction when looking for proxy information from
                  Mac OS X System Configuration or Windows Systems Registry:
                  in these cases, the Toolkit does not support the use of proxies
                  which require authentication (username and password).
        """
        # Get the dictionary of scheme to proxy server URL mappings; for example:
        #     {"http": "http://foo:bar@74.50.63.111:80", "https": "http://74.50.63.111:443"}
        # "getproxies" scans the environment for variables named <scheme>_proxy, in case insensitive way.
        # When it cannot find it, for Mac OS X it looks for proxy information from Mac OSX System Configuration,
        # and for Windows it looks for proxy information from Windows Systems Registry.
        # If both lowercase and uppercase environment variables exist (and disagree), lowercase is preferred.
        # Note the following restriction: "getproxies" does not support the use of proxies which
        # require authentication (user and password) when looking for proxy information from
        # Mac OSX System Configuration or Windows Systems Registry.
        system_proxies = urllib.request.getproxies()

        # Get the http proxy when it exists in the dictionary.
        proxy = system_proxies.get("http")

        if proxy:
            # Remove any spurious "http://" from the http proxy string.
            proxy = proxy.replace("http://", "", 1)

        return proxy
