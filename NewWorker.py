from PyQt5.QtCore import QThread, pyqtSignal

import numpy
import multiprocessing as mp

from model.AlertModel import WarnAlert
from model.ProccessModel import BasicCameraProccess
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

    command = mp.Value('i', 0)

    def run(self):

        self.command.value = 1

        TestCamera = CameraFactory.CameraFactory(CameraFactory.TextTestCamera)
        CombinedCam = CameraFactory.CameraFactory(CameraFactory.TextCombinedCamera)
        YoloCam = CameraFactory.CameraFactory(CameraFactory.TextYoloCamera)

        # LeftCamera = BasicCameraProccess(self.command, CombinedCam, config["LEFT_CAMERA_ID"], self.LeftImage, self.Alert, self.LeftCameraStatus)
        # RightCamera = BasicCameraProccess(self.command, CombinedCam, config["RIGHT_CAMERA_ID"], self.RightImage, self.Alert, self.RightCameraStatus)
        RightCamera = BasicCameraProccess(self.command, TestCamera, config["RIGHT_CAMERA_ID"], self.RightImage, self.Alert, self.LeftCameraStatus)
        # FrontCamera = BasicCameraProccess(self.command, YoloCam, config["FRONT_CAMERA_ID"], self.FrontImage, self.Alert, self.FrontCameraStatus)     

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
        self.command.value = 0
        self.ThreadActive = False
