from PyQt5.QtCore import QThread, pyqtSignal

import numpy
import multiprocessing as mp

from model.AlertModel import WarnAlert
from model.ProccessModel import TestCameraProcess
from factories import CameraFactory
import yaml

with open('config.yml', 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)


class Worker(QThread):
    FrontImage = pyqtSignal(numpy.ndarray)
    LeftImage = pyqtSignal(numpy.ndarray)
    RightImage = pyqtSignal(numpy.ndarray)
    Alert = pyqtSignal(WarnAlert)

    LeftCameraStatus = pyqtSignal(int)
    RightCameraStatus = pyqtSignal(int)
    FrontCameraStatus = pyqtSignal(int)

    def run(self):
        # LeftCamera = CombinedCameraProccess(config["LEFT_CAMERA_ID"], self.LeftImage, self.Alert, self.LeftCameraStatus)
        # RightCamera = CombinedCameraProccess(config["RIGHT_CAMERA_ID"], self.RightImage, self.Alert, self.RightCameraStatus)
        RightCamera = TestCameraProcess(config["RIGHT_CAMERA_ID"], self.RightImage, self.Alert, self.LeftCameraStatus)
        # FrontCamera = YoloCameraProccess(config["FRONT_CAMERA_ID"], self.FrontImage, self.Alert, self.FrontCameraStatus)

        Cameras = [RightCamera]

        for Camera in Cameras:
            Camera.runCamera()

        self.ThreadActive = True

        while self.ThreadActive:
            for Camera in Cameras:
                Camera.getStatus()
                Camera.getFrame()
                Camera.getAlert()

        for Camera in Cameras:
            Camera.endCamera()

        self.quit()

    def stop(self):
        self.ThreadActive = False
