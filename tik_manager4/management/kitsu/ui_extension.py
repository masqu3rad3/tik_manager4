"""UI Extension for Kitsu"""


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
        kitsu_menu = self.parent.menu_bar.addMenu("Kitsu")

        login_action = QtWidgets.QAction("&Login", self.parent)
        kitsu_menu.addAction(login_action)

        create_project_from_kitsu = QtWidgets.QAction("&Create Project from Kitsu", self.parent)
        kitsu_menu.addAction(create_project_from_kitsu)

        force_sync = QtWidgets.QAction("&Force Sync", self.parent)
        kitsu_menu.addAction(force_sync)

        kitsu_menu.addSeparator()
        logout_action = QtWidgets.QAction("&Logout", self.parent)
        kitsu_menu.addAction(logout_action)

        # SIGNALS
        login_action.triggered.connect(self.on_login)
        create_project_from_kitsu.triggered.connect(
            self.on_create_project_from_kitsu
        )
        force_sync.triggered.connect(self.on_force_sync)
        # for some reason, lambda is needed...
        logout_action.triggered.connect(lambda: self.on_logout())

    def on_login(self):
        """Login to Kitsu."""
        handler = self.parent.management_connect("kitsu")
        handler.authenticate()
        self.feedback.pop_info(title="Logged in", text="Logged in to Kitsu.")

    def on_force_sync(self):
        """Force synchronize the project."""
        is_management_driven = self.parent.tik.project.settings.get("management_driven", False)
        if not is_management_driven:
            self.feedback.pop_info(title="Warning", text="The project is not management driven.\n\nOnly projects created through Kitsu can be synced.\nUse 'Create Project from Kitsu' menu item to create a project.\n\nNo action will be taken.")
            return
        ret = self.feedback.pop_question(title="Force Sync", text="This action will forcefully sync the project to the Kitsu project.\n\nThis action can take a long time depending on the number of assets and shots in the project.\n\nDo you want to continue?", buttons=["yes", "cancel"])
        if ret == "yes":
            wait_pop = WaitDialog("Force Synchronization In Progress. Please wait...", parent=self.parent)
            handler = self.parent.management_connect("kitsu")
            wait_pop.display()
            handler.force_sync()
            wait_pop.kill()

    def on_logout(self):
        """Logout from Kitsu."""
        handler = self.parent.management_connect("kitsu")
        handler.logout()
        self.feedback.pop_info(title="Logged out", text="Logged out of Kitsu.\nPlease restart the application to see changes.")

    def on_create_project_from_kitsu(self):
        """Create a project from shotgrid."""
        if not self.parent._pre_check(level=3):
            return

        handler = self.parent.management_connect("kitsu")
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

