from abc import ABC, abstractclassmethod
import cv2
from datetime import datetime
from factories import AlertFactory
from PyQt5.QtCore import pyqtSignal
import multiprocessing as mp
from sys import platform
import queue
import yaml

from cameraFunc import YoloCamera, CombinedCamera, TestCamera

with open('config.yml', 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)


class ICameraProcess(ABC):
    @abstractclassmethod
    def runCamera(self):
        return NotImplemented

    @abstractclassmethod
    def setRecorder(self):
        return NotImplemented

    @abstractclassmethod
    def recordFrame(self):
        return NotImplemented

    @abstractclassmethod
    def getFrame(self):
        return NotImplemented

    @abstractclassmethod
    def endCamera(self):
        return NotImplemented


class BasicCameraProccess(ICameraProcess):
    def __init__(
            self, camera_id: str, ImageSignal: pyqtSignal, AlertSignal: pyqtSignal, StatusSignal: pyqtSignal) -> None:
        super().__init__()

        self.camera = object

        self.ImageSignal = ImageSignal
        self.AlertSignal = AlertSignal
        self.StatusSignal = StatusSignal

        self.camera_id = camera_id
        self.video_index = 1
        self.command = mp.Value('i', 0)
        self.status = mp.Value('i', 0)
        self.alert = mp.Value('i', 99)
        self.queue = mp.Queue(4)

    def runCamera(self):
        self.proccess = mp.Process(target=self.camera, args=(
            self.queue, self.command, self.alert, self.camera_id, self.status,))

        self.command.value = 1
        self.proccess.start()
        self.setRecorder()

    def setRecorder(self):
        self.t1 = datetime.now()
        self.t2 = self.t1
        fileName = f"videos/cam_{self.camera_id}_{self.video_index}.avi"
        video_code = cv2.VideoWriter_fourcc(*'XVID')
        frameRate = 20
        resolution = (config["MainImage_Width"], config["MainImage_Height"])
        self.videoOutput = cv2.VideoWriter(fileName, video_code, frameRate, resolution)

    def recordFrame(self, frame):
        self.videoOutput.write(frame)
        self.t2 = datetime.now()
        if (self.t2 - self.t1).seconds >= int(config["Record_Seconds"]):
            self.videoOutput.release()
            self.video_index += 1
            # 每30分鐘洗白重來
            self.video_index = self.video_index % int(config["Record_Total"])
            self.setRecorder()

    def getStatus(self):
        self.StatusSignal.emit(self.status.value)

    def getFrame(self):
        try:
            frame = self.queue.get_nowait()
            self.recordFrame(frame)
            self.ImageSignal.emit(frame)
            return frame
        except queue.Empty or queue.Full:
            pass

    def getAlert(self):
        if self.alert.value == AlertFactory.AlertIndex_None:
            return

        WarnAlert = AlertFactory.AlertList[self.alert.value]
        WarnAlert.redAlert()

        self.AlertSignal.emit(WarnAlert)
        self.alert.value = AlertFactory.AlertIndex_None

    def endCamera(self):
        self.command.value = 0
        self.videoOutput.release()
        self.StatusSignal.emit(0)

        # while not self.queue.empty:
        #     self.queue.get_nowait()
        #     print("cleaning")
        # self.queue.close()
        # print("closed")

        if platform == "linux":
            self.proccess.terminate()
        else:
            self.proccess.kill()


class TestCameraProcess(BasicCameraProccess):
    def __init__(
            self, camera_id: str, ImageSignal: pyqtSignal, AlertSignal: pyqtSignal, StatusSignal: pyqtSignal) -> None:
        super().__init__(camera_id, ImageSignal, AlertSignal, StatusSignal)
        self.camera = TestCamera.runCamera

    def setRecorder(self):
        self.t1 = datetime.now()
        self.t2 = self.t1
        fileName = f"videos/cam_{self.camera_id}_{self.video_index}.avi"
        video_code = cv2.VideoWriter_fourcc(*'XVID')
        frameRate = 20
        resolution = (640, 480) #解析度不同
        self.videoOutput = cv2.VideoWriter(fileName, video_code, frameRate, resolution)

class CombinedCameraProcess(BasicCameraProccess):
    def __init__(
            self, camera_id: str, ImageSignal: pyqtSignal, AlertSignal: pyqtSignal, StatusSignal: pyqtSignal) -> None:
        super().__init__(camera_id, ImageSignal, AlertSignal, StatusSignal)
        self.camera = CombinedCamera.runCamera


class YoloCameraProcess(BasicCameraProccess):
    def __init__(
            self, camera_id: str, ImageSignal: pyqtSignal, AlertSignal: pyqtSignal, StatusSignal: pyqtSignal) -> None:
        super().__init__(camera_id, ImageSignal, AlertSignal, StatusSignal)
        self.camera = YoloCamera.runCamera
