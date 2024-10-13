# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'item.ui'
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

class Ui_Item(object):
    def setupUi(self, Item):
        if not Item.objectName():
            Item.setObjectName(u"Item")
        Item.resize(335, 110)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Item.sizePolicy().hasHeightForWidth())
        Item.setSizePolicy(sizePolicy)
        Item.setStyleSheet(u"QLabel{\n"
"   font-size: 11px;\n"
"   margin-bottom: 3px\n"
"}\n"
"")
        self.verticalLayout = QVBoxLayout(Item)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.name = QLabel(Item)
        self.name.setObjectName(u"name")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.name.sizePolicy().hasHeightForWidth())
        self.name.setSizePolicy(sizePolicy1)
        self.name.setStyleSheet(u"font-size: 13px;")
        self.name.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.name.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.name)

        self.line = QFrame(Item)
        self.line.setObjectName(u"line")
        self.line.setStyleSheet(u"border: none;\n"
"border-bottom-color: rgba(150,150,150,100);\n"
"border-bottom-width: 1px;\n"
"border-bottom-style: solid;")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_2.addWidget(self.line)

        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.value = QLabel(Item)
        self.value.setObjectName(u"value")
        sizePolicy1.setHeightForWidth(self.value.sizePolicy().hasHeightForWidth())
        self.value.setSizePolicy(sizePolicy1)
        self.value.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.value.setWordWrap(True)
        self.value.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.verticalLayout.addWidget(self.value)

        self.type = QLabel(Item)
        self.type.setObjectName(u"type")
        sizePolicy1.setHeightForWidth(self.type.sizePolicy().hasHeightForWidth())
        self.type.setSizePolicy(sizePolicy1)
        self.type.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.type.setWordWrap(True)
        self.type.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.verticalLayout.addWidget(self.type)

        self.description = QLabel(Item)
        self.description.setObjectName(u"description")
        self.description.setMaximumSize(QSize(350, 16777215))
        self.description.setTextFormat(Qt.RichText)
        self.description.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.description.setWordWrap(True)
        self.description.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.verticalLayout.addWidget(self.description)

        self.verticalSpacer = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.verticalLayout.setStretch(4, 1)

        self.retranslateUi(Item)

        QMetaObject.connectSlotsByName(Item)
    # setupUi

    def retranslateUi(self, Item):
        Item.setWindowTitle(QCoreApplication.translate("Item", u"Form", None))
        self.name.setText(QCoreApplication.translate("Item", u"Settings Name", None))
        self.value.setText(QCoreApplication.translate("Item", u"Value: foo bar", None))
        self.type.setText(QCoreApplication.translate("Item", u"Type: bool", None))
        self.description.setText(QCoreApplication.translate("Item", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Lucida Grande'; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">description</p></body></html>", None))
    # retranslateUi
