# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/about.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DialogAbout(object):
    def setupUi(self, DialogAbout):
        DialogAbout.setObjectName("DialogAbout")
        DialogAbout.resize(336, 282)
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(40)
        DialogAbout.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(DialogAbout)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(DialogAbout)
        self.label.setMidLineWidth(1)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(DialogAbout)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.pushButtonClose = QtWidgets.QPushButton(DialogAbout)
        self.pushButtonClose.setObjectName("pushButtonClose")
        self.verticalLayout.addWidget(self.pushButtonClose)

        self.retranslateUi(DialogAbout)
        QtCore.QMetaObject.connectSlotsByName(DialogAbout)

    def retranslateUi(self, DialogAbout):
        _translate = QtCore.QCoreApplication.translate
        DialogAbout.setWindowTitle(_translate("DialogAbout", "關於"))
        self.label.setText(_translate("DialogAbout", "AI警示系統"))
        self.label_2.setText(_translate("DialogAbout", "V 1.0.0"))
        self.pushButtonClose.setText(_translate("DialogAbout", "關閉"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DialogAbout = QtWidgets.QDialog()
    ui = Ui_DialogAbout()
    ui.setupUi(DialogAbout)
    DialogAbout.show()
    sys.exit(app.exec_())
