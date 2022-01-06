from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import (
    QMainWindow
)
from PyQt5.QtCore import QTimer, Qt, pyqtSlot
from PyQt5.uic import loadUi
from factories.AlertFactory import AlertFactory, AlertList
from ui.newUi import Ui_MainWindow

import os
import numpy as np
import cv2
import yaml

from model.AlertModel import WarnAlert

with open('config.yml', 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)


class ViewWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.defaultStyleSheet = "background-color: black; font-family:微軟正黑體; font-size:28pt;font-weight: bold; color:white"
        self.styleSheetStatusOn = "background-color: black; font-family:微軟正黑體; color: white"
        self.styleSheetStatusOff = "background-color: red; font-family:微軟正黑體; color: black"
        self.defaultWarnMessage = "警示訊息"
        self.defaultFrontLabelText = "前鏡頭"
        self.defaultLeftLabelText = "左鏡頭"
        self.defaultRightLabelText = "右鏡頭"

    def setup(self, controller):
        sound_file = f'{os.getcwd()}/sound/welcome.wav'
        self.qs = QSound(sound_file)
        self.controller = controller
        # self.showMaximized()

        self.alert_list = [QSound(warn.warn_file) for warn in AlertList]

        if config["PRODUCTION"] is True:
            self.qs.play()

    @pyqtSlot()
    def setDefaultView(self):
        self.labelCamLeft.clear()
        self.labelCamRight.clear()

        self.labelCamLeft.setText(self.defaultLeftLabelText)
        self.labelCamRight.setText(self.defaultRightLabelText)

    @pyqtSlot(int)
    def UpdateRightCameraStatus(self, status):
        self.checkBoxCamRight.setChecked(status)
        self.checkBoxCamRight.setStyleSheet(self.styleSheetStatusOn)
        if status == 0:
            self.setDefaultView()
            self.checkBoxCamRight.setStyleSheet(self.styleSheetStatusOff)

    @pyqtSlot(int)
    def UpdateLeftCameraStatus(self, status):
        self.checkBoxCamLeft.setChecked(status)
        self.checkBoxCamLeft.setStyleSheet(self.styleSheetStatusOn)
        if status == 0:
            self.setDefaultView()
            self.checkBoxCamLeft.setStyleSheet(self.styleSheetStatusOff)

    @pyqtSlot(int)
    def UpdateFrontCameraStatus(self, status):
        self.checkBoxCamFront.setChecked(status)
        self.checkBoxCamFront.setStyleSheet(self.styleSheetStatusOn)
        if status == 0:
            self.checkBoxCamFront.setStyleSheet(self.styleSheetStatusOff)

    @pyqtSlot(np.ndarray)
    def UpdateLeftSlot(self, Image):
        self.setImg(Image, self.labelCamLeft)

    @pyqtSlot(np.ndarray)
    def UpdateRightSlot(self, Image):
        self.setImg(Image, self.labelCamRight)

    @pyqtSlot(np.ndarray)
    def UpdateFrontSlot(self, Image):
        pass

    @pyqtSlot(str)
    def UpdateCpuUsage(self, value):
        self.labelCpuNum.setText(value)

    @pyqtSlot(str)
    def UpdateGpuUsage(self, value):
        self.labelGpuNum.setText(value)

    @pyqtSlot(WarnAlert)
    def runAlert(self, WarnAlert):

        for alert in self.alert_list:
            if not alert.isFinished():
                return

        self.alert_list[WarnAlert.alertIndex].play()

        self.labelSpeed.setText(WarnAlert.warn_message)

        for i in range(0, 1800, 600):
            QTimer.singleShot((0.5 * i), lambda: self.labelSpeed.setStyleSheet(self.defaultStyleSheet.replace("black", WarnAlert.warn_color)))
            QTimer.singleShot(
                i, lambda: self.labelSpeed.setStyleSheet(self.defaultStyleSheet))

    def keyPressEvent(self, event):
        key = event.key()
        self.controller.keyPress(key)

    def setImg(self, frame, label):
        Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        Pic = QImage(Image.data, Image.shape[1],
                     Image.shape[0], QImage.Format_RGB888)

        if config["PRODUCTION"] is not True:
            h, w = label.size().height(), label.size().width()
            Pic = Pic.scaled(w, h, Qt.KeepAspectRatio)

        # 如果有需要再獨立 目前先放在這一併執行
        label.setPixmap(QPixmap.fromImage(Pic))
