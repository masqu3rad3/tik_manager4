# pylint: disable=import-error
"""Dialog for settings."""

import sys  # This is required for the 'frozen' attribute DO NOT REMOVE
from pathlib import Path
import logging

from tik_manager4.ui.Qt import QtWidgets, QtCore
from tik_manager4.ui.widgets.validated_string import ValidatedString
from tik_manager4.ui.widgets.settings_widgets import (
    UsersDefinitions,
    MetadataDefinitions,
    CategoryDefinitions
)
from tik_manager4.ui.widgets.switch_tree import SwitchTreeWidget, SwitchTreeItem
from tik_manager4.ui.widgets.common import (
    HeaderLabel,
    ResolvedText,
    TikButtonBox,
    TikButton,
    HorizontalSeparator,
)
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui.layouts.settings_layout import (
    SettingsLayout,
    convert_to_ui_definition,
    convert_to_settings_data,
)
from tik_manager4.ui.dialog.data_containers import MainLayout
from tik_manager4 import management

LOG = logging.getLogger(__name__)


class SettingsDialog(QtWidgets.QDialog):
    """Settings dialog."""

    def __init__(self, main_object, *args, **kwargs):
        """Initiate the class."""
        super().__init__(*args, **kwargs)

        # DYNAMIC VARIABLES
        self._setting_widgets = []
        self.settings_list = []  # list of settings objects
        self.feedback = Feedback(parent=self)
        self.main_object = main_object
        self.layouts = MainLayout()
        self.setWindowTitle("Settings")
        self.menu_tree_widget: QtWidgets.QTreeWidget
        self.apply_button: QtWidgets.QPushButton
        self._validations_and_extracts = (
            None  # for caching the validations and extracts
        )
        self.error_count: int = 0
        # Execution
        self.build_ui()
        # expand everything
        self.menu_tree_widget.expandAll()

    def build_ui(self):
        """Build the UI."""
        self.build_layouts()
        self.build_static_widgets()
        self.create_content()
        # set the first item on menu tree as current
        self.menu_tree_widget.setCurrentItem(self.menu_tree_widget.topLevelItem(0))
        self.resize(960, 630)
        self.layouts.splitter.setSizes([250, 750])

    def build_layouts(self):
        """Build layouts."""
        self.layouts.master_layout = QtWidgets.QVBoxLayout(self)
        self.layouts.splitter = QtWidgets.QSplitter(self)

        left_widget = QtWidgets.QWidget(self.layouts.splitter)
        self.layouts.left_layout = QtWidgets.QVBoxLayout(left_widget)
        self.layouts.left_layout.setContentsMargins(0, 0, 0, 0)

        right_widget = QtWidgets.QWidget(self.layouts.splitter)
        self.layouts.right_layout = QtWidgets.QVBoxLayout(right_widget)
        self.layouts.right_layout.setContentsMargins(0, 0, 0, 0)
        self.layouts.master_layout.addWidget(self.layouts.splitter)
        self.layouts.buttons_layout = QtWidgets.QHBoxLayout()
        self.layouts.master_layout.addLayout(self.layouts.buttons_layout)

    def build_static_widgets(self):
        """Build static widgets."""

        self.menu_tree_widget = SwitchTreeWidget(user=self.main_object.user)
        self.menu_tree_widget.setRootIsDecorated(True)
        self.menu_tree_widget.setHeaderHidden(True)
        self.menu_tree_widget.header().setVisible(False)
        self.layouts.left_layout.addWidget(self.menu_tree_widget)

        tik_button_box = TikButtonBox(parent=self)
        self.layouts.buttons_layout.addWidget(tik_button_box)
        self.apply_button = tik_button_box.addButton(
            "Apply", QtWidgets.QDialogButtonBox.ApplyRole
        )
        self.apply_button.setEnabled(False)
        cancel_button = tik_button_box.addButton(
            "Cancel", QtWidgets.QDialogButtonBox.RejectRole
        )
        ok_button = tik_button_box.addButton(
            "Ok", QtWidgets.QDialogButtonBox.AcceptRole
        )
        # SIGNALS
        self.apply_button.clicked.connect(self.apply_settings)
        cancel_button.clicked.connect(self.close)
        ok_button.clicked.connect(lambda: self.apply_settings(close_dialog=True))

        self.layouts.buttons_layout.addWidget(tik_button_box)

    def create_content(self):
        """Create the content."""
        self.menu_tree_widget.clear()
        self.user_title()
        self.project_title()
        self.common_title()
        self.create_content_links()

    def user_title(self):
        """Create the user settings."""
        # create the menu items
        user_widget_item = SwitchTreeItem(["User"], permission_level=0)
        self.menu_tree_widget.addTopLevelItem(user_widget_item)

        # create sub-branches
        user_settings_item = SwitchTreeItem(["User Settings"], permission_level=0)
        user_widget_item.addChild(user_settings_item)
        ui_definition = {
            "commonFolder": {
                "display_name": "Common Folder",
                "tooltip": "The folder where the common data for all projects is stored.",
                "type": "pathBrowser",
                "value": self.main_object.user.settings.get_property("commonFolder"),
            },
            "user_templates_directory": {
                "display_name": "User Templates Directory",
                "tooltip": "The folder where all user template files stored for all Dccs. Supports flags.",
                "type": "pathBrowser",
                "value": self.main_object.user.settings.get_property(
                    "user_templates_directory"
                ),
            },
            "alembic_viewer": {
                "display_name": "Alembic Viewer",
                "tooltip": "The path to the Alembic Viewer executable. Supports flags.",
                "type": "fileBrowser",
                "value": self.main_object.user.settings.get_property("alembic_viewer"),
            },
            "usd_viewer": {
                "display_name": "USD Viewer",
                "tooltip": "The path to the USD Viewer executable. Supports flags.",
                "type": "fileBrowser",
                "value": self.main_object.user.settings.get_property("usd_viewer"),
            },
            "fbx_viewer": {
                "display_name": "FBX Viewer",
                "tooltip": "The path to the FBX Viewer executable. Supports flags.",
                "type": "fileBrowser",
                "value": self.main_object.user.settings.get_property("fbx_viewer"),
            },
            "image_viewer": {
                "display_name": "Image Viewer",
                "tooltip": "The path to the Image Viewer executable. Supports flags.",
                "type": "fileBrowser",
                "value": self.main_object.user.settings.get_property("image_viewer"),
            },
            "sequence_viewer": {
                "display_name": "Sequence Viewer",
                "tooltip": "The path to the Sequence Viewer executable. Supports flags.",
                "type": "fileBrowser",
                "value": self.main_object.user.settings.get_property("sequence_viewer"),
            },
            "video_player": {
                "display_name": "Video Viewer",
                "tooltip": "The path to the Video Player executable. Supports flags.",
                "type": "fileBrowser",
                "value": self.main_object.user.settings.get_property("video_player"),
            },
        }

        user_settings_item.content = self.__create_generic_settings_layout(
            settings_data=self.main_object.user.settings,
            title="User Settings",
            ui_definition=ui_definition,
        )

        user_password_item = SwitchTreeItem(["Change Password"], permission_level=0)
        user_widget_item.addChild(user_password_item)
        user_password_item.content = self.__create_user_password_layout()

        # Localization settings
        user_localization_item = SwitchTreeItem(["Localization"], permission_level=0)
        user_widget_item.addChild(user_localization_item)

        localization_ui_definition = {
            "enabled": {
                "display_name": "Enabled",
                "type": "boolean",
                "value": self.main_object.user.localization.get_property("enabled", False),
                "disables": [],
            },
            "local_cache_folder": {
                "display_name": "Local Cache Folder",
                "tooltip": "Local folder to store cache files.",
                "type": "pathBrowser",
                "value": self.main_object.user.localization.get_property("local_cache_folder"),
            },
            "cache_works": {
                "display_name": "Cache Work Files",
                "type": "boolean",
                "tooltip": "If enabled, work files will be stored in the cache folder and won't be accessible for other users until its synced.",
                "value": self.main_object.user.localization.get_property("cache_works", True),
            },
            "cache_publishes": {
                "display_name": "Cache Publish Files",
                "type": "boolean",
                "tooltip": "If enabled, publish files will be stored in the cache folder and won't be accessible for other users until its synced.",
                "value": self.main_object.user.localization.get_property("cache_publishes", False),
            }
        }

        # fill the content
        user_localization_item.content = self.__create_generic_settings_layout(
            settings_data=self.main_object.user.localization,
            title="Localization",
            ui_definition=localization_ui_definition,
        )

    def __create_user_password_layout(self):
        """Create the widget for changing the user password."""
        content_widget = QtWidgets.QWidget()
        self.layouts.right_layout.addWidget(content_widget)

        settings_v_lay = QtWidgets.QVBoxLayout(content_widget)
        header_layout = QtWidgets.QVBoxLayout()
        settings_v_lay.addLayout(header_layout)

        # add the title
        title_label = HeaderLabel("Change User Password")
        header_layout.addWidget(title_label)

        # add a label to show the path of the settings file
        path_label = ResolvedText(
            f"Change user password of {self.main_object.user.name}"
        )
        header_layout.addWidget(path_label)
        header_layout.addWidget(HorizontalSeparator(color=(255, 141, 28), height=1))

        # form layout
        form_layout = QtWidgets.QFormLayout()
        settings_v_lay.addLayout(form_layout)

        old_password_lbl = QtWidgets.QLabel("Old Password :")
        old_password_le = ValidatedString(
            name="old_password", allow_special_characters=True
        )
        old_password_le.setEchoMode(QtWidgets.QLineEdit.Password)
        form_layout.addRow(old_password_lbl, old_password_le)

        new_password_lbl = QtWidgets.QLabel("New Password :")
        new_password_le = ValidatedString(
            name="new_password", allow_special_characters=True
        )
        new_password_le.setEchoMode(QtWidgets.QLineEdit.Password)
        form_layout.addRow(new_password_lbl, new_password_le)

        new_password2_lbl = QtWidgets.QLabel("New Password Again :")
        new_password2_le = ValidatedString(
            name="new_password2", allow_special_characters=True
        )
        new_password2_le.setEchoMode(QtWidgets.QLineEdit.Password)
        form_layout.addRow(new_password2_lbl, new_password2_le)

        # add a button to change the password
        change_password_button = TikButton(text="Change Password", parent=self)
        settings_v_lay.addWidget(change_password_button)

        settings_v_lay.addStretch()

        def on_change_password():
            """Convenience function to change the password."""
            if new_password_le.text() != new_password2_le.text():
                self.feedback.pop_info(
                    title="Cannot change password",
                    text="New passwords do not match.",
                    critical=True,
                )
                return
            result, msg = self.main_object.user.change_user_password(
                old_password=old_password_le.text(),
                new_password=new_password_le.text(),
            )
            if result == -1:
                self.feedback.pop_info(
                    title="Cannot change password", text=msg, critical=True
                )
            else:
                self.feedback.pop_info(title="Password Changed", text=msg)
                old_password_le.clear()
                new_password_le.clear()
                new_password2_le.clear()
            self.error_count += 1

            if self.error_count == 2:
                self.feedback.pop_info(
                    title="Too many errors",
                    text=f"Friendly reminder: You are trying to change the password for:\n\n {self.main_object.user.name}.",
                )

            if self.error_count == 5:
                self.feedback.pop_info(
                    title="Too many errors",
                    text="This starting to look suspicious. I am watching you!",
                )

            if self.error_count == 12:
                self.feedback.pop_info(
                    title="Too many errors",
                    text="This is your last warning.",
                )

            if self.error_count > 12:
                self.feedback.pop_info(
                    title="Too many errors",
                    text="Thats it. Something fishy going on here. I am closing the window!",
                )
                self.close()

        # SIGNALS
        change_password_button.clicked.connect(on_change_password)

        content_widget.setVisible(False)
        return content_widget

    def project_title(self):
        """Create the project settings."""
        # create the menu items
        project_widget_item = SwitchTreeItem(["Project"], permission_level=3)
        self.menu_tree_widget.addTopLevelItem(project_widget_item)

        # create sub-branches
        preview_settings_item = SwitchTreeItem(["Preview Settings"], permission_level=3)
        project_widget_item.addChild(preview_settings_item)
        preview_settings_item.content = self.__create_generic_settings_layout(
            settings_data=self.main_object.project.preview_settings,
            title="Preview Settings",
        )
        category_definitions = SwitchTreeItem(
            ["Category Definitions"], permission_level=3
        )
        project_widget_item.addChild(category_definitions)
        category_definitions.content = self._project_category_definitions_content()

        metadata = SwitchTreeItem(["Metadata"], permission_level=3)
        project_widget_item.addChild(metadata)
        metadata.content = self._metadata_content()

    def common_title(self):
        """Create the common settings."""
        # create the menu items
        common_widget_item = SwitchTreeItem(["Common"], permission_level=3)
        self.menu_tree_widget.addTopLevelItem(common_widget_item)

        # create sub-branches
        category_definitions = SwitchTreeItem(
            ["Category Definitions (Common)"], permission_level=3
        )
        common_widget_item.addChild(category_definitions)
        category_definitions.content = self._common_category_definitions_content()

        metadata = SwitchTreeItem(["Metadata (Common)"], permission_level=3)
        common_widget_item.addChild(metadata)
        metadata.content = self._common_metadata_content()

        users_management = SwitchTreeItem(["Users Management"], permission_level=3)
        common_widget_item.addChild(users_management)
        users_management.content = self.__common_users_management_content()

        # combine the ui definitions for all management platforms
        ui_definition = {}
        for plt in management.platforms.keys():
            settings_ui = management.platforms[plt].get_settings_ui()
            # update the management settings for any missing keys
            settings_data = convert_to_settings_data(settings_ui)
            self.main_object.user.commons.management_settings.add_missing_keys(settings_data)
            ui_definition.update(settings_ui)

        # ui_definition = management.platforms["shotgrid"].get_settings_ui()
        platform_settings = SwitchTreeItem(["Platform Settings"], permission_level=3)
        common_widget_item.addChild(platform_settings)
        platform_settings.content = self.__create_generic_settings_layout(
            settings_data=self.main_object.user.commons.management_settings,
            title="Platform Settings",
            ui_definition=ui_definition,
        )

    def create_content_links(self):
        """Create content widgets for all top level items."""
        # collect all root items
        root_items = [
            self.menu_tree_widget.topLevelItem(x)
            for x in range(self.menu_tree_widget.topLevelItemCount())
        ]
        for root_item in root_items:
            # create a content widget
            if not root_item.content:
                content_widget = QtWidgets.QWidget()
                content_widget.setVisible(False)
                content_layout = QtWidgets.QVBoxLayout(content_widget)
            else:
                content_widget = root_item.content
                content_layout = content_widget.layout()

            # get all children of the root item
            children = [root_item.child(x) for x in range(root_item.childCount())]
            for child in children:
                # create a QCommandLinkButton for each child
                button = QtWidgets.QCommandLinkButton(child.text(0))
                button.clicked.connect(
                    lambda _=None, x=child: self.menu_tree_widget.setCurrentItem(x)
                )
                content_layout.addWidget(button)

            content_layout.addStretch()
            self.layouts.right_layout.addWidget(content_widget)
            # add it to the item
            root_item.content = content_widget

    def apply_settings(self, close_dialog=False):
        """Apply the settings."""
        for settings_object in self.settings_list:
            settings_object.apply_settings()
            self.check_changes()
        if close_dialog:
            self.close()

    def check_changes(self):
        """Check if there are changes in the settings and enable the apply button."""

        for settings_object in self.settings_list:
            if settings_object.is_settings_changed():
                self.apply_button.setEnabled(True)
                return
        self.apply_button.setEnabled(False)

    def _gather_validations_and_extracts(self):
        """Collect the available validations and extracts."""
        if self._validations_and_extracts:
            return self._validations_and_extracts
        # we cannot simply rely on the collected validators and extractors due to it will
        # differ from Dcc to Dcc. So we need to collect them from the directories.
        # This method is not the best way to do it but it is the most reliable way.
        self._validations_and_extracts = {
            "dcc_extracts": {},
            "dcc_validations": {},
            "all_validations": [],
            "all_extracts": [],
        }
        validations = []
        extracts = []

        is_frozen = getattr(sys, "frozen", False)
        # get the location of the file
        if not is_frozen:
            # get the location of the file. tik_manager/ui/dialog/settings_dialog.py
            _file_path = Path(__file__)
            tik_manager4_path = _file_path.parents[2]
        else:
            # First get the location of the executable
            # which is in by default tik_manager4/dist/tik4/<name>.exe
            _exe_path = Path(sys.executable)
            # Pick walk up to the tik_manager4 folder. This will be different if the executable is somewhere else.
            tik_manager4_path = _exe_path.parents[2]

        # DCC folder
        _dcc_folder = tik_manager4_path / "dcc"
        # collect all 'extract' and 'validate' folders under _dcc_folder recursively
        extract_folders = list(_dcc_folder.glob("**/extract"))
        validate_folders = list(_dcc_folder.glob("**/validate"))
        # get the extracts and validates in the <common>/plugins folder
        extract_folders.extend(list((Path(self.main_object.user.commons.folder_path) / "plugins").glob("**/extract")))
        validate_folders.extend(list((Path(self.main_object.user.commons.folder_path) / "plugins").glob("**/validation")))

        # collect all extractors
        for _extract_folder in extract_folders:
            # get the dcc name from the folder name which is the parent of the extract folder
            dcc_name = _extract_folder.parent.stem
            dcc_extracts = [
                    x.stem
                    for x in _extract_folder.glob("*.py")
                    if not x.stem.startswith("_")
                ]
            # update or create the dcc name in the dictionary

            # get the extracts in the common folder
            self._validations_and_extracts["dcc_extracts"][dcc_name] = dcc_extracts
            extracts.extend(dcc_extracts)

        for _validate_folder in validate_folders:
            dcc_name = _validate_folder.parent.stem
            dcc_validations = [
                    x.stem
                    for x in _validate_folder.glob("*.py")
                    if not x.stem.startswith("_")
                ]
            self._validations_and_extracts["dcc_validations"][dcc_name] = dcc_validations
            validations.extend(dcc_validations)

        self._validations_and_extracts["all_validations"] = list(set(validations))
        self._validations_and_extracts["all_extracts"] = list(set(extracts))

        return self._validations_and_extracts

    def __create_generic_settings_layout(
        self, settings_data, title="", ui_definition=None
    ):
        """Create a generic settings layout."""
        content_widget = QtWidgets.QWidget()
        self.layouts.right_layout.addWidget(content_widget)

        settings_v_lay = QtWidgets.QVBoxLayout(content_widget)

        header_layout = QtWidgets.QVBoxLayout()
        settings_v_lay.addLayout(header_layout)

        # add the title
        title_label = HeaderLabel(title)
        header_layout.addWidget(title_label)

        # add a label to show the path of the settings file
        path_label = ResolvedText(settings_data.settings_file)
        header_layout.addWidget(path_label)
        header_layout.addWidget(HorizontalSeparator(color=(255, 141, 28), height=1))

        # make a scroll area for the main content
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area_contents_widget = QtWidgets.QWidget()
        scroll_area_contents_widget.setGeometry(QtCore.QRect(0, 0, 104, 345))
        scroll_area.setWidget(scroll_area_contents_widget)
        settings_v_lay.addWidget(scroll_area)
        scroll_layout = QtWidgets.QVBoxLayout(scroll_area_contents_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        # Actual content creation begins here..
        self.settings_list.append(settings_data)
        ui_definition = ui_definition or convert_to_ui_definition(
            settings_data.properties
        )
        settings_layout = SettingsLayout(ui_definition, settings_data, parent=self)
        scroll_layout.addLayout(settings_layout)

        # SIGNALS
        settings_layout.modified.connect(self.check_changes)

        content_widget.setVisible(False)
        return content_widget

    def _project_category_definitions_content(self):
        """Create the project category definitions."""

        settings_data = self.main_object.project.guard.category_definitions
        availability_dict = self._gather_validations_and_extracts()
        self.settings_list.append(settings_data)

        project_category_definitions_widget = CategoryDefinitions(
            settings_data,
            availability_dict,
            title="Category Definitions (Project)",
            parent=self,
        )

        # hide by default
        project_category_definitions_widget.setVisible(False)
        self.layouts.right_layout.addWidget(project_category_definitions_widget)

        # SIGNALS
        project_category_definitions_widget.modified.connect(self.check_changes)
        return project_category_definitions_widget

    def _metadata_content(self):
        """Create the metadata content."""
        settings_data = self.main_object.project.metadata_definitions
        # add it to the global settings list so it can be checked globally.
        self.settings_list.append(settings_data)

        metadata_widget = MetadataDefinitions(
            settings_data, title="Metadata Definitions", parent=self
        )
        metadata_widget.setVisible(False)
        self.layouts.right_layout.addWidget(metadata_widget)

        # SIGNALS
        metadata_widget.modified.connect(self.check_changes)
        return metadata_widget

    def _common_metadata_content(self):
        """Create the common metadata content."""
        settings_data = self.main_object.user.commons.metadata
        # add it to the global settings list so it can be checked globally.
        self.settings_list.append(settings_data)

        common_metadata_widget = MetadataDefinitions(
            settings_data, title="Metadata Definitions (Common)", parent=self
        )
        common_metadata_widget.setVisible(False)
        self.layouts.right_layout.addWidget(common_metadata_widget)

        # SIGNALS
        common_metadata_widget.modified.connect(self.check_changes)
        return common_metadata_widget

    def _common_category_definitions_content(self):
        """Create the common category definitions."""
        settings_data = self.main_object.user.commons.category_definitions
        availability_dict = self._gather_validations_and_extracts()
        self.settings_list.append(settings_data)

        common_category_definitions_widget = CategoryDefinitions(
            settings_data,
            availability_dict,
            title="Category Definitions (Common)",
            parent=self,
        )
        common_category_definitions_widget.setVisible(False)
        self.layouts.right_layout.addWidget(common_category_definitions_widget)

        # SIGNALS
        common_category_definitions_widget.modified.connect(self.check_changes)
        return common_category_definitions_widget

    def __common_users_management_content(self):
        """Create the user management content."""
        settings_data = self.main_object.user.commons.users
        # add the settings data so it can be checked for alterations within the entire dialog
        self.settings_list.append(settings_data)

        user_management_widget = UsersDefinitions(
            self.main_object.user, title="Users Management", parent=self
        )
        user_management_widget.setVisible(False)  # hide by default
        self.layouts.right_layout.addWidget(user_management_widget)

        # SIGNALS
        user_management_widget.modified.connect(self.check_changes)
        return user_management_widget


# test the dialog
if __name__ == "__main__":
    import sys
    import tik_manager4
    from tik_manager4.ui import pick

    app = QtWidgets.QApplication(sys.argv)
    tik = tik_manager4.initialize("Standalone")
    _style_file = pick.style_file()
    dialog = SettingsDialog(tik, styleSheet=str(_style_file.readAll(), "utf-8"))
    dialog.show()
    sys.exit(app.exec_())
