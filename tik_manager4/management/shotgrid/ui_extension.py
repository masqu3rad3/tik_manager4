
from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.management.ui.dialog import CreateFromManagementDialog
from tik_manager4.ui.widgets.pop import WaitDialog

from tik_manager4.management.extension_core import ExtensionCore

class UiExtensions(ExtensionCore):
    def __init__(self, parent):
        self.parent = parent
        self.feedback = Feedback(parent=self.parent)

    def build_ui(self):
        """Build the extension UI."""
        self.add_main_menu()

    def add_main_menu(self):
        """Add the extension commands to the main menu."""
        sg_menu = self.parent.menu_bar.addMenu("Shotgrid")

        create_project_from_shotgrid = QtWidgets.QAction("&Create Project from Shotgrid", self.parent)
        sg_menu.addAction(create_project_from_shotgrid)

        force_sync = QtWidgets.QAction("&Force Sync", self.parent)
        sg_menu.addAction(force_sync)

        sg_menu.addSeparator()
        logout_action = QtWidgets.QAction("&Logout", self.parent)
        sg_menu.addAction(logout_action)

        # SIGNALS
        create_project_from_shotgrid.triggered.connect(
            self.on_create_project_from_shotgrid
        )
        force_sync.triggered.connect(self.on_force_sync)
        # for some reason, lambda is needed...
        logout_action.triggered.connect(lambda: self.on_logout())

    def on_force_sync(self):
        """Force synchronize the project."""
        is_management_driven = self.parent.tik.project.settings.get("management_driven", False)
        if not is_management_driven:
            self.feedback.pop_info(title="Warning", text="The project is not management driven.\n\nOnly projects created through Shotgrid can be synced.\nUse 'Create Project from Shotgrid' menu item to create a project.\n\nNo action will be taken.")
            return
        management_platform = self.parent.tik.project.settings.get("management_platform")
        if management_platform != "shotgrid":
            self.feedback.pop_info(
                title="Warning",
                text="The project is not managed by Shotgrid.\n\nOnly projects managed by Shotgrid can be synced.\nUse 'Create Project from Shotgrid' menu item to create a project.\n\nNo action will be taken.",
                critical=True,
            )
            return
        ret = self.feedback.pop_question(title="Force Sync", text="This action will forcefully sync the project to the shotgrid project.\n\nThis action can take a long time depending on the number of assets and shots in the project.\n\nDo you want to continue?", buttons=["yes", "cancel"])
        if ret == "yes":
            wait_pop = WaitDialog("Force Synchronization In Progress. Please wait...", parent=self.parent)
            handler = self.parent.management_connect("shotgrid")
            wait_pop.display()
            result, msg = handler.force_sync()
            wait_pop.kill()
            if not result:
                self.feedback.pop_info(title="Error", text=msg, critical=True)

    def on_logout(self):
        """Logout from Shotgrid."""
        method = self.parent.tik.user.commons.management_settings.get("sg_authentication_method")
        if method != "User":
            self.feedback.pop_info(title="Warning", text="The Shotgrid authentication method is not set to User.\nNo action will be taken.\n\nThe Authenticaion method can be changed from settings -> Common -> Platform Settings.")
            return
        handler = self.parent.management_connect("shotgrid")
        handler.logout()
        self.feedback.pop_info(title="Logged out", text="Logged out of Shotgrid.\nPlease restart the application to see changes.")

    def on_create_project_from_shotgrid(self):
        """Create a project from shotgrid."""
        if not self.parent._pre_check(level=3):
            return

        handler = self.parent.management_connect("shotgrid")
        if not handler:
            return

        dialog = CreateFromManagementDialog(handler, parent=self.parent)
        state = dialog.exec()
        if state:
            # hard refresh the project
            # self.parent.subprojects_mcv.manual_refresh()
            self.parent.refresh_project()
            self.parent.status_bar.showMessage("Project created successfully")
        return

