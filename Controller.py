from View import ViewWindow
from CameraWorker import CameraWorker
from tegraWorker import TegraWorker


class MainController:
    def __init__(self, view: ViewWindow) -> None:
        self.view = view

    def start(self):
        self.view.setup(self)
        self.view.show()
        self.tegra = TegraWorker()
        self.tegra.CpuUsage.connect(self.view.UpdateCpuUsage)
        self.tegra.GpuUsage.connect(self.view.UpdateGpuUsage)
        self.tegra.start()        
        
        self.cameraWorker = CameraWorker()
        self.cameraWorker.finished.connect(self.view.setDefaultView)
        self.cameraWorker.LeftImage.connect(self.view.UpdateLeftSlot)
        self.cameraWorker.RightImage.connect(self.view.UpdateRightSlot)
        self.cameraWorker.FrontImage.connect(self.view.UpdateFrontSlot)

        self.cameraWorker.RightCameraStatus.connect(self.view.UpdateRightCameraStatus)
        self.cameraWorker.LeftCameraStatus.connect(self.view.UpdateLeftCameraStatus)
        self.cameraWorker.FrontCameraStatus.connect(self.view.UpdateFrontCameraStatus)
        self.cameraWorker.Alert.connect(self.view.runAlert)

        self.cameraWorker.start()

    def keyPress(self, key):
        print(f"keyPress: {key}")

        if key == 81:  # Q
            self.cameraWorker.stop()
            self.tegra.stop()
        elif key == 87 and self.cameraWorker.ThreadActive:  # W
            self.cameraWorker.start()
            self.tegra.start()

