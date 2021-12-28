from NewView import ViewWindow
from NewWorker import Worker


class MainController:
    def __init__(self, view: ViewWindow) -> None:
        self.view = view

    def start(self):
        self.view.setup(self)
        self.view.show()
        self.view.prepareWorker(Worker)
        self.view.Worker.start()

    def keyPress(self, key):
        print(f"keyPress: {key}")

        if key == 72:
            self.checkBoxCamLeft.setChecked(1)
        elif key == 71:
            self.checkBoxCamLeft.setChecked(0)

        if key == 81:  # Q
            self.Worker.stop()
        elif key == 87 and self.Worker.ThreadActive:  # W
            self.Worker.start()
