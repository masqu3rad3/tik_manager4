"""Dialog for checking for updates and providing links to download the latest version of the software."""

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui.dialog.data_containers import MainLayout

class UpdateDialog(QtWidgets.QDialog):
    """Dialog for checking for updates and providing links to download the latest version of the software."""

    def __init__(self, release_object, parent=None):
        super(UpdateDialog, self).__init__(parent)

        self.release_object = release_object

        self.setWindowTitle("Tik Manager4 Update")

        self.layouts = MainLayout()
        self.layouts.master_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layouts.master_layout)

        self.build_ui()
        self.build_buttons()

    def build_header(self):
        """Build the header."""
        self.layouts.header_layout = QtWidgets.QVBoxLayout()
        self.layouts.master_layout.addLayout(self.layouts.header_layout)

        header_label = QtWidgets.QLabel("New Release Available") if self.release_object.is_newer else QtWidgets.QLabel("Tik Manager is up to date")
        header_label.setAlignment(QtCore.Qt.AlignCenter)
        header_label.setFont(QtGui.QFont("Arial", 20))
        self.layouts.header_layout.addWidget(header_label)

    @staticmethod
    def format_link(url):
        """Format the link."""
        formatted_url =f"""
        <head>
          <style>
            a {{ color: cyan; text-decoration: none;}} /* CSS link color */
          </style>
        </head>
        <body>
          <a href="{url}">{url}</a>
        </body>
        """
        return formatted_url

    def build_ui(self):
        """Build the UI elements."""
        self.layouts.header_layout = QtWidgets.QVBoxLayout()
        self.layouts.master_layout.addLayout(self.layouts.header_layout)

        self.layouts.body_layout = QtWidgets.QVBoxLayout()
        self.layouts.master_layout.addLayout(self.layouts.body_layout)



        if self.release_object.is_newer:
            header_label = QtWidgets.QLabel(f"Release {self.release_object.name} Available")
            header_label.setAlignment(QtCore.Qt.AlignCenter)
            header_label.setFont(QtGui.QFont("Arial", 16))
            self.layouts.header_layout.addWidget(header_label)

            release_notest_te = QtWidgets.QTextBrowser()
            release_notest_te.setOpenExternalLinks(True) # open links in browser
            release_notest_te.setReadOnly(True)
            release_notest_te.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            release_notest_te.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
            release_notest_te.setMarkdown(self.release_object.release_notes)

            self.layouts.body_layout.addWidget(release_notest_te)

            link_dict = self.release_object.collect_links()
            form_layout = QtWidgets.QFormLayout()
            form_layout.setLabelAlignment(QtCore.Qt.AlignRight)
            self.layouts.body_layout.addLayout(form_layout)
            for lbl, url in link_dict.items():
                link_label = QtWidgets.QLabel(f"{lbl}:")
                link_url = QtWidgets.QLabel()
                link_url.setOpenExternalLinks(True)
                link_url.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
                link_url.setWordWrap(True)
                link_url.setTextFormat(QtCore.Qt.RichText)
                link_url.setText(self.format_link(url))
                form_layout.addRow(link_label, link_url)

            self.setMinimumWidth(600)
            self.setMinimumHeight(200)
        else:
            header_label = QtWidgets.QLabel("Tik Manager is up to date")
            header_label.setAlignment(QtCore.Qt.AlignCenter)
            header_label.setFont(QtGui.QFont("Arial", 16))
            self.layouts.header_layout.addWidget(header_label)

            info_label = QtWidgets.QLabel("You are using the latest version of Tik Manager. "
                                          "Previous versions can be found on the releases page.")
            self.layouts.body_layout.addWidget(info_label)
            releases_url = "https://github.com/masqu3rad3/tik_manager4/releases"
            releases_url_lbl = QtWidgets.QLabel()
            releases_url_lbl.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
            releases_url_lbl.setOpenExternalLinks(True)
            releases_url_lbl.setTextFormat(QtCore.Qt.RichText)
            releases_url_lbl.setText(self.format_link(releases_url))
            self.layouts.body_layout.addWidget(releases_url_lbl)

    def build_buttons(self):
        """Build the buttons."""
        self.layouts.buttons_layout = QtWidgets.QHBoxLayout()
        self.layouts.master_layout.addLayout(self.layouts.buttons_layout)

        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        self.layouts.buttons_layout.addWidget(self.close_button)


