from pathlib import Path
import multiprocessing as mp
import cv2
import depthai as dai
import numpy as np
import queue
import yaml
from factories import AlertFactory

with open('config.yml', 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

def runCamera(camera_id):
    print(dai.Device.getAllAvailableDevices())
    pipeline = dai.Pipeline()

    cam = pipeline.createColorCamera()
    cam.setPreviewSize(config["MainImage_Width"], config["MainImage_Height"])
    cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    cam.setFps(10)
    cam.setInterleaved(False)
    cam.setBoardSocket(dai.CameraBoardSocket.RGB)
    cam_xout = pipeline.createXLinkOut()
    cam_xout.setStreamName("cam_out")
    cam.preview.link(cam_xout.input)

    found, device_info = dai.Device.getDeviceByMxId(camera_id)
    if not found:
        raise RuntimeError("device not found")

    device = dai.Device(pipeline, device_info)
    print("Starting pipeline...")
    cam_out = device.getOutputQueue("cam_out", 1, True)

    while True:
        in_rgb = cam_out.tryGet()
        if in_rgb is not None:
            frame = in_rgb.getCvFrame()

            cv2.imshow("frame", frame)

            if cv2.waitKey(1) == ord('q'):
                break

        # i += 1
        # img_id = i % 2 + 1
        # frame = cv2.imread(f'test_img/{img_id}.jpg')
        # frame = cv2.resize(frame, (400,250))
        # q.put_nowait(frame)
        # time.sleep(0.1)


if __name__ == '__main__':
    runCamera(config["RIGHT_CAMERA_ID"])