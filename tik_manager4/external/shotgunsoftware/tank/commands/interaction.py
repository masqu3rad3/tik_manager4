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
Interfaces for prompting the user for input during tank command execution.
"""

from __future__ import print_function
from .. import LogManager
from tank_vendor.six.moves import input


log = LogManager.get_logger(__name__)


class CommandInteraction(object):
    """
    Base class interface for tank command interaction.
    This can be subclassed in order to provide a custom
    interaction environment when running commands in
    API mode.

    In order to override the built-in interaction behavior,
    pass an instance of a command interaction class to
    the :meth:`sgtk.SgtkSystemCommand.execute` method.
    """

    def __init__(self):
        pass

    @property
    def supports_interaction(self):
        """
        True if interaction is supported, false if not.
        Implementations returning ``False`` here typically
        implement other methods by returning default values
        without prompting the user for feedback.
        """
        raise NotImplementedError

    def request_input(self, message):
        """
        Request general input from the user.

        :param str message: Message to display
        :returns: Information entered by user.
        :rtype: str
        """
        raise NotImplementedError

    def ask_yn_question(self, message):
        """
        Prompts the user with a yes/no question.

        :param str message: Message to display
        :returns: True if user selects yes, false if no.
        """
        raise NotImplementedError

    def ask_yna_question(self, message, force_prompt=False):
        """
        Prompts the user with a yes/no/always question.

        Always means that further calls to this method will return True.

        :param str message: Message to display
        :param bool force_prompt: Force a prompt, even if always
            has been selected in the past.
        :returns: True if user selects yes, false if no.
        """
        raise NotImplementedError


class RawInputCommandInteraction(CommandInteraction):
    """
    Interaction interface that uses stdout/stdin for prompting.
    """

    def __init__(self):
        self._ask_questions = True

    @property
    def supports_interaction(self):
        """
        True if interaction is supported, false if not.
        """
        return True

    def request_input(self, message):
        """
        Request general input from the user.

        :param str message: Message to display
        :returns: Information entered by user.
        :rtype: str
        """
        return input(message)

    def ask_yn_question(self, message):
        """
        Prompts the user with a yes/no question.

        :param str message: Message to display
        :returns: True if user selects yes, false if no.
        """
        answer = input("%s [yn]" % message)
        answer = answer.lower()
        if answer != "n" and answer != "y":
            print("Press y for YES, n for NO")
            answer = input("%s [yn]" % message)

        if answer == "y":
            return True

        return False

    def ask_yna_question(self, message, force_prompt=False):
        """
        Prompts the user with a yes/no/always question.

        Always means that further calls to this method will return True.

        :param str message: Message to display
        :param bool force_prompt: Force a prompt, even if always
            has been selected in the past.
        :returns: True if user selects yes, false if no.
        """
        if not self._ask_questions and not force_prompt:
            # auto-press YES
            return True

        answer = input("%s [Yna?]" % message)
        answer = answer.lower()
        if answer != "n" and answer != "a" and answer != "y" and answer != "":
            print("Press ENTER or y for YES, n for NO and a for ALWAYS.")
            answer = input("%s [Yna?]" % message)

        if answer == "a":
            self._ask_questions = False
            return True

        if answer == "y" or answer == "":
            return True

        return False


class YesToEverythingInteraction(CommandInteraction):
    """
    Interaction interface that says yes to everything.
    """

    @property
    def supports_interaction(self):
        """
        True if interaction is supported, false if not.
        """
        return False

    def request_input(self, message):
        """
        Request general input from the user.

        :param str message: Message to display
        :returns: Information entered by user.
        :rtype: str
        """
        raise RuntimeError("Cannot prompt user for input")

    def ask_yn_question(self, message):
        """
        Prompts the user with a yes/no question.

        :param str message: Message to display
        :returns: True if user selects yes, false if no.
        """
        return True

    def ask_yna_question(self, message, force_prompt=False):
        """
        Prompts the user with a yes/no/always question.

        Always means that further calls to this method will return True.

        :param str message: Message to display
        :param bool force_prompt: Force a prompt, even if always
            has been selected in the past.
        :returns: True if user selects yes, false if no.
        """
        return True
