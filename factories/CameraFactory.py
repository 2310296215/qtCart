from cameraFunc import YoloCamera, FatigueCam, PedestrianCamera, CombinedCamera, TestCamera

TextTestCamera= "TestCamera"
TextYoloCamera = 'YoloCamera'
TextPedestrianCamera = 'PedestrianCamera'
TextFatigueCamera = 'FatigueCamera'
TextCombinedCamera = 'CombinedCamera'

def CameraFactory(CameraIndex):
    CameraDict = {
        TextTestCamera: TestCamera.runCamera,
        TextFatigueCamera: FatigueCam.runFatigueCam,
        TextYoloCamera: YoloCamera.runCamera,
        TextPedestrianCamera: PedestrianCamera.runPedestrianCamera,
        TextCombinedCamera: CombinedCamera.runCamera
    }

    return CameraDict[CameraIndex]