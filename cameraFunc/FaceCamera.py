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

VOC_CLASSES = ("helmet", "head")
nnPath = "cameraFunc/models/yolox_nano_0_1_0_openvino_2021.4_6shave.blob"

def runFaceCamera(frame_queue:mp.Queue, command:mp.Value, alert:mp.Value, camera_id: str, status:mp.Value):
    try:
        # Start defining a pipeline
        pipeline = dai.Pipeline()

        print("Creating Color Camera...")
        cam = pipeline.createColorCamera()
        cam.setPreviewSize(1280, 720)
        cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        cam.setFps(10)
        cam.setInterleaved(False)
        cam.setBoardSocket(dai.CameraBoardSocket.RGB)
        cam_xout = pipeline.createXLinkOut()
        cam_xout.setStreamName("cam_out")
        cam.preview.link(cam_xout.input)

        # NeuralNetwork
        print(f"Creating {Path(nnPath).stem} Neural Network...")
        yoloDet_phone = pipeline.createNeuralNetwork()  # type: dai.node.NeuralNetwork
        yoloDet_phone.setBlobPath(str(nnPath))
        yoloDet_phone.setNumInferenceThreads(2)
        yolox_det_nn_xout_phone = pipeline.createXLinkOut()  # type: dai.node.XLinkOut
        yolox_det_nn_xout_phone.setStreamName("yolox_det_nn_phone")
        yoloDet_phone.out.link(yolox_det_nn_xout_phone.input)

        found, device_info = dai.Device.getDeviceByMxId("192.168.1.200")
        if not found:
            raise RuntimeError("device not found")
        print("prepare device")
        device = dai.Device(pipeline, device_info)
        cam_out = device.getOutputQueue("cam_out", 1, True)

        while True:
            frame = cam_out.get().getCvFrame()

            try:
                cv2.imshow('frame', frame)
            except:
                pass

            if cv2.waitKey(1) == ord('q'):
                break
    except Exception as e:
        print(f'front error: {e}')
    finally:
        print('end front')

if __name__ == "__main__":
    runFaceCamera()