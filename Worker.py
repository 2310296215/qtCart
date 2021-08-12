from re import S
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage

import multiprocessing as mp
import queue
import cv2
import time

from cameraFunc import FaceCamera, PedestrianCamera
from Gen2.FatigueCam import runFatigueCam

class Worker(QThread):
    FrontImage = pyqtSignal(QImage)
    RearImage = pyqtSignal(QImage)
    Alert = pyqtSignal(str)

    command = mp.Value('i', 1)
    warning = mp.Value('i', 0)
    front_queue = mp.Queue(4)
    rear_queue = mp.Queue(4)

    #front_proccess = mp.Process(target=FaceCamera.runFaceCamera, args=(front_queue, command,))
    front_proccess = mp.Process(target=runFatigueCam, args=(front_queue, command,warning, ))
    rear_proccess = mp.Process(target=PedestrianCamera.runRearCamera, args=(rear_queue, command,))

    def run(self):
        self.front_proccess.start()
        self.rear_proccess.start()
        self.ThreadActive = True
        i = 0
        
        while self.ThreadActive:
            try:
                front_frame = self.front_queue.get_nowait()
                front_Pic = frameToPic(front_frame)
                self.FrontImage.emit(front_Pic)
            except queue.Empty or queue.Full:
                pass

            try:
                rear_frame = self.rear_queue.get_nowait()
                rear_Pic = frameToPic(rear_frame)
                self.RearImage.emit(rear_Pic)
            except queue.Empty or queue.Full:
                pass
            if self.warning.value == 1:
                self.Alert.emit('alert alert')
                self.warning.value = 0

        print('while loop ended')
        self.front_queue.close()
        self.rear_queue.close()       

        # normally dont just kill
        self.front_proccess.kill()
        self.rear_proccess.kill() 


    def stop(self):
        self.command.value = 0
        self.ThreadActive = False
        self.quit()

    @staticmethod
    def cvFrametoQtImage(frame):
        pass

def frameToPic(frame):
    Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    ConvertToQtFormat = QImage(Image.data, Image.shape[1], Image.shape[0], QImage.Format_RGB888)
    Pic = ConvertToQtFormat.scaled(400,250, Qt.KeepAspectRatio)
    return Pic