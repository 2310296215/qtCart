from View import ViewWindow
from CameraWorker import CameraWorker
from tegraWorker import TegraWorker


class MainController:
    def __init__(self, view: ViewWindow) -> None:
        self.view = view

    def start(self):
        self.view.setup(self)
        self.view.show()

        self.tegraWorker = self.prepareTegra()
        self.tegraWorker.start()

        self.cameraWorker = self.prepareCameras()
        self.cameraWorker.start()

    def prepareTegra(self):
        tegra = TegraWorker()
        tegra.CpuUsage.connect(self.view.UpdateCpuUsage)
        tegra.GpuUsage.connect(self.view.UpdateGpuUsage)

        return tegra

    def prepareCameras(self):
        cameraWorker = CameraWorker()
        cameraWorker.finished.connect(self.view.setDefaultView)
        cameraWorker.LeftImage.connect(self.view.UpdateLeftSlot)
        cameraWorker.RightImage.connect(self.view.UpdateRightSlot)
        cameraWorker.FrontImage.connect(self.view.UpdateFrontSlot)

        cameraWorker.RightCameraStatus.connect(self.view.UpdateRightCameraStatus)
        cameraWorker.LeftCameraStatus.connect(self.view.UpdateLeftCameraStatus)
        cameraWorker.FrontCameraStatus.connect(self.view.UpdateFrontCameraStatus)
        cameraWorker.Alert.connect(self.view.runAlert)

        return cameraWorker

    def keyPress(self, key):
        print(f"keyPress: {key}")

        if key == 81:  # Q
            self.cameraWorker.stop()
            self.tegraWorker.stop()
        elif key == 87 and self.cameraWorker.ThreadActive:  # W
            self.cameraWorker.start()
            self.tegraWorker.start()
