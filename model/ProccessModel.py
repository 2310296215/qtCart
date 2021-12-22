from abc import ABC, abstractclassmethod
import cv2
from datetime import datetime
from factories import AlertFactory
from PyQt5.QtCore import pyqtSignal
import multiprocessing as mp
import queue
import yaml

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
            self, command: mp.Value, camera: object, camera_id: str, ImageSignal: pyqtSignal, AlertSignal: pyqtSignal, StatusSignal: pyqtSignal) -> None:
        super().__init__()
        self.command = command
        self.ImageSignal = ImageSignal
        self.AlertSignal = AlertSignal
        self.StatusSignal = StatusSignal

        self.camera_id = camera_id
        self.video_index = 1

        self.status = mp.Value('i', 0)
        self.alert = mp.Value('i', 99)
        self.queue = mp.Queue(4)
        self.proccess = mp.Process(target=camera, args=(
            self.queue, self.command, self.alert, camera_id, self.status,))

    def runCamera(self):
        self.proccess.start()
        self.setRecorder()

    def setRecorder(self):
        self.t1 = datetime.now()
        self.t2 = self.t1
        fileName = f"videos/cam_{self.camera_id}_{self.video_index}.avi"
        video_code = cv2.VideoWriter_fourcc(*'XVID')
        frameRate = 20
        resolution = (1280, 720)
        self.videoOutput = cv2.VideoWriter(fileName, video_code, frameRate, resolution)

    def recordFrame(self, frame):
        self.videoOutput.write(frame)
        self.t2 = datetime.now()
        if (self.t2 - self.t1).seconds >= int(config["Record_Seconds"]):
            print("RELEASE")
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
        self.videoOutput.release()
        self.StatusSignal.emit(0)
