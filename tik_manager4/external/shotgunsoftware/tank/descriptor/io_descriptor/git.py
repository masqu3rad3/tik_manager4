# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
import os
import uuid
import shutil
import tempfile
import subprocess

from .downloadable import IODescriptorDownloadable
from ... import LogManager
from ...util.process import subprocess_check_output, SubprocessCalledProcessError

from ..errors import TankError
from ...util import filesystem
from ...util import is_windows

log = LogManager.get_logger(__name__)


def _can_hide_terminal():
    """
    Ensures this version of Python can hide the terminal of a subprocess
    launched with the subprocess module.
    """
    try:
        # These values are not defined between Python 2.6.6 and 2.7.1 inclusively.
        subprocess.STARTF_USESHOWWINDOW
        subprocess.SW_HIDE
        return True
    except Exception:
        return False


def _check_output(*args, **kwargs):
    """
    Wraps the call to subprocess_check_output so it can run headless on Windows.
    """
    if is_windows() and _can_hide_terminal():
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        kwargs["startupinfo"] = startupinfo

    return subprocess_check_output(*args, **kwargs)


class TankGitError(TankError):
    """
    Errors related to git communication
    """

    pass


class IODescriptorGit(IODescriptorDownloadable):
    """
    Base class for git descriptors.

    Abstracts operations around repositories, since all git
    descriptors have a repository associated (via the 'path'
    parameter).
    """

    def __init__(self, descriptor_dict, sg_connection, bundle_type):
        """
        Constructor

        :param descriptor_dict: descriptor dictionary describing the bundle
        :param sg_connection: Shotgun connection to associated site.
        :param bundle_type: Either AppDescriptor.APP, CORE, ENGINE or FRAMEWORK.
        :return: Descriptor instance
        """
        super(IODescriptorGit, self).__init__(
            descriptor_dict, sg_connection, bundle_type
        )

        self._path = descriptor_dict.get("path")
        # strip trailing slashes - this is so that when we build
        # the name later (using os.basename) we construct it correctly.
        if self._path.endswith("/") or self._path.endswith("\\"):
            self._path = self._path[:-1]

    @LogManager.log_timing
    def _clone_then_execute_git_commands(
        self, target_path, commands, depth=None, ref=None, is_latest_commit=None
    ):
        """
        Clones the git repository into the given location and
        executes the given list of git commands::

            # this will clone the associated git repo into
            # /tmp/foo and then execute the given commands
            # in order in a shell environment
            commands = [
                "checkout -q my_feature_branch",
                "reset -q --hard -q a6512356a"
            ]
            self._clone_then_execute_git_commands("/tmp/foo", commands)

        The initial clone operation happens via the subprocess module, ensuring
        there is no terminal that will pop for credentials, leading to a more
        seamless experience. If the operation failed, we try a second time with
        os.system, ensuring that there is an initialized shell environment, allowing
        git to potentially request shell based authentication for repositories
        which require credentials.

        The subsequent list of commands are intended to be executed on the
        recently cloned repository and will the cwd will be set so that they
        are executed in the directory scope of the newly cloned repository.

        :param target_path: path to clone into
        :param commands: list git commands to execute, e.g. ['checkout x']
        :param depth: depth of the clone, allows shallow clone
        :param ref: git ref to checkout - it can be commit, tag or branch
        :returns: stdout and stderr of the last command executed as a string
        :raises: TankGitError on git failure
        """
        # ensure *parent* folder exists
        parent_folder = os.path.dirname(target_path)

        filesystem.ensure_folder_exists(parent_folder)

        # first probe to check that git exists in our PATH
        log.debug("Checking that git exists and can be executed...")
        try:
            output = _check_output(["git", "--version"])
        except:
            log.exception("Unexpected error:")
            raise TankGitError(
                "Cannot execute the 'git' command. Please make sure that git is "
                "installed on your system and that the git executable has been added to the PATH."
            )

        log.debug("Git installed: %s" % output)

        # Make sure all git commands are correct according to the descriptor type
        cmd = self._validate_git_commands(
            target_path, depth=depth, ref=ref, is_latest_commit=is_latest_commit
        )

        run_with_os_system = True

        # We used to call only os.system here. On macOS and Linux this behaved correctly,
        # i.e. if stdin was open you would be prompted on the terminal and if not then an
        # error would be raised. This is the best we could do.
        #
        # However, for Windows, os.system actually pops a terminal, which is annoying, especially
        # if you don't require to authenticate. To avoid this popup, we will first launch
        # git through the subprocess module and instruct it to not show a terminal for the
        # subprocess.
        #
        # If that fails, then we'll assume that it failed because credentials were required.
        # Unfortunately, we can't tell why it failed.
        #
        # Note: We only try this workflow if we can actually hide the terminal on Windows.
        # If we can't there's no point doing all of this and we should just use
        # os.system.
        if is_windows() and _can_hide_terminal():
            log.debug("Executing command '%s' using subprocess module." % cmd)
            try:
                # It's important to pass GIT_TERMINAL_PROMPT=0 or the git subprocess will
                # just hang waiting for credentials to be entered on the missing terminal.
                # I would have expected Windows to give an error about stdin being close and
                # aborting the git command but at least on Windows 10 that is not the case.
                environ = {}
                environ.update(os.environ)
                environ["GIT_TERMINAL_PROMPT"] = "0"
                _check_output(cmd, env=environ)

                # If that works, we're done and we don't need to use os.system.
                run_with_os_system = False
                status = 0
            except SubprocessCalledProcessError:
                log.debug("Subprocess call failed.")

        if run_with_os_system:
            # Make sure path and repo path are quoted.
            log.debug("Executing command '%s' using os.system" % cmd)
            log.debug(
                "Note: in a terminal environment, this may prompt for authentication"
            )
            status = os.system(cmd)

        log.debug("Command returned exit code %s" % status)
        if status != 0:
            raise TankGitError(
                "Error executing git operation. The git command '%s' "
                "returned error code %s." % (cmd, status)
            )
        log.debug("Git clone into '%s' successful." % target_path)

        # clone worked ok! Now execute git commands on this repo

        output = None

        # note: for windows, we use git -C to point git to the right current
        # working directory. This requires git 1.9+. This is to ensure that
        # the solution handles UNC paths, which do not support os.getcwd() operations.
        #
        # for other platforms, we omit -C to ensure compatibility with older versions
        # of git. Centos 7 still ships with 1.8.

        cwd = os.getcwd()
        try:
            if not is_windows():
                log.debug("Setting cwd to '%s'" % target_path)
                os.chdir(target_path)

            for command in commands:

                if is_windows():
                    # we use git -C to specify the working directory where to execute the command
                    # this option was added in as part of git 1.9
                    # and solves an issue with UNC paths on windows.
                    full_command = 'git -C "%s" %s' % (target_path, command)
                else:
                    full_command = "git %s" % command

                log.debug("Executing '%s'" % full_command)
                try:
                    output = _check_output(full_command, shell=True)

                    # note: it seems on windows, the result is sometimes wrapped in single quotes.
                    output = output.strip().strip("'")

                except SubprocessCalledProcessError as e:
                    raise TankGitError(
                        "Error executing git operation '%s': %s (Return code %s)"
                        % (full_command, e.output, e.returncode)
                    )
                log.debug("Execution successful. stderr/stdout: '%s'" % output)
        finally:
            if not is_windows():
                log.debug("Restoring cwd (to '%s')" % cwd)
                os.chdir(cwd)

        # return the last returned stdout/stderr
        return output

    def _tmp_clone_then_execute_git_commands(self, commands, depth=None, ref=None):
        """
        Clone into a temp location and executes the given
        list of git commands.

        For more details, see :meth:`_clone_then_execute_git_commands`.

        :param commands: list git commands to execute, e.g. ['checkout x']
        :returns: stdout and stderr of the last command executed as a string
        """
        clone_tmp = os.path.join(
            tempfile.gettempdir(), "sgtk_clone_%s" % uuid.uuid4().hex
        )
        filesystem.ensure_folder_exists(clone_tmp)
        try:
            return self._clone_then_execute_git_commands(
                clone_tmp, commands, depth, ref
            )
        finally:
            log.debug("Cleaning up temp location '%s'" % clone_tmp)
            shutil.rmtree(clone_tmp, ignore_errors=True)

    def get_system_name(self):
        """
        Returns a short name, suitable for use in configuration files
        and for folders on disk, e.g. 'tk-maya'
        """
        bn = os.path.basename(self._path)
        (name, ext) = os.path.splitext(bn)
        return name

    def has_remote_access(self):
        """
        Probes if the current descriptor is able to handle
        remote requests. If this method returns, true, operations
        such as :meth:`download_local` and :meth:`get_latest_version`
        can be expected to succeed.

        :return: True if a remote is accessible, false if not.
        """
        # check if we can clone the repo
        can_connect = True
        try:
            log.debug("%r: Probing if a connection to git can be established..." % self)
            # clone repo into temp folder
            self._tmp_clone_then_execute_git_commands([], depth=1)
            log.debug("...connection established")
        except Exception as e:
            log.debug("...could not establish connection: %s" % e)
            can_connect = False
        return can_connect

    def _copy(self, target_path, skip_list=None):
        """
        Copy the contents of the descriptor to an external location

        Subclassed git implementation which includes .git folders
        in the copy, unless they are specifically skipped by the skip_list.

        :param target_path: target path to copy the descriptor to.
        :param skip_list: List of folders or files that should not be copied into the destination.

        .. note::
            The folders or files specified must be at the root of the bundle.
        """
        log.debug("Copying %r -> %s" % (self, target_path))
        # make sure item exists locally
        self.ensure_local()
        # copy descriptor into target.
        # the skip list contains .git folders by default, so pass in []
        # to turn that restriction off. In the case of the git descriptor,
        # we want to transfer this folder as well.
        filesystem.copy_folder(
            self.get_path(),
            target_path,
            # Make we do not pass none or we will be getting the default skip list.
            skip_list=skip_list or [],
        )

    def _validate_git_commands(
        self, target_path, depth=None, ref=None, is_latest_commit=None
    ):
        """
        Validate that git commands are correct according to the descriptor type
        avoiding shallow git clones when tracking against commits in a git branch.
        :param target_path: path to clone into
        :param depth: depth of the clone, allows shallow clone
        :param ref: git ref to checkout - it can be commit, tag or branch
        :returns: str git commands to execute
        """
        # Note: git doesn't like paths in single quotes when running on
        # windows - it also prefers to use forward slashes
        #
        # Also note - we are adding a --no-hardlinks flag here to ensure that
        # when a github repo resides locally on a drive, git isn't trying
        # to be clever and utilize hard links to save space - this can cause
        # complications in cleanup scenarios and with file copying. We want
        # each repo that we clone to be completely independent on a filesystem level.
        log.debug("Git Cloning %r into %s" % (self, target_path))
        depth = "--depth %s" % depth if depth else ""
        ref = "-b %s" % ref if ref else ""
        cmd = 'git clone --no-hardlinks -q "%s" %s "%s" %s' % (
            self._path,
            ref,
            target_path,
            depth,
        )
        if self._descriptor_dict.get("type") == "git_branch":
            if not is_latest_commit:
                if "--depth" in cmd:
                    depth = ""
                    cmd = 'git clone --no-hardlinks -q "%s" %s "%s" %s' % (
                        self._path,
                        ref,
                        target_path,
                        depth,
                    )

        return cmd
