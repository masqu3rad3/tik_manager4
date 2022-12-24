"""Utility functions for the UI."""

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui, Qt

def toggle_widget(widget, state, functionality=True, visibility=False):
    """Toggle a widget's functionality and/or visibility.

    Args:
        widget (QtWidgets.QWidget): The widget to toggle.
        state (bool): The state to set the widget to.
        functionality (bool): Whether to toggle the widget's functionality.
        visibility (bool): Whether to toggle the widget's visibility.

    """
    if functionality:
        widget.setEnabled(state)
    if visibility:
        widget.setVisible(state)

def create_row(form, label, widget_type, **kwargs):
    """Add a row to a form layout.

    Args:
        form (QtWidgets.QFormLayout): The form layout to add the row to.
        label (str): The label to add to the row.
        widget_type (widget): The widget or layout to add to the row.

    """
    widget = widget_type(**kwargs)
    lbl = QtWidgets.QLabel(label)
    form.addRow(lbl, widget)
    return widget


def add_widget(widget_type, layout, label=None, **kwargs):
    """Add a widget to a layout.

    Args:
        widget_type (any widget): The widget type to add.
        layout (QtWidgets.QLayout): The layout to add the widget to.
                    Supports QtWidgets.QLayout and QtWidgets.QFormLayout
                    subclasses.
        label (str): The label to add to the widget.
        **kwargs: The keyword arguments to pass to the widget.

    Returns:
        QtWidgets.QWidget: The widget that was added.

    """
    widget = widget_type(**kwargs)
    if isinstance(layout, Qt.QtWidgets.QFormLayout):
        lbl = QtWidgets.QLabel(label or "")
        layout.addRow(lbl, widget)
    else:
        layout.addWidget(widget)
    return widget
