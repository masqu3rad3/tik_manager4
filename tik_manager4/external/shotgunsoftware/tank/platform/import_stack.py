# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Manages a thread-safe stack of Toolkit imports.
"""

import threading


class ImportStack(object):
    """
    Manages a thread-safe stack of Toolkit imports. Used in conjunction with the
    _get_current_bundle() method - for more details, see platform/util.py.
    """

    # global variable that holds a stack of references to
    # a current bundle object, per thread - this variable is populated
    # whenever the bundle.import_module method is executed
    # and is a way for import_framework() to be able to resolve
    # the current bundle even when being recursively called
    # inside an import_module call.
    # By using a threadlocal storage, we effectively maintain one stack per
    # thread. This allows for threadsafe execution and imports, where two pieces
    # of different code can execute in parallel and resolve the correct imports.
    __threadlocal_storage = threading.local()

    @classmethod
    def get_current_bundle(cls):
        """
        Retrieves the bundle currently importing from.

        :returns: The TankBundle currently importing from.
        """
        import_stack = cls._get_thread_import_stack()
        if len(import_stack) > 0:
            return import_stack[-1]
        return None

    @classmethod
    def push_current_bundle(cls, bundle):
        """
        Sets which bundle we are currently importing from.

        :param bundle: Bundle we are importing from.
        """
        cls._get_thread_import_stack().append(bundle)

    @classmethod
    def pop_current_bundle(cls):
        """
        Pops the current bundle we're importing from from the stack.
        """
        cls._get_thread_import_stack().pop()

    @classmethod
    def _get_thread_import_stack(cls):
        """
        Gets the import stack for the current thread.

        :returns: A list of TankBundles.
        """
        if not hasattr(cls.__threadlocal_storage, "import_stack"):
            cls.__threadlocal_storage.import_stack = []
        return cls.__threadlocal_storage.import_stack
