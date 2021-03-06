import cv2
import queue
from datetime import datetime
import multiprocessing as mp
import yaml
from factories.AlertFactory import AlertEnum

with open('config.yml', 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)


def runCamera(frame_queue: mp.Queue, command: mp.Value, alert: mp.Value, camera_id: str, status: mp.Value):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    # t = datetime.now()

    try:
        while command.value != 0:
            status.value = 1
            ret, frame = cap.read()

            # if(datetime.now() - t).seconds >= 10:
            #     raise RuntimeError("Errrrrr")

            if frame is not None:
                # frame = cv2.resize(frame, (config["MainImage_Width"], config["MainImage_Height"]), interpolation=cv2.INTER_LINEAR)
                try:
                    frame_queue.put_nowait(frame)
                except queue.Full:
                    pass

            alert.value = int(AlertEnum.NoHelmet)
    except Exception as e:
        print(e)

    finally:
        cap.release()
        status.value = 0
        while not frame_queue.empty():
            frame_queue.get_nowait()
        frame_queue.close()
