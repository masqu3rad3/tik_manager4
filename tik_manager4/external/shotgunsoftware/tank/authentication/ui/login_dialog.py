# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from .qt_abstraction import QtCore
for name, cls in QtCore.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls

from .qt_abstraction import QtGui
for name, cls in QtGui.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls


from .recent_box import RecentBox
from .aspect_preserving_label import AspectPreservingLabel

from  . import resources_rc

class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        if not LoginDialog.objectName():
            LoginDialog.setObjectName(u"LoginDialog")
        LoginDialog.setWindowModality(Qt.NonModal)
        LoginDialog.resize(424, 304)
        LoginDialog.setMinimumSize(QSize(424, 304))
        LoginDialog.setStyleSheet(u"\n"
"QWidget\n"
"{\n"
"    background-color: rgb(36, 39, 42);\n"
"    color: rgb(192, 192, 192);\n"
"    selection-background-color: rgb(168, 123, 43);\n"
"    selection-color: rgb(230, 230, 230);\n"
"    font-size: 11px;\n"
"}\n"
"\n"
"QPushButton\n"
"{\n"
"    background-color: transparent;\n"
"    border: 1px solid transparent;\n"
"    border-radius: 2px;\n"
"    padding: 8px;\n"
"    padding-left: 15px;\n"
"    padding-right: 15px;\n"
"}\n"
"\n"
"QPushButton::menu-indicator {\n"
"    subcontrol-position: right center;\n"
"}\n"
"\n"
"QPushButton QMenu::item {\n"
"    padding: 15px;\n"
"    border: 1px solid transparent;\n"
"}\n"
"\n"
"QPushButton QMenu::item:disabled {\n"
"    color: rgb(160, 160, 160);\n"
"    font-style: italic;\n"
"}\n"
"\n"
"QPushButton QMenu::item:selected {\n"
"    border-color: rgb(54, 60, 66);\n"
"}\n"
"\n"
"QPushButton QMenu::item:pressed\n"
"{\n"
"    border-color: rgb(192, 192, 192);\n"
"}\n"
"\n"
"QLineEdit, QComboBox\n"
"{\n"
"    background-color: rgb(29, 31, 34);\n"
"    bord"
                        "er: 1px solid rgb(54, 60, 66);\n"
"    border-radius: 2px;\n"
"    padding: 5px;\n"
"    font-size: 12px;\n"
"}\n"
"\n"
"QComboBox\n"
"{\n"
"    margin-left: 3px;\n"
"    margin-right: 3px;\n"
"}\n"
"\n"
"QPushButton:focus\n"
"{\n"
"    border-color: rgb(48, 167, 227);\n"
"    outline: none;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    border-color: rgb(54, 60, 66);\n"
"}\n"
"\n"
"QPushButton:pressed\n"
"{\n"
"    border-color: rgb(192, 192, 192);\n"
"}\n"
"\n"
"QComboBox:focus, QLineEdit:focus\n"
"{\n"
"    border: 1px solid rgb(48, 167, 227);\n"
"}\n"
"\n"
"QComboBox:drop-down:button {\n"
"    border: 1px solid rgb(54, 60, 66);\n"
"}\n"
"\n"
"QComboBox:down-arrow {\n"
"    image: url(:/shotgun_authentication/down-arrow.png);\n"
"}\n"
"\n"
"QLineEdit:disabled {\n"
"    background-color: rgb(60, 60, 60);\n"
"    color: rgb(160, 160, 160);\n"
"}\n"
"\n"
"QComboBox::drop-down:disabled {\n"
"    border-width: 0px;\n"
"}\n"
"\n"
"QComboBox::down-arrow:disabled {\n"
"    image: url(noimg); border-width: 0px;\n"
"}\n"
""
                        "\n"
"QComboBox::disabled {\n"
"    background-color: rgb(60, 60, 60);\n"
"    color: rgb(160, 160, 160);\n"
"}\n"
"\n"
"QPushButton.main\n"
"{\n"
"    background-color: rgb(35, 165, 225);\n"
"    border-color: rgb(36, 39, 42);\n"
"    color: rgb(248, 248, 248);\n"
"}\n"
"\n"
"QPushButton.main:focus, QPushButton.main:hover\n"
"{\n"
"    border-color: rgb(54, 60, 66);\n"
"}\n"
"\n"
"QPushButton.main:pressed\n"
"{\n"
"    border-color: rgb(248, 248, 248);\n"
"}\n"
"")
        LoginDialog.setModal(True)
        self.verticalLayout_2 = QVBoxLayout(LoginDialog)
        self.verticalLayout_2.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.logo = AspectPreservingLabel(LoginDialog)
        self.logo.setObjectName(u"logo")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logo.sizePolicy().hasHeightForWidth())
        self.logo.setSizePolicy(sizePolicy)
        self.logo.setMaximumSize(QSize(320, 72))
        self.logo.setPixmap(QPixmap(u":/shotgun_authentication/shotgun_logo_light_medium.png"))
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setTextInteractionFlags(Qt.NoTextInteraction)

        self.horizontalLayout.addWidget(self.logo)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.stackedWidget = QStackedWidget(LoginDialog)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setMinimumSize(QSize(324, 172))
        self.login_page = QWidget()
        self.login_page.setObjectName(u"login_page")
        self.verticalLayout_3 = QVBoxLayout(self.login_page)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.credentials = QWidget(self.login_page)
        self.credentials.setObjectName(u"credentials")
        self.credentials.setMinimumSize(QSize(0, 126))
        self.verticalLayout_7 = QVBoxLayout(self.credentials)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.site = RecentBox(self.credentials)
        self.site.setObjectName(u"site")

        self.verticalLayout_7.addWidget(self.site)

        self.login = RecentBox(self.credentials)
        self.login.setObjectName(u"login")

        self.verticalLayout_7.addWidget(self.login)

        self.password = QLineEdit(self.credentials)
        self.password.setObjectName(u"password")
        self.password.setMinimumSize(QSize(308, 0))
        self.password.setEchoMode(QLineEdit.Password)

        self.verticalLayout_7.addWidget(self.password)

        self.message = QLabel(self.credentials)
        self.message.setObjectName(u"message")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.message.sizePolicy().hasHeightForWidth())
        self.message.setSizePolicy(sizePolicy1)
        self.message.setTextFormat(Qt.RichText)
        self.message.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.message.setWordWrap(True)
        self.message.setMargin(4)
        self.message.setOpenExternalLinks(True)

        self.verticalLayout_7.addWidget(self.message)

        self.verticalSpacer_3 = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer_3)

        self.verticalLayout_3.addWidget(self.credentials)

        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(10)
        self.button_layout.setObjectName(u"button_layout")
        self.button_layout.setContentsMargins(0, -1, -1, -1)
        self.button_options = QPushButton(self.login_page)
        self.button_options.setObjectName(u"button_options")
        self.button_options.setAutoDefault(False)
        self.button_options.setFlat(True)

        self.button_layout.addWidget(self.button_options)

        self.links = QVBoxLayout()
        self.links.setObjectName(u"links")
        self.forgot_password_link = QLabel(self.login_page)
        self.forgot_password_link.setObjectName(u"forgot_password_link")
        self.forgot_password_link.setCursor(QCursor(Qt.PointingHandCursor))
        self.forgot_password_link.setTextFormat(Qt.RichText)
        self.forgot_password_link.setMargin(4)
        self.forgot_password_link.setOpenExternalLinks(False)

        self.links.addWidget(self.forgot_password_link)

        self.button_layout.addLayout(self.links)

        self.sign_in_hspacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.button_layout.addItem(self.sign_in_hspacer)

        self.sign_in = QPushButton(self.login_page)
        self.sign_in.setObjectName(u"sign_in")
        self.sign_in.setAutoDefault(True)
        self.sign_in.setFlat(True)

        self.button_layout.addWidget(self.sign_in)

        self.button_layout.setStretch(2, 1)

        self.verticalLayout_3.addLayout(self.button_layout)

        self.stackedWidget.addWidget(self.login_page)
        self._2fa_page = QWidget()
        self._2fa_page.setObjectName(u"_2fa_page")
        self.verticalLayout_4 = QVBoxLayout(self._2fa_page)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.credentials_2 = QWidget(self._2fa_page)
        self.credentials_2.setObjectName(u"credentials_2")
        self.credentials_2.setMinimumSize(QSize(0, 133))
        self.horizontalLayout_2 = QHBoxLayout(self.credentials_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.credentials_2)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(86, 0))
        self.label.setPixmap(QPixmap(u":/google_authenticator/google_authenticator.png"))
        self.label.setAlignment(Qt.AlignHCenter|Qt.AlignTop)

        self.horizontalLayout_2.addWidget(self.label)

        self.widget_2 = QWidget(self.credentials_2)
        self.widget_2.setObjectName(u"widget_2")
        self.verticalLayout = QVBoxLayout(self.widget_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self._2fa_message = QLabel(self.widget_2)
        self._2fa_message.setObjectName(u"_2fa_message")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self._2fa_message.sizePolicy().hasHeightForWidth())
        self._2fa_message.setSizePolicy(sizePolicy2)
        self._2fa_message.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self._2fa_message.setWordWrap(True)
        self._2fa_message.setMargin(0)

        self.verticalLayout.addWidget(self._2fa_message)

        self._2fa_code = QLineEdit(self.widget_2)
        self._2fa_code.setObjectName(u"_2fa_code")

        self.verticalLayout.addWidget(self._2fa_code)

        self.invalid_code = QLabel(self.widget_2)
        self.invalid_code.setObjectName(u"invalid_code")
        sizePolicy2.setHeightForWidth(self.invalid_code.sizePolicy().hasHeightForWidth())
        self.invalid_code.setSizePolicy(sizePolicy2)

        self.verticalLayout.addWidget(self.invalid_code)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.horizontalLayout_2.addWidget(self.widget_2)

        self.verticalLayout_4.addWidget(self.credentials_2)

        self.button_layout_2 = QHBoxLayout()
        self.button_layout_2.setSpacing(10)
        self.button_layout_2.setObjectName(u"button_layout_2")
        self.button_layout_2.setContentsMargins(0, -1, -1, -1)
        self.use_backup = QPushButton(self._2fa_page)
        self.use_backup.setObjectName(u"use_backup")
        self.use_backup.setFlat(True)

        self.button_layout_2.addWidget(self.use_backup)

        self._2fa_hspacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.button_layout_2.addItem(self._2fa_hspacer)

        self.verify_2fa = QPushButton(self._2fa_page)
        self.verify_2fa.setObjectName(u"verify_2fa")
        self.verify_2fa.setMinimumSize(QSize(65, 0))
        self.verify_2fa.setAutoDefault(False)
        self.verify_2fa.setFlat(True)

        self.button_layout_2.addWidget(self.verify_2fa)

        self.verticalLayout_4.addLayout(self.button_layout_2)

        self.stackedWidget.addWidget(self._2fa_page)
        self.backup_page = QWidget()
        self.backup_page.setObjectName(u"backup_page")
        self.verticalLayout_6 = QVBoxLayout(self.backup_page)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.credentials_3 = QWidget(self.backup_page)
        self.credentials_3.setObjectName(u"credentials_3")
        self.credentials_3.setMinimumSize(QSize(0, 133))
        self.horizontalLayout_3 = QHBoxLayout(self.credentials_3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(self.credentials_3)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setPixmap(QPixmap(u":/backup_codes/backup_codes_light_bg.png"))
        self.label_2.setAlignment(Qt.AlignHCenter|Qt.AlignTop)

        self.horizontalLayout_3.addWidget(self.label_2)

        self.widget_4 = QWidget(self.credentials_3)
        self.widget_4.setObjectName(u"widget_4")
        self.verticalLayout_5 = QVBoxLayout(self.widget_4)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self._2fa_message_2 = QLabel(self.widget_4)
        self._2fa_message_2.setObjectName(u"_2fa_message_2")
        sizePolicy2.setHeightForWidth(self._2fa_message_2.sizePolicy().hasHeightForWidth())
        self._2fa_message_2.setSizePolicy(sizePolicy2)
        self._2fa_message_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self._2fa_message_2.setWordWrap(True)
        self._2fa_message_2.setMargin(0)

        self.verticalLayout_5.addWidget(self._2fa_message_2)

        self.backup_code = QLineEdit(self.widget_4)
        self.backup_code.setObjectName(u"backup_code")

        self.verticalLayout_5.addWidget(self.backup_code)

        self.invalid_backup_code = QLabel(self.widget_4)
        self.invalid_backup_code.setObjectName(u"invalid_backup_code")
        sizePolicy2.setHeightForWidth(self.invalid_backup_code.sizePolicy().hasHeightForWidth())
        self.invalid_backup_code.setSizePolicy(sizePolicy2)

        self.verticalLayout_5.addWidget(self.invalid_backup_code)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer)

        self.horizontalLayout_3.addWidget(self.widget_4)

        self.verticalLayout_6.addWidget(self.credentials_3)

        self.button_layout_3 = QHBoxLayout()
        self.button_layout_3.setSpacing(10)
        self.button_layout_3.setObjectName(u"button_layout_3")
        self.button_layout_3.setContentsMargins(0, -1, -1, -1)
        self.use_app = QPushButton(self.backup_page)
        self.use_app.setObjectName(u"use_app")
        self.use_app.setAutoDefault(False)
        self.use_app.setFlat(True)

        self.button_layout_3.addWidget(self.use_app)

        self.backup_hspacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.button_layout_3.addItem(self.backup_hspacer)

        self.verify_backup = QPushButton(self.backup_page)
        self.verify_backup.setObjectName(u"verify_backup")
        self.verify_backup.setMinimumSize(QSize(65, 0))
        self.verify_backup.setAutoDefault(True)
        self.verify_backup.setFlat(True)

        self.button_layout_3.addWidget(self.verify_backup)

        self.verticalLayout_6.addLayout(self.button_layout_3)

        self.stackedWidget.addWidget(self.backup_page)
        self.asl_page = QWidget()
        self.asl_page.setObjectName(u"asl_page")
        self.verticalLayout_21 = QVBoxLayout(self.asl_page)
        self.verticalLayout_21.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.asl_msg = QLabel(self.asl_page)
        self.asl_msg.setObjectName(u"asl_msg")
        sizePolicy1.setHeightForWidth(self.asl_msg.sizePolicy().hasHeightForWidth())
        self.asl_msg.setSizePolicy(sizePolicy1)
        self.asl_msg.setStyleSheet(u"padding-left: 40px; padding-left: 40px;padding-right: 40px;")
        self.asl_msg.setAlignment(Qt.AlignCenter)
        self.asl_msg.setWordWrap(True)

        self.verticalLayout_21.addWidget(self.asl_msg)

        self.asl_msg_back = QLabel(self.asl_page)
        self.asl_msg_back.setObjectName(u"asl_msg_back")
        self.asl_msg_back.setAlignment(Qt.AlignCenter)
        self.asl_msg_back.setWordWrap(True)

        self.verticalLayout_21.addWidget(self.asl_msg_back)

        self.asl_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_21.addItem(self.asl_spacer)

        self.asl_msg_help = QLabel(self.asl_page)
        self.asl_msg_help.setObjectName(u"asl_msg_help")
        self.asl_msg_help.setAlignment(Qt.AlignCenter)
        self.asl_msg_help.setWordWrap(True)

        self.verticalLayout_21.addWidget(self.asl_msg_help)

        self.stackedWidget.addWidget(self.asl_page)

        self.verticalLayout_2.addWidget(self.stackedWidget)

        self.verticalLayout_2.setStretch(0, 1)

        self.retranslateUi(LoginDialog)

        self.stackedWidget.setCurrentIndex(0)
        self.sign_in.setDefault(True)
        self.verify_2fa.setDefault(True)
        self.verify_backup.setDefault(True)

        QMetaObject.connectSlotsByName(LoginDialog)
    # setupUi

    def retranslateUi(self, LoginDialog):
        LoginDialog.setWindowTitle(QCoreApplication.translate("LoginDialog", u"Flow Production Tracking Login", None))
        self.logo.setText("")
