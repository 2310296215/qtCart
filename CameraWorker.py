import numpy
import yaml

from factories.AlertFactory import AlertEnum
from PyQt5.QtCore import QThread, pyqtSignal
from model.ProccessModel import TestCameraProcess, CombinedCameraProcess, YoloCameraProcess


with open('config.yml', 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)


class CameraWorker(QThread):
    FrontImage = pyqtSignal(numpy.ndarray)
    LeftImage = pyqtSignal(numpy.ndarray)
    RightImage = pyqtSignal(numpy.ndarray)
    Alert = pyqtSignal(AlertEnum)

    LeftCameraStatus = pyqtSignal(int)
    RightCameraStatus = pyqtSignal(int)
    FrontCameraStatus = pyqtSignal(int)

    def run(self):
        TestCamera = TestCameraProcess("TEST_CAMERA_ID", self.RightImage, self.Alert, self.RightCameraStatus)

        LeftCamera = CombinedCameraProcess(config["LEFT_CAMERA_ID"], self.LeftImage, self.Alert, self.LeftCameraStatus)
        RightCamera = CombinedCameraProcess(config["RIGHT_CAMERA_ID"], self.RightImage, self.Alert, self.RightCameraStatus)
        FrontCamera = YoloCameraProcess(config["FRONT_CAMERA_ID"], self.FrontImage, self.Alert, self.FrontCameraStatus)

        Cameras = [TestCamera] #[LeftCamera, RightCamera, FrontCamera]

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
