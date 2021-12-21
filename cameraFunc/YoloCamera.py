#!/usr/bin/env python3
import cv2
import depthai as dai
import numpy as np
from datetime import datetime
import queue
import yaml
import multiprocessing as mp
import yaml

from factories import AlertFactory

with open('config.yml', 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

'''
Spatial Tiny-yolo example
  Performs inference on RGB camera and retrieves spatial location coordinates: x,y,z relative to the center of depth map.
  Can be used for tiny-yolo-v3 or tiny-yolo-v4 networks
'''


def runCamera(frame_queue, command, alert, camera_id):
    nnBlobPath = 'cameraFunc/models/yolo-v4-tiny-tf_openvino_2021.4_6shave.blob'

    with open('config.yml', 'r') as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)

    # Tiny yolo v3/4 label texts
    labelMap = [
        "person",         "bicycle",    "car",           "motorbike",     "aeroplane",   "bus",           "train",
        "truck",          "boat",       "traffic light", "fire hydrant",  "stop sign",   "parking meter", "bench",
        "bird",           "cat",        "dog",           "horse",         "sheep",       "cow",           "elephant",
        "bear",           "zebra",      "giraffe",       "backpack",      "umbrella",    "handbag",       "tie",
        "suitcase",       "frisbee",    "skis",          "snowboard",     "sports ball", "kite",          "baseball bat",
        "baseball glove", "skateboard", "surfboard",     "tennis racket", "bottle",      "wine glass",    "cup",
        "fork",           "knife",      "spoon",         "bowl",          "banana",      "apple",         "sandwich",
        "orange",         "broccoli",   "carrot",        "hot dog",       "pizza",       "donut",         "cake",
        "chair",          "sofa",       "pottedplant",   "bed",           "diningtable", "toilet",        "tvmonitor",
        "laptop",         "mouse",      "remote",        "keyboard",      "cell phone",  "microwave",     "oven",
        "toaster",        "sink",       "refrigerator",  "book",          "clock",       "vase",          "scissors",
        "teddy bear",     "hair drier", "toothbrush"
    ]

    # Create pipeline
    pipeline = dai.Pipeline()

    # Define sources and outputs
    camRgb = pipeline.createColorCamera()
    spatialDetectionNetwork = pipeline.createYoloSpatialDetectionNetwork()
    monoLeft = pipeline.createMonoCamera()
    monoRight = pipeline.createMonoCamera()
    stereo = pipeline.createStereoDepth()
    manip = pipeline.createImageManip()

    xoutRgb = pipeline.createXLinkOut()
    xoutNN = pipeline.createXLinkOut()
    xoutBoundingBoxDepthMapping = pipeline.createXLinkOut()
    xoutDepth = pipeline.createXLinkOut()
    manipOut = pipeline.createXLinkOut()

    xoutRgb.setStreamName("rgb")
    xoutNN.setStreamName("detections")
    xoutBoundingBoxDepthMapping.setStreamName("boundingBoxDepthMapping")
    xoutDepth.setStreamName("depth")
    manipOut.setStreamName("manip")

    # Properties
    camRgb.setPreviewSize(1080, 720)
    camRgb.setPreviewKeepAspectRatio(True)
    camRgb.setFps(10)
    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    camRgb.setInterleaved(False)
    camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

    monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
    monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)


    manip.initialConfig.setResizeThumbnail(416, 416)
    manip.initialConfig.setFrameType(dai.ImgFrame.Type.BGR888p)
    manip.inputImage.setBlocking(False)

    # setting node configs
    stereo.initialConfig.setConfidenceThreshold(255)

    spatialDetectionNetwork.setBlobPath(nnBlobPath)
    spatialDetectionNetwork.setConfidenceThreshold(0.5)
    spatialDetectionNetwork.input.setBlocking(False)
    spatialDetectionNetwork.setBoundingBoxScaleFactor(0.5)
    spatialDetectionNetwork.setDepthLowerThreshold(100)
    spatialDetectionNetwork.setDepthUpperThreshold(5000)

    # Yolo specific parameters
    spatialDetectionNetwork.setNumClasses(80)
    spatialDetectionNetwork.setCoordinateSize(4)
    spatialDetectionNetwork.setAnchors(np.array([10,14, 23,27, 37,58, 81,82, 135,169, 344,319]))
    spatialDetectionNetwork.setAnchorMasks({ "side26": np.array([1,2,3]), "side13": np.array([3,4,5]) })
    spatialDetectionNetwork.setIouThreshold(0.5)

    # Linking
    monoLeft.out.link(stereo.left)
    monoRight.out.link(stereo.right)

    camRgb.preview.link(manip.inputImage)
    manip.out.link(spatialDetectionNetwork.input)
    spatialDetectionNetwork.passthrough.link(xoutRgb.input)
    spatialDetectionNetwork.out.link(xoutNN.input)
    spatialDetectionNetwork.boundingBoxMapping.link(xoutBoundingBoxDepthMapping.input)

    stereo.depth.link(spatialDetectionNetwork.inputDepth)
    spatialDetectionNetwork.passthroughDepth.link(xoutDepth.input)

    found, device_info = dai.Device.getDeviceByMxId(camera_id)
    if not found:
        raise RuntimeError("device not found")
    device = dai.Device(pipeline, device_info)

    # Output queues will be used to get the rgb frames and nn data from the outputs defined above
    previewQueue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    detectionNNQueue = device.getOutputQueue(name="detections", maxSize=4, blocking=False)
    xoutBoundingBoxDepthMappingQueue = device.getOutputQueue(name="boundingBoxDepthMapping", maxSize=4, blocking=False)
    depthQueue = device.getOutputQueue(name="depth", maxSize=4, blocking=False)

    counter = 0
    color = (255, 255, 255)

    video_index = 1
    t1 = datetime.now()
    t2 = t1
    fileName = f"videos/cam_{camera_id}_{video_index}.avi"
    video_code = cv2.VideoWriter_fourcc(*'XVID')
    frameRate = 20
    resolution = (1280, 720)
    videoOutput = cv2.VideoWriter(fileName, video_code, frameRate, resolution)

    while command.value != 0:
        inPreview = previewQueue.get()
        inDet = detectionNNQueue.get()
        depth = depthQueue.get()

        frame = inPreview.getCvFrame()

        counter+=1
        detections = inDet.detections

        # If the frame is available, draw bounding boxes on it and show the frame
        height = frame.shape[0]
        width  = frame.shape[1]

        for detection in detections:
            # Denormalize bounding box
            x1 = int(detection.xmin * width)
            x2 = int(detection.xmax * width)
            y1 = int(detection.ymin * height)
            y2 = int(detection.ymax * height)
            try:
                label = labelMap[detection.label]
            except:
                label = detection.label

            if label != 'person':
                continue

            person_distance = int(detection.spatialCoordinates.z)

            cv2.putText(frame, str(label), (x1 + 10, y1 + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
            cv2.putText(frame, "{:.2f}".format(detection.confidence*100), (x1 + 10, y1 + 35), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
            cv2.putText(frame, f"X: {int(detection.spatialCoordinates.x)} mm", (x1 + 10, y1 + 50), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
            cv2.putText(frame, f"Y: {int(detection.spatialCoordinates.y)} mm", (x1 + 10, y1 + 65), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
            cv2.putText(frame, f"Z: {int(detection.spatialCoordinates.z)} mm", (x1 + 10, y1 + 80), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, cv2.FONT_HERSHEY_SIMPLEX)

            if alert.value != AlertFactory.AlertIndex_None:
                continue

            if person_distance < config["RED_ALERT_DISTANCE"]:
                alert.value = AlertFactory.AlertIndex_PedestrianFront
            elif person_distance < config["YELLOW_ALERT_DISTANCE"]:
                alert.value = AlertFactory.AlertIndex_PedestrianFront

        # crop black out of image
        frame = frame[91:325, 0:416]

        if config["PRODUCTION"] is True:
            frame = cv2.resize(frame, (config["MainImage_Width"], config["MainImage_Height"]), interpolation=cv2.INTER_LINEAR)

        t2 = datetime.now()
        if (t2 - t1).seconds >= 60:
            videoOutput.release()
            video_index += 1
            # 每30分鐘洗白重來
            video_index = video_index % 10
            fileName = f"videos/cam_{camera_id}_{video_index}.avi"
            videoOutput = cv2.VideoWriter(fileName, video_code, frameRate, resolution)
            t1 = t2
        videoOutput.write(frame)
        try:
            frame_queue.put_nowait(frame)
        except queue.Full:
            pass

        videoOutput.release()

def main():
    frame_queue = mp.Queue(4)
    command = mp.Value('i', 1)
    alert = mp.Value('i', 99)
    camera_id = config["FRONT_CAMERA_ID"]
    print(camera_id)

    proccess = mp.Process(target=runCamera, args=(frame_queue, command, alert, camera_id, ))
    proccess.start()

    while True:
        try:
            frame = frame_queue.get_nowait()
            cv2.imshow('frame', frame)
        except queue.Empty or queue.Full:
            pass

        if alert.value != AlertFactory.AlertIndex_None:
            print(AlertFactory.AlertList[alert.value])

        if cv2.waitKey(1) == ord('q'):
            command.value = 0
            break

    proccess.kill()

if __name__ == '__main__':
    main()