#if QT_CONFIG(accessibility)
        self.site.setAccessibleName(QCoreApplication.translate("LoginDialog", u"site", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.login.setAccessibleName(QCoreApplication.translate("LoginDialog", u"login", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.password.setAccessibleName(QCoreApplication.translate("LoginDialog", u"password", None))
#endif // QT_CONFIG(accessibility)
        self.password.setPlaceholderText(QCoreApplication.translate("LoginDialog", u"password", None))
        self.message.setText(QCoreApplication.translate("LoginDialog", u"Please enter your credentials.", None))
        self.button_options.setText(QCoreApplication.translate("LoginDialog", u"See other options", None))
        self.forgot_password_link.setText(QCoreApplication.translate("LoginDialog", u"<html><head/><body><p><a href=\"#\" style=\"color:#c0c1c3;\">Forgot your password?</a></p></body></html>", None))
        self.sign_in.setText(QCoreApplication.translate("LoginDialog", u"Sign In", None))
        self.sign_in.setProperty("class", QCoreApplication.translate("LoginDialog", u"main", None))
        self.label.setText("")
        self._2fa_message.setText(QCoreApplication.translate("LoginDialog", u"Enter the code generated by the Google Authenticator or Duo Mobile app.", None))
#if QT_CONFIG(accessibility)
        self._2fa_code.setAccessibleName(QCoreApplication.translate("LoginDialog", u"2fa code", None))
#endif // QT_CONFIG(accessibility)
        self._2fa_code.setPlaceholderText(QCoreApplication.translate("LoginDialog", u"Enter code", None))
        self.invalid_code.setText("")
        self.use_backup.setText(QCoreApplication.translate("LoginDialog", u"Use backup code", None))
        self.verify_2fa.setText(QCoreApplication.translate("LoginDialog", u"Verify", None))
        self.verify_2fa.setProperty("class", QCoreApplication.translate("LoginDialog", u"main", None))
        self.label_2.setText("")
        self._2fa_message_2.setText(QCoreApplication.translate("LoginDialog", u"Please enter one of your backup codes.", None))
#if QT_CONFIG(accessibility)
        self.backup_code.setAccessibleName(QCoreApplication.translate("LoginDialog", u"backup code", None))
#endif // QT_CONFIG(accessibility)
        self.backup_code.setText("")
        self.backup_code.setPlaceholderText(QCoreApplication.translate("LoginDialog", u"Enter backup code", None))
        self.invalid_backup_code.setText("")
        self.use_app.setText(QCoreApplication.translate("LoginDialog", u"Use Google App", None))
        self.verify_backup.setText(QCoreApplication.translate("LoginDialog", u"Verify", None))
        self.verify_backup.setProperty("class", QCoreApplication.translate("LoginDialog", u"main", None))
        self.asl_msg.setText(QCoreApplication.translate("LoginDialog", u"Check your default web browser to continue logging in.", None))
        self.asl_msg_back.setText(QCoreApplication.translate("LoginDialog", u"<html><head/><body><p><a href=\"#\"><span style=\" text-decoration: underline; color:#c0c1c3;\">Cancel & return to the login page</span></a></p></body></html>", None))
        self.asl_msg_help.setText(QCoreApplication.translate("LoginDialog", u"<html><head/><body><p>If you are having trouble logging in with the browser, <a href=\"{url}\"><span style=\" text-decoration: underline; color:#c0c1c3;\">select this support link</span></a></p></body></html>", None))
    # retranslateUi
