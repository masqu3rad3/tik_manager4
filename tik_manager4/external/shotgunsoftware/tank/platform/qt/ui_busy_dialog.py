# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'busy_dialog.ui'
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

class Ui_BusyDialog(object):
    def setupUi(self, BusyDialog):
        if not BusyDialog.objectName():
            BusyDialog.setObjectName(u"BusyDialog")
        BusyDialog.resize(500, 110)
        BusyDialog.setStyleSheet(u"/* Style for the window itself */\n"
"#frame {\n"
"border-color: #30A7E3;\n"
"border-style: solid;\n"
"border-width: 2px;\n"
"}\n"
"\n"
"/* Style for the header text */\n"
"#title {\n"
"color: #30A7E3;\n"
"margin-top: 15px;\n"
"margin-bottom: 0px;\n"
"margin-left: 1px;\n"
"font-size: 16px;\n"
"font-weight: bold;\n"
"}\n"
"\n"
"/* Style for the details text */\n"
"#details {\n"
"margin-top: 1px;\n"
"margin-left: 3px;\n"
"margin-bottom: 0px;\n"
"font-size: 11px;\n"
"}\n"
"")
        self.horizontalLayout_2 = QHBoxLayout(BusyDialog)
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.frame = QFrame(BusyDialog)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setPixmap(QPixmap(u":/Tank.Platform.Qt/sg_logo_80px.png"))

        self.horizontalLayout.addWidget(self.label)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.title = QLabel(self.frame)
        self.title.setObjectName(u"title")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.title.sizePolicy().hasHeightForWidth())
        self.title.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.title)

        self.details = QLabel(self.frame)
        self.details.setObjectName(u"details")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.details.sizePolicy().hasHeightForWidth())
        self.details.setSizePolicy(sizePolicy1)
        self.details.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.details.setWordWrap(True)

        self.verticalLayout.addWidget(self.details)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.horizontalLayout_2.addWidget(self.frame)

        self.retranslateUi(BusyDialog)

        QMetaObject.connectSlotsByName(BusyDialog)
    # setupUi

    def retranslateUi(self, BusyDialog):
        BusyDialog.setWindowTitle(QCoreApplication.translate("BusyDialog", u"Dialog", None))
        self.label.setText("")
        self.title.setText(QCoreApplication.translate("BusyDialog", u"Doing something, hang on!", None))
        self.details.setText(QCoreApplication.translate("BusyDialog", u"Lots of interesting details about what is going on", None))
    # retranslateUi
