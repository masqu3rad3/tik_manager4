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
Default implementation for the Tank Dialog

"""

from . import QtCore, QtGui
from . import ui_tank_dialog
from . import TankDialogBase
from .config_item import ConfigItem
from .. import engine
from .. import application
from .. import constants
from ...errors import TankError

import sys
import os
import inspect
from tank_vendor import six


class TankQDialog(TankDialogBase):
    """
    Wraps around app widgets. Contains Tank specific toolbars and configuration info
    in addition to the user object that it is hosting.
    """

    TOOLBAR_HEIGHT = 45
    GRADIENT_WIDTH = 11
    INFO_WIDTH = 400

    @staticmethod
    def _stop_buggy_background_worker_qthreads(widget):
        """
        There is a bug in the worker/threading code in the BrowserWidget that was fixed
        in v0.1.17 and the tk-multi-workfiles Save As dialog that was fixed in v0.3.22.

        The bug results in a fatal crash if the BrowserWidget is cleaned up properly or
        if the Save As dialog is closed before the thread has completely stopped!

        However, because the engine was previously not releasing any dialogs, the cleanup
        code was never running which meant the bug was hidden!

        Now the engine has been fixed so that it cleans up correctly, all old versions
        of Multi Publish and apps using a pre-v0.1.17 version of the BrowserWidget became
        extremely unstable.

        As a workaround, this function finds all pre-v0.1.17 BrowserWidgets and
        pre-v0.3.22 SaveAsForms and applies a fix (basically waits for the worker thread
        to stop) to avoid instability!
        """
        checked_classes = {}

        widgets = [widget]
        for w in widgets:

            # look through class hierarchy - can't use isinstance here
            # because we don't know which module the BrowserWidget would
            # be from!
            cls_type = None
            for cls in inspect.getmro(type(w)):

                # stop if we've previously checked this class:
                cls_type = checked_classes.get(cls, None)
                if cls_type != None:
                    break
                checked_classes[cls] = ""

                # only care about certain specific classes:
                if cls.__name__ == "BrowserWidget":
                    # tk-framework-widget.BrowserWidget

                    # check the class has some members we know about and that
                    # have been there since the first version of the code:
                    if (
                        hasattr(w, "_worker")
                        and isinstance(w._worker, QtCore.QThread)
                        and hasattr(w, "_app")
                        and isinstance(w._app, application.Application)
                        and hasattr(w, "_spin_icons")
                        and isinstance(w._spin_icons, list)
                    ):
                        # assume that this is derived from an actual tk-framework-widget.BrowserWidget!
                        cls_type = "BrowserWidget"
                elif cls.__name__ == "SaveAsForm":
                    # tk-multi-workfiles.SaveAsForm

                    # check the class has some members we know about and that
                    # have been there since the first version of the code:
                    if (
                        hasattr(w, "_preview_updater")
                        and isinstance(w._preview_updater, QtCore.QThread)
                        and hasattr(w, "_reset_version")
                        and isinstance(w._reset_version, bool)
                    ):
                        # assume that this is derived from an actual tk-multi-workfiles.SaveAsForm!
                        cls_type = "SaveAsForm"

                if cls_type != None:
                    checked_classes[cls] = cls_type
                    break

            if cls_type:
                worker = None
                if cls_type == "BrowserWidget":
                    worker = w._worker
                elif cls_type == "SaveAsForm":
                    worker = w._preview_updater
                else:
                    continue

                # now check to see if the worker already contains the fix:
                if hasattr(worker, "_SGTK_IMPLEMENTS_QTHREAD_CRASH_FIX_"):
                    # this is already fixed so we don't need to do anything more!
                    continue

                # lets make sure the worker is stopped...
                worker.stop()
                # and wait for the thread to finish - this line is the fix!
                worker.wait()
            else:
                # add all child widgets to list to be checked
                widgets.extend(w.children())
                continue

    @staticmethod
    def wrap_widget_class(widget_class):
        """
        Return a new class derived from widget_class that overrides
        the closeEvent method and emits a signal if the event is
        accepted by the widget_class implementation.

        This is the cleanest way I've found to catch when the widget
        has been closed that doesn't mess with either Qt or Python
        memory/gc management!
        """
        derived_class_name = "__" + widget_class.__name__ + "_TkWidgetWrapper__"

        def closeEvent(self, event):
            """
            close event handled for the wrapper class.  This
            calls the widget_class.closeEvent method and then
            if the event was accepted it emits the widget
            closed signal.
            """
            # call base class closeEvent:
            widget_class.closeEvent(self, event)

            if not event.isAccepted():
                return

            # apply fix to make sure all workers in pre v0.1.17 tk-framework-widget
            # BrowserWidgets are stopped correctly!
            TankQDialog._stop_buggy_background_worker_qthreads(self)

            # if accepted then emit signal:
            self._tk_widgetwrapper_widget_closed.emit()

        # create the derived widget class:
        derived_widget_class = type(
            derived_class_name,
            (widget_class,),
            {
                "_tk_widgetwrapper_widget_closed": QtCore.Signal(),
                "closeEvent": closeEvent,
            },
        )
        return derived_widget_class

    # Signal emitted when dialog is closed
    # either via closing the dialog directly
    # or as a result of the child widget
    # being closed.
    dialog_closed = QtCore.Signal(object)

    def __init__(self, title, bundle, widget, parent):
        """
        Constructor
        """
        TankDialogBase.__init__(self, parent)

        # indicates that we are showing the info pane
        self._info_mode = False
        self._bundle = bundle
        self._widget = widget

        self._config_items = []

        # Set the WA_DeleteOnClose attribute to be sure the dialog will be fully destroyed on close
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        ########################################################################################
        # set up the main UI and header
        self.ui = ui_tank_dialog.Ui_TankDialog()
        self.ui.setupUi(self)

        # when rendering the main UI title text, if the app is in dev mode, add
        # a little DEV text.
        if self._bundle.descriptor.get_dict().get("type") == "dev":
            self.ui.label.setText(
                "%s<span style='font-size:9px; color: #30A7E3'>  DEV</span>" % title
            )
        else:
            self.ui.label.setText(title)

        self.setWindowTitle("Flow Production Tracking: %s" % title)
        if os.path.exists(bundle.icon_256):
            self._window_icon = QtGui.QIcon(bundle.icon_256)
            self.setWindowIcon(self._window_icon)

        # set the visibility of the title bar:
        show_tk_title_bar = (
            not hasattr(self._widget, "hide_tk_title_bar")
            or not self._widget.hide_tk_title_bar
        )
        self.ui.top_group.setVisible(show_tk_title_bar)

        if show_tk_title_bar:

            ########################################################################################
            # set up the title bar and configuration panel

            self.ui.tank_logo.setToolTip(
                "This is part of the PTR desktop app %s" % self._bundle.name
            )
            self.ui.label.setToolTip(
                "This is part of the PTR desktop app %s" % self._bundle.name
            )

            # Add our context to the header
            # two lines - top line covers pipeline config and Project
            # second line covers context (entity, step etc)

            pc = self._bundle.context.tank.pipeline_configuration

            if self._bundle.context.entity is None:
                # this is a project only context

                # top line can contain the Pipeline Config
                if pc.get_name() and pc.get_name() not in (
                    constants.PRIMARY_PIPELINE_CONFIG_NAME,
                    constants.UNMANAGED_PIPELINE_CONFIG_NAME,
                ):
                    # we are using a non-default pipeline config
                    first_line = (
                        "<b style='color: #30A7E3'>Config %s</b>" % pc.get_name()
                    )
                else:
                    first_line = "Toolkit %s" % self._bundle.context.tank.version

                # second line contains the project
                if self._bundle.context.project:
                    second_line = "Project %s" % self._bundle.context.project.get(
                        "name", "Undefined"
                    )
                else:
                    second_line = "No Project Set"

            else:
                # this is a standard context with an entity

                # top line will contain the project name
                if self._bundle.context.project:
                    first_line = "Project %s" % self._bundle.context.project.get(
                        "name", "Undefined"
                    )
                else:
                    first_line = "No Project Set"  # can this happen?

                # ...unless we are running a non-Primary PC
                pc = self._bundle.context.tank.pipeline_configuration
                if pc.get_name() and pc.get_name() not in (
                    constants.PRIMARY_PIPELINE_CONFIG_NAME,
                    constants.UNMANAGED_PIPELINE_CONFIG_NAME,
                ):
                    # we are using a non-default pipeline config
                    first_line = (
                        "<b style='color: #30A7E3'>Config %s</b>" % pc.get_name()
                    )

                # second line contains the entity and task, step
                second_line = str(self._bundle.context)

            self.ui.lbl_context.setText("%s<br>%s" % (first_line, second_line))

            ########################################################################################
            # add more detailed context info for the tooltip

            def _format_context_property(p, show_type=False):
                if p is None:
                    formatted = "Undefined"
                elif show_type:
                    formatted = "{} {}".format(p.get("type"), p.get("name"))
                else:
                    formatted = "{}".format(p.get("name"))

                return formatted

            tooltip = ""
            tooltip += "<b>Your Current Context</b>"
            tooltip += "<hr>"
            tooltip += "<b>Project</b>: %s<br>" % _format_context_property(
                self._bundle.context.project
            )
            tooltip += "<b>Entity</b>: %s<br>" % _format_context_property(
                self._bundle.context.entity, True
            )
            tooltip += "<b>Pipeline Step</b>: %s<br>" % _format_context_property(
                self._bundle.context.step
            )
            tooltip += "<b>Task</b>: %s<br>" % _format_context_property(
                self._bundle.context.task
            )
            tooltip += "<b>User</b>: %s<br>" % _format_context_property(
                self._bundle.context.user
            )
            for e in self._bundle.context.additional_entities:
                tooltip += "<b>Additional Item</b>: %s<br>" % _format_context_property(
                    e, True
                )

            tooltip += "<br>"
            tooltip += "<b>System Information</b>"
            tooltip += "<hr>"
            tooltip += (
                "<b>Flow Production Tracking Toolkit Version: </b>%s<br>" % self._bundle.tank.version
            )
            tooltip += "<b>Pipeline Config: </b>%s<br>" % pc.get_name()
            tooltip += "<b>Config Path: </b>%s<br>" % pc.get_path()

            self.ui.lbl_context.setToolTip(tooltip)

            ########################################################################################
            # now setup the info page with all the details

            self.ui.details_show.clicked.connect(self._on_arrow)
            self.ui.details_hide.clicked.connect(self._on_arrow)
            self.ui.app_name.setText(self._bundle.display_name)
            self.ui.app_description.setText(self._bundle.description)
            # get the descriptor type (eg. git/app store/dev etc)
            descriptor_type = self._bundle.descriptor.get_dict().get(
                "type", "Undefined"
            )
            self.ui.app_tech_details.setText(
                "Location: %s %s (Source: %s)"
                % (self._bundle.name, self._bundle.version, descriptor_type)
            )

            context_info = "Your current work area is %s. " % self._bundle.context
            # try get the environment - may not work - not all bundle classes have a .engine method
            try:
                context_info += "You are currently running in the %s environment." % (
                    self._bundle.engine.environment["name"]
                )
            except:
                pass

            self.ui.app_work_area_info.setText(context_info)

            # see if there is an app icon, in that case display it
            self.ui.app_icon.setPixmap(QtGui.QPixmap(self._bundle.icon_256))

            self.ui.btn_documentation.clicked.connect(self._on_doc)
            self.ui.btn_support.clicked.connect(self._on_support)
            self.ui.btn_file_system.clicked.connect(self._on_filesystem)
            self.ui.btn_shotgun.clicked.connect(self._on_shotgun)
            self.ui.btn_reload.clicked.connect(self._on_reload)

            # When there is no file system locations, hide the "Jump to File System" button.
            if not self._bundle.context.filesystem_locations:
                self.ui.btn_file_system.setVisible(False)

            if len(self._bundle.descriptor.configuration_schema) == 0:
                # no configuration for this app!
                self.ui.config_header.setVisible(False)
                self.ui.config_line.setVisible(False)
                self.ui.config_label.setVisible(False)

            else:
                # enumerate configuration items
                for (
                    setting,
                    params,
                ) in self._bundle.descriptor.configuration_schema.items():
                    value = self._bundle.get_setting(setting, None)
                    self._add_settings_item(setting, params, value)

        ########################################################################################
        # parent the widget we are hosting into the dialog area
        self._widget.setParent(self.ui.page_1)
        self.ui.target.insertWidget(0, self._widget)

        # adjust size of the outer window to match the hosted widget size
        dlg_height = self._widget.height()
        if show_tk_title_bar:
            dlg_height += TankQDialog.TOOLBAR_HEIGHT
        self.resize(self._widget.width(), dlg_height)

        ########################################################################################
        # keep track of widget so that when
        # it closes we also close this dialog
        self._orig_widget_closeEvent = None
        if hasattr(self._widget, "_tk_widgetwrapper_widget_closed"):
            # This is a wrapped widget so we can cleanly connect to the closed
            # signal it provides.
            #
            # Doing things this way will result in gc being able to clean up
            # properly when the widget object is no longer referenced!
            self._widget._tk_widgetwrapper_widget_closed.connect(self._on_widget_closed)
        else:
            # This is a non-wrapped widget so lets use the less
            # memory friendly version by bypassing the closeEvent method!
            # Note, as soon as we do this, python thinks there is a circular
            # reference between the widget and the bound method so it won't clean
            # it up straight away...
            #
            # If widget also has a __del__ method then this will stop it
            # being gc'd at all... ever..!
            self._orig_widget_closeEvent = self._widget.closeEvent
            self._widget.closeEvent = self._widget_closeEvent

    def event(self, event):
        """
        To avoid key press events being posted to the host application (e.g. hotkeys
        in Maya), we need to filter them out.

        Events will still be handled by child controls (e.g. text edits) correctly,
        this just stops those events being posted any further up than this widget.
        """
        if (
            event.type() == QtCore.QEvent.KeyPress
            and event.key() != QtCore.Qt.Key_Escape
        ):
            # Don't let the event go any further!
            # self._bundle.log_debug("Suppressing key press '%s' in Toolkit dialog!" % event.key())
            return True
        else:
            # standard event processing
            return TankDialogBase.event(self, event)

    def closeEvent(self, event):
        """
        Override the dialog closeEvent handler so that it first tries
        to close the enclosed widget.

        If the enclosed widget doesn't close then we should ignore the
        event so the dialog doesn't close.

        :param event:   The close event to handle
        """
        if self._widget:
            if not self._widget.close():
                # failed to close the widget which means we
                # shouldn't close the dialog!
                event.ignore()

    def done(self, exit_code):
        """
        Override 'done' method to emit the dialog_closed
        event.  This method is called regardless of how
        the dialog is closed.

        :param exit_code:   The exit code to use if this is
                            being shown as a modal dialog.
        """
        if self._widget:
            # explicitly call close on the widget - this ensures
            # any custom closeEvent code is executed properly
            if self._widget.close():
                # Note that this will indirectly call _do_done()
                # so there is no need to call it explicitly from
                # here!
                pass
            else:
                # widget suppressed the close!
                return
        else:
            # process 'done' so that the exit code
            # gets correctly propogated and the close
            # event is emitted.
            self._do_done(exit_code)

    def _do_done(self, exit_code):
        """
        Internal method used to execute the base class done() method
        and emit the dialog_closed signal.

        This may get called directly from 'done' but may also get called
        when the embedded widget is closed and the dialog is modal.

        :param exit_code:   The exit code to use if this is
                            being shown as a modal dialog.
        """
        # call base done() implementation - this sets
        # the exit code returned from exec()/show_modal():
        TankDialogBase.done(self, exit_code)

        # and emit dialog closed signal:
        self.dialog_closed.emit(self)

    def detach_widget(self):
        """
        Detach the widget from the dialog so that it
        remains alive when the dialog is removed gc'd
        """
        if not self._widget:
            return None

        # stop watching for the widget being closed:
        if hasattr(self._widget, "_tk_widgetwrapper_widget_closed"):
            # disconnect from the widget closed signal
            self._widget._tk_widgetwrapper_widget_closed.disconnect(
                self._on_widget_closed
            )

        elif self._orig_widget_closeEvent:
            # apply fix to make sure all workers in pre v0.1.17 tk-framework-widget
            # BrowserWidgets are stopped correctly!
            # Note, this is the only place this can be done for non-wrapped
            # widgets as once it's detached we have no further access to it!
            TankQDialog._stop_buggy_background_worker_qthreads(self)

            # reset the widget closeEvent function.  Note that
            # python still thinks there is a circular reference
            # (inst->bound method->inst) so this will get gc'd
            # but not straight away!
            self._widget.closeEvent = self._orig_widget_closeEvent
            self._orig_widget_closeEvent = None

        # unparent the widget from the dialog:
        if self._widget.parent() == self.ui.page_1:
            self._widget.setParent(None)

        # clear self._widget and return it
        widget = self._widget
        self._widget = None
        return widget

    def _widget_closeEvent(self, event):
        """
        Called if the contained widget isn't a wrapped widget
        and it's closed by calling widget.close()
        """
        if self._orig_widget_closeEvent:
            # call the original closeEvent
            self._orig_widget_closeEvent(event)

        if not event.isAccepted():
            # widget didn't accept the close
            # so stop!
            return

        # the widget is going to close so
        # lets handle it!
        self._on_widget_closed()

    def _on_widget_closed(self):
        """
        This is called when the contained widget is closed - it
        handles the event and then closes the dialog
        """
        exit_code = QtGui.QDialog.Accepted

        # look if the hosted widget has an exit_code we should pick up
        if self._widget and hasattr(self._widget, "exit_code"):
            exit_code = self._widget.exit_code

        # and call done to close the dialog with the correct exit
        # code and emit the dialog closed signal.
        #
        # Note that we don't call done() directly as it would
        # recursively call close on our widget again!
        self._do_done(exit_code)

    def _on_arrow(self):
        """
        callback when someone clicks the 'details' > arrow icon
        """
        if not hasattr(QtCore, "QAbstractAnimation"):
            # This version of Qt doesn't expose the Q*Animation classes (probably
            # and old version of PyQt) so just move the pages manually:
            self.setUpdatesEnabled(False)
            try:
                if self._info_mode:
                    # hide the info panel:
                    # activate page 1 again - note that this will reset all positions!
                    self.ui.stackedWidget.setCurrentIndex(0)

                    # Flip arrow icon
                    self.ui.details_show.setVisible(True)
                    self.ui.details_hide.setVisible(False)
                else:
                    # show the info panel:
                    # activate page 2 - note that this will reset all positions!
                    self.ui.stackedWidget.setCurrentIndex(1)

                    # Flip arrow icon
                    self.ui.details_show.setVisible(False)
                    self.ui.details_hide.setVisible(True)

                    # this hides page page 1, so let's show it again
                    self.ui.page_1.show()
                    # make sure page1 stays on top
                    self.ui.page_1.raise_()
                    # and move the page 1 window to allow room for page 2, the info panel:
                    self.ui.page_1.move(
                        self.ui.page_1.x()
                        - (TankQDialog.GRADIENT_WIDTH + TankQDialog.INFO_WIDTH),
                        self.ui.page_1.y(),
                    )
            finally:
                self.setUpdatesEnabled(True)

            self._info_mode = not (self._info_mode)
        else:
            # lets animate the transition:
            self.__animate_toggle_info_panel()

    def __animate_toggle_info_panel(self):
        """
        Toggle the visibility of the info panel, animating the transition.
        """
        if self._info_mode:
            # Flip arrow icon
            self.ui.details_show.setVisible(True)
            self.ui.details_hide.setVisible(False)

            self.setUpdatesEnabled(False)
            try:
                # activate page 1 again - note that this will reset all positions!
                self.ui.stackedWidget.setCurrentIndex(0)
                # this hides page page 2, but let's show it again
                self.ui.page_2.show()
                # put this window top most to avoid flickering
                self.ui.page_2.raise_()
                # and move the page 1 window back to its current position
                self.ui.page_1.move(
                    self.ui.page_1.x()
                    - (TankQDialog.GRADIENT_WIDTH + TankQDialog.INFO_WIDTH),
                    self.ui.page_1.y(),
                )
                # now that the first window is positioned correctly, make it top most again.
                self.ui.page_1.raise_()
            finally:
                self.setUpdatesEnabled(True)

            self.anim = QtCore.QPropertyAnimation(self.ui.page_1, b"pos")
            self.anim.setDuration(600)
            self.anim.setStartValue(
                QtCore.QPoint(self.ui.page_1.x(), self.ui.page_1.y())
            )
            self.anim.setEndValue(
                QtCore.QPoint(
                    self.ui.page_1.x()
                    + (TankQDialog.GRADIENT_WIDTH + TankQDialog.INFO_WIDTH),
                    self.ui.page_1.y(),
                )
            )
            self.anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
            self.anim.finished.connect(self._finished_show_anim)

            self.anim2 = QtCore.QPropertyAnimation(self.ui.page_2, b"pos")
            self.anim2.setDuration(600)
            self.anim2.setStartValue(
                QtCore.QPoint(self.ui.page_2.x(), self.ui.page_2.y())
            )
            self.anim2.setEndValue(
                QtCore.QPoint(
                    self.ui.page_2.x()
                    + TankQDialog.GRADIENT_WIDTH
                    + TankQDialog.INFO_WIDTH,
                    self.ui.page_2.y(),
                )
            )
            self.anim2.setEasingCurve(QtCore.QEasingCurve.OutCubic)

            self.grp = QtCore.QParallelAnimationGroup()
            self.grp.addAnimation(self.anim)
            self.grp.addAnimation(self.anim2)
            self.grp.start()

        else:
            # Flip arrow icon
            self.ui.details_show.setVisible(False)
            self.ui.details_hide.setVisible(True)

            # activate page 2 - note that this will reset all positions!
            self.ui.stackedWidget.setCurrentIndex(1)
            # this hides page page 1, but let's show it again
            self.ui.page_1.show()
            # but make sure page1 stays on top
            self.ui.page_1.raise_()

            self.anim = QtCore.QPropertyAnimation(self.ui.page_2, b"pos")
            self.anim.setDuration(600)
            self.anim.setStartValue(
                QtCore.QPoint(
                    self.ui.page_2.x()
                    + (TankQDialog.GRADIENT_WIDTH + TankQDialog.INFO_WIDTH),
                    self.ui.page_2.y(),
                )
            )
            self.anim.setEndValue(QtCore.QPoint(self.ui.page_2.x(), self.ui.page_2.y()))
            self.anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)

            self.anim2 = QtCore.QPropertyAnimation(self.ui.page_1, b"pos")
            self.anim2.setDuration(600)
            self.anim2.setStartValue(
                QtCore.QPoint(self.ui.page_1.x(), self.ui.page_1.y())
            )
            self.anim2.setEndValue(
                QtCore.QPoint(
                    self.ui.page_1.x()
                    - (TankQDialog.GRADIENT_WIDTH + TankQDialog.INFO_WIDTH),
                    self.ui.page_1.y(),
                )
            )
            self.anim2.setEasingCurve(QtCore.QEasingCurve.OutCubic)
            self.anim2.finished.connect(self._finished_show_anim)

            self.grp = QtCore.QParallelAnimationGroup()
            self.grp.addAnimation(self.anim)
            self.grp.addAnimation(self.anim2)
            self.grp.start()

    def _finished_show_anim(self):
        """
        Callback called when the animation is complete
        """
        # now set the new info mode representing
        # the state we have just arrived at
        self._info_mode = not (self._info_mode)

        if not self._info_mode:
            # no longer want to display the side bar
            self.ui.page_2.hide()

    def _on_doc(self):
        """
        Launch doc url
        """
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(self._bundle.documentation_url))

    def _on_support(self):
        """
        Launch support url
        """
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(self._bundle.support_url))

    def _on_filesystem(self):
        """
        Show the context in the file system
        """
        # launch one window for each location on disk
        paths = self._bundle.context.filesystem_locations
        for disk_location in paths:

            url = QtCore.QUrl.fromLocalFile(disk_location)
            status = QtGui.QDesktopServices.openUrl(url)

            if not status:
                self._engine.log_error("Failed to open '%s'!" % disk_location)

    def _on_shotgun(self):
        """
        Show the context in shotgun
        """
        url = self._bundle.context.shotgun_url
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def _on_reload(self):
        """
        Reloads the engine and apps
        """
        try:
            # first, reload the template defs
            self._bundle.tank.reload_templates()
        except TankError as e:
            self._bundle.log_error(e)

        try:

            # now restart the engine
            current_context = self._bundle.context
            current_engine_name = self._bundle.engine.name
            if engine.current_engine():
                engine.current_engine().destroy()
            engine.start_engine(
                current_engine_name, current_context.tank, current_context
            )
        except TankError as e:
            self._bundle.log_error("Could not restart the engine: %s" % e)
        except Exception:
            self._bundle.log_exception("Could not restart the engine!")

    def _on_edit_config(self):
        """
        Future use
        """
        pass

    def _on_add_param(self):
        """
        Future use
        """
        pass

    def _add_settings_item(self, setting, params, value):
        """
        Adds a settings item to the list of settings.
        """
        widget = ConfigItem(setting, params, value, self._bundle, self)
        self.ui.config_layout.addWidget(widget)
        self._config_items.append(widget)
