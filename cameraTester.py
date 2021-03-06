import cv2
import multiprocessing as mp
import yaml
import time
from sys import platform
from cameraFunc import YoloCamera, CombinedCamera, TestCamera, RgbCamera
import queue

with open('config.yml', 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

def main():
    frame_queue = mp.Queue(4)
    command = mp.Value('i', 1)
    alert = mp.Value('i', 0)
    status = mp.Value('i', 0)
    camera_id = config["LEFT_CAMERA_ID"]

    # camera_id = config["LEFT_CAMERA_ID"]
    # CameraProcess = YoloCamera.runCamera
    # CameraProcess = CombinedCamera.runCamera
    CameraProcess = RgbCamera.runCamera

    command.value = 1
    proccess = mp.Process(
        target=CameraProcess,
        args=(frame_queue, command, alert, camera_id,status,)
        )
    proccess.start()

    while command.value == 1:
        try:
            frame = frame_queue.get_nowait()
            cv2.imshow('frame', frame)
        except queue.Empty or queue.Full:
            pass

        if cv2.waitKey(1) == ord('q'):
            command.value = 0

    proccess.terminate()


if __name__ == '__main__':
    main()
