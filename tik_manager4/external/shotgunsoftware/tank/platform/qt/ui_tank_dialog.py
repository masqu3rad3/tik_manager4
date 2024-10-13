# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tank_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from . import QtCore
for name, cls in QtCore.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls

from . import QtGui
for name, cls in QtGui.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls


from  . import resources_rc

class Ui_TankDialog(object):
    def setupUi(self, TankDialog):
        if not TankDialog.objectName():
            TankDialog.setObjectName(u"TankDialog")
        TankDialog.resize(879, 551)
        TankDialog.setStyleSheet(u"")
        self.verticalLayout_3 = QVBoxLayout(TankDialog)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(TankDialog)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page_1 = QWidget()
        self.page_1.setObjectName(u"page_1")
        self.page_1.setStyleSheet(u"QWidget#page_1 {\n"
"margin: 0px;\n"
"}")
        self.verticalLayout = QVBoxLayout(self.page_1)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.top_group = QGroupBox(self.page_1)
        self.top_group.setObjectName(u"top_group")
        self.top_group.setMinimumSize(QSize(0, 45))
        self.top_group.setMaximumSize(QSize(16777215, 45))
        self.top_group.setStyleSheet(u"#top_group {\n"
"background-color:  #2D2D2D;\n"
"border: none;\n"
"border-bottom:1px solid #202020;\n"
"}\n"
"")
        self.top_group.setFlat(False)
        self.horizontalLayout = QHBoxLayout(self.top_group)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(4, 0, 1, 1)
        self.tank_logo = QLabel(self.top_group)
        self.tank_logo.setObjectName(u"tank_logo")
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tank_logo.sizePolicy().hasHeightForWidth())
        self.tank_logo.setSizePolicy(sizePolicy)
        self.tank_logo.setPixmap(QPixmap(u":/Tank.Platform.Qt/tank_logo.png"))

        self.horizontalLayout.addWidget(self.tank_logo)

        self.label = QLabel(self.top_group)
        self.label.setObjectName(u"label")
        self.label.setStyleSheet(u"/* want this stylesheet to apply to the label but not the tooltip */\n"
"QLabel{\n"
"    color: white;\n"
"    font-size: 20px;\n"
"    margin-left: 5px;\n"
"    font-family: \"Open Sans\";\n"
"    font-style: \"Regular\";\n"
"}")

        self.horizontalLayout.addWidget(self.label)

        self.lbl_context = QLabel(self.top_group)
        self.lbl_context.setObjectName(u"lbl_context")
        self.lbl_context.setStyleSheet(u"/* want this stylesheet to apply to the label but not the tooltip */\n"
"QLabel {\n"
"    color: rgba(250,250,250,180);\n"
"    font-size: 11px;\n"
"    margin-right: 8px;\n"
"    font-family: \"Open Sans\";\n"
"    font-style: \"Regular\";\n"
"}\n"
"\n"
"\n"
"")
        self.lbl_context.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout.addWidget(self.lbl_context)

        self.details_show = QToolButton(self.top_group)
        self.details_show.setObjectName(u"details_show")
        self.details_show.setMinimumSize(QSize(34, 34))
        self.details_show.setFocusPolicy(Qt.ClickFocus)
        self.details_show.setStyleSheet(u"QToolButton{\n"
"width: 12px;\n"
"height: 20px;\n"
"background-image: url(:/Tank.Platform.Qt/arrow.png);\n"
"border: none;\n"
"background-color: none;\n"
"}\n"
"\n"
"QToolButton:hover{\n"
"background-image: url(:/Tank.Platform.Qt/arrow_hover.png);\n"
"}\n"
"\n"
"QToolButton:pressed{\n"
"background-image: url(:/Tank.Platform.Qt/arrow_pressed.png);\n"
"}\n"
"")
        self.details_show.setAutoRaise(True)

        self.horizontalLayout.addWidget(self.details_show)

        self.details_hide = QToolButton(self.top_group)
        self.details_hide.setObjectName(u"details_hide")
        self.details_hide.setMinimumSize(QSize(34, 34))
        self.details_hide.setFocusPolicy(Qt.ClickFocus)
        self.details_hide.setVisible(False)
        self.details_hide.setStyleSheet(u"QToolButton{\n"
" width: 12px;\n"
" height: 20px;\n"
" background-image: url(:/Tank.Platform.Qt/arrow_flipped.png);\n"
" border: none;\n"
" background-color: none;\n"
" }\n"
"\n"
" QToolButton:hover{\n"
" background-image: url(:/Tank.Platform.Qt/arrow_flipped_hover.png);\n"
" }\n"
"\n"
" QToolButton:pressed{\n"
" background-image: url(:/Tank.Platform.Qt/arrow_flipped_pressed.png);\n"
" }\n"
" ")
        self.details_hide.setAutoRaise(True)

        self.horizontalLayout.addWidget(self.details_hide)

        self.verticalLayout.addWidget(self.top_group)

        self.target = QVBoxLayout()
        self.target.setSpacing(4)
        self.target.setObjectName(u"target")

        self.verticalLayout.addLayout(self.target)

        self.stackedWidget.addWidget(self.page_1)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.page_2.setStyleSheet(u"QWidget {\n"
"    font-family: \"Open Sans\";\n"
"    font-style: \"Regular\";\n"
"}")
        self.verticalLayout_2 = QVBoxLayout(self.page_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(1, 1, 1, 1)
        self.page_2_group = QGroupBox(self.page_2)
        self.page_2_group.setObjectName(u"page_2_group")
        self.page_2_group.setMinimumSize(QSize(0, 100))
        self.page_2_group.setStyleSheet(u"QGroupBox {\n"
"margin: 0px;\n"
"}")
        self.horizontalLayout_2 = QHBoxLayout(self.page_2_group)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(145, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.label_3 = QLabel(self.page_2_group)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(40, 0))
        self.label_3.setMaximumSize(QSize(40, 16777215))

        self.horizontalLayout_2.addWidget(self.label_3)

        self.gradient = QGroupBox(self.page_2_group)
        self.gradient.setObjectName(u"gradient")
        self.gradient.setMinimumSize(QSize(11, 0))
        self.gradient.setMaximumSize(QSize(11, 16777215))
        self.gradient.setStyleSheet(u"#gradient {\n"
"background-image: url(:/Tank.Platform.Qt/gradient.png);\n"
"border: none;\n"
"}")

        self.horizontalLayout_2.addWidget(self.gradient)

        self.scrollArea = QScrollArea(self.page_2_group)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setMinimumSize(QSize(400, 0))
        self.scrollArea.setMaximumSize(QSize(400, 16777215))
        self.scrollArea.setStyleSheet(u"/*\n"
"All labels inside this scroll area should be 12px font.\n"
"This is to avoid the UI looking different in different app like\n"
"maya and nuke which all use slightly different style sheets.\n"
" */\n"
"QLabel{\n"
"   font-size: 11px;\n"
"   margin-bottom: 8px\n"
"}\n"
"")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 398, 550))
        self.verticalLayout_4 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.app_icon = QLabel(self.scrollAreaWidgetContents)
        self.app_icon.setObjectName(u"app_icon")
        self.app_icon.setMinimumSize(QSize(64, 64))
        self.app_icon.setMaximumSize(QSize(64, 64))
        self.app_icon.setPixmap(QPixmap(u":/Tank.Platform.Qt/default_app_icon_256.png"))
        self.app_icon.setScaledContents(True)
        self.app_icon.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_4.addWidget(self.app_icon)

        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setSpacing(1)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.app_name = QLabel(self.scrollAreaWidgetContents)
        self.app_name.setObjectName(u"app_name")
        self.app_name.setStyleSheet(u"font-size: 16px;\n"
"")
        self.app_name.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_8.addWidget(self.app_name)

        self.horizontalLayout_4.addLayout(self.verticalLayout_8)

        self.verticalLayout_4.addLayout(self.horizontalLayout_4)

        self.app_description = QLabel(self.scrollAreaWidgetContents)
        self.app_description.setObjectName(u"app_description")
        self.app_description.setMaximumSize(QSize(350, 16777215))
        self.app_description.setWordWrap(True)

        self.verticalLayout_4.addWidget(self.app_description)

        self.app_tech_details = QLabel(self.scrollAreaWidgetContents)
        self.app_tech_details.setObjectName(u"app_tech_details")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.app_tech_details.sizePolicy().hasHeightForWidth())
        self.app_tech_details.setSizePolicy(sizePolicy1)
        self.app_tech_details.setMinimumSize(QSize(0, 22))
        self.app_tech_details.setMaximumSize(QSize(16777215, 22))
        self.app_tech_details.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.app_tech_details.setWordWrap(True)

        self.verticalLayout_4.addWidget(self.app_tech_details)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setSpacing(2)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.btn_documentation = QToolButton(self.scrollAreaWidgetContents)
        self.btn_documentation.setObjectName(u"btn_documentation")

        self.horizontalLayout_9.addWidget(self.btn_documentation)

        self.btn_support = QToolButton(self.scrollAreaWidgetContents)
        self.btn_support.setObjectName(u"btn_support")

        self.horizontalLayout_9.addWidget(self.btn_support)

        self.horizontalSpacer_5 = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_5)

        self.verticalLayout_4.addLayout(self.horizontalLayout_9)

        self.label_5 = QLabel(self.scrollAreaWidgetContents)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setStyleSheet(u"font-size: 16px;\n"
"margin-top: 30px;")

        self.verticalLayout_4.addWidget(self.label_5)

        self.line = QFrame(self.scrollAreaWidgetContents)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_4.addWidget(self.line)

        self.app_work_area_info = QLabel(self.scrollAreaWidgetContents)
        self.app_work_area_info.setObjectName(u"app_work_area_info")
        self.app_work_area_info.setMaximumSize(QSize(350, 16777215))
        self.app_work_area_info.setWordWrap(True)

        self.verticalLayout_4.addWidget(self.app_work_area_info)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setSpacing(2)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.btn_file_system = QToolButton(self.scrollAreaWidgetContents)
        self.btn_file_system.setObjectName(u"btn_file_system")

        self.horizontalLayout_10.addWidget(self.btn_file_system)

        self.btn_shotgun = QToolButton(self.scrollAreaWidgetContents)
        self.btn_shotgun.setObjectName(u"btn_shotgun")

        self.horizontalLayout_10.addWidget(self.btn_shotgun)

        self.horizontalSpacer_6 = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_6)

        self.verticalLayout_4.addLayout(self.horizontalLayout_10)

        self.app_work_area_info_2 = QLabel(self.scrollAreaWidgetContents)
        self.app_work_area_info_2.setObjectName(u"app_work_area_info_2")
        self.app_work_area_info_2.setMaximumSize(QSize(350, 16777215))
        self.app_work_area_info_2.setWordWrap(True)

        self.verticalLayout_4.addWidget(self.app_work_area_info_2)

        self.btn_reload = QToolButton(self.scrollAreaWidgetContents)
        self.btn_reload.setObjectName(u"btn_reload")

        self.verticalLayout_4.addWidget(self.btn_reload)

        self.config_header = QLabel(self.scrollAreaWidgetContents)
        self.config_header.setObjectName(u"config_header")
        self.config_header.setStyleSheet(u"font-size: 16px;\n"
"margin-top: 30px;")

        self.verticalLayout_4.addWidget(self.config_header)

        self.config_line = QFrame(self.scrollAreaWidgetContents)
        self.config_line.setObjectName(u"config_line")
        self.config_line.setFrameShape(QFrame.HLine)
        self.config_line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_4.addWidget(self.config_line)

        self.config_label = QLabel(self.scrollAreaWidgetContents)
        self.config_label.setObjectName(u"config_label")
        self.config_label.setMaximumSize(QSize(350, 16777215))
        self.config_label.setWordWrap(True)

        self.verticalLayout_4.addWidget(self.config_label)

        self.config_layout = QVBoxLayout()
        self.config_layout.setSpacing(20)
        self.config_layout.setObjectName(u"config_layout")

        self.verticalLayout_4.addLayout(self.config_layout)

        self.verticalSpacer_2 = QSpacerItem(328, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout_2.addWidget(self.scrollArea)

        self.verticalLayout_2.addWidget(self.page_2_group)

        self.stackedWidget.addWidget(self.page_2)

        self.verticalLayout_3.addWidget(self.stackedWidget)

        self.retranslateUi(TankDialog)

        self.stackedWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(TankDialog)
    # setupUi

    def retranslateUi(self, TankDialog):
        TankDialog.setWindowTitle(QCoreApplication.translate("TankDialog", u"Dialog", None))
        self.top_group.setTitle("")
        self.tank_logo.setText("")
        self.label.setText(QCoreApplication.translate("TankDialog", u"TextLabel", None))
#if QT_CONFIG(tooltip)
        self.lbl_context.setToolTip(QCoreApplication.translate("TankDialog", u"foo bar", None))
#endif // QT_CONFIG(tooltip)
        self.lbl_context.setText(QCoreApplication.translate("TankDialog", u"Current Work Area:\n"
"TextLabel", None))
#if QT_CONFIG(tooltip)
        self.details_show.setToolTip(QCoreApplication.translate("TankDialog", u"Click for App Details", None))
#endif // QT_CONFIG(tooltip)
        self.details_show.setText("")
#if QT_CONFIG(tooltip)
        self.details_hide.setToolTip(QCoreApplication.translate("TankDialog", u"Hide App Details", None))
#endif // QT_CONFIG(tooltip)
        self.details_hide.setText("")
        self.page_2_group.setTitle("")
        self.label_3.setText("")
        self.gradient.setTitle("")
        self.app_icon.setText("")
        self.app_name.setText(QCoreApplication.translate("TankDialog", u"Publish And Snapshot", None))
        self.app_description.setText(QCoreApplication.translate("TankDialog", u"Tools to see what is out of date in your scene etc etc.", None))
        self.app_tech_details.setText(QCoreApplication.translate("TankDialog", u"tk-multi-snapshot, v1.2.3", None))
        self.btn_documentation.setText(QCoreApplication.translate("TankDialog", u"Documentation", None))
        self.btn_support.setText(QCoreApplication.translate("TankDialog", u"Help && Support", None))
        self.label_5.setText(QCoreApplication.translate("TankDialog", u"Your Current Work Area", None))
        self.app_work_area_info.setText(QCoreApplication.translate("TankDialog", u"TextLabel", None))
        self.btn_file_system.setText(QCoreApplication.translate("TankDialog", u"Jump to File System", None))
        self.btn_shotgun.setText(QCoreApplication.translate("TankDialog", u"Jump to Flow Production Tracking", None))
        self.app_work_area_info_2.setText(QCoreApplication.translate("TankDialog", u"If you are making changes to configuration or code, use the reload button to quickly load your changes in without having to restart:", None))
        self.btn_reload.setText(QCoreApplication.translate("TankDialog", u"Reload Engine and Apps", None))
        self.config_header.setText(QCoreApplication.translate("TankDialog", u"Configuration", None))
        self.config_label.setText(QCoreApplication.translate("TankDialog", u"Below is a list of all the configuration settings for this app, as defined in your environment file:", None))
    # retranslateUi
