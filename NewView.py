from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import (
    QMainWindow
)
from PyQt5.QtCore import QTimer, Qt, pyqtSlot
from PyQt5.uic import loadUi
from ui.newUi import Ui_MainWindow

import numpy as np
import cv2
import yaml

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
        self.qs = QSound('sound/welcome.wav', parent=self.labelSpeed)
        if config["PRODUCTION"] is True:
            self.qs.play()

    def prepareWorker(self, worker):
        self.Worker = worker()
        self.Worker.finished.connect(self.setDefaultView)
        self.Worker.LeftImage.connect(self.UpdateLeftSlot)
        self.Worker.RightImage.connect(self.UpdateRightSlot)

        self.Worker.RightCameraStatus.connect(self.UpdateRightCameraStatus)
        self.Worker.LeftCameraStatus.connect(self.UpdateLeftCameraStatus)
        self.Worker.FrontCameraStatus.connect(self.UpdateFrontCameraStatus)

        self.Worker.Alert.connect(self.runAlert)

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

    def keyPressEvent(self, event):
        key = event.key()
        print(key)

        if key == 72:
            self.checkBoxCamLeft.setChecked(1)
        elif key == 71:
            self.checkBoxCamLeft.setChecked(0)

        if key == 81:  # Q
            self.Worker.stop()
        elif key == 87 and self.Worker.command.value == 0:  # W
            self.Worker.start()

    def runAlert(self, WarnAlert):
        if not self.qs.isFinished():
            return

        self.labelSpeed.setText(WarnAlert.warn_message)
        sound_file = WarnAlert.warn_file
        self.qs = QSound(sound_file, parent=self.labelSpeed)
        self.qs.play()

        for i in range(0, 1800, 600):
            QTimer.singleShot((0.5 * i), lambda: self.labelSpeed.setStyleSheet(self.defaultStyleSheet.replace("black", WarnAlert.warn_color)))
                # f"background-color: {WarnAlert.warn_color}; font-family:微軟正黑體; font-size:20pt;font-weight: bold;"))
            QTimer.singleShot(
                i, lambda: self.labelSpeed.setStyleSheet(self.defaultStyleSheet))

    def setImg(self, frame, label):

        Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        Pic = QImage(Image.data, Image.shape[1],
                     Image.shape[0], QImage.Format_RGB888)

        if config["PRODUCTION"] is not True:
            h, w = label.size().height(), label.size().width()
            Pic = Pic.scaled(w, h, Qt.KeepAspectRatio)

        # 如果有需要再獨立 目前先放在這一併執行
        label.setPixmap(QPixmap.fromImage(Pic))
