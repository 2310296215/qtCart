from PyQt5.QtCore import QThread, pyqtSignal

import subprocess
from sys import platform


class TegraWorker(QThread):

    CpuUsage = pyqtSignal(str)
    GpuUsage = pyqtSignal(str)

    def run(self):

        if not platform == "linux":
            return

        cmd = "tegrastats"
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        self.running = True
        try:
            while self.running:
                result = self.process.stdout.readline().decode().strip()
                data = result.split(" ")

                cpus = data[9].replace("[", "").replace("]", "")
                cpu_usage = 0
                for cpu in cpus.split(","):
                    c = cpu.split("@")[0].replace("%", "")
                    cpu_usage += int(c)
                cpu_usage = f"{(cpu_usage / 6):.2f}"
                gpu_usage = data[13].replace("%", "")

                self.CpuUsage.emit(cpu_usage)
                self.GpuUsage.emit(gpu_usage)

        except Exception as e:
            print(f"tegra error: {e}")
        finally:
            self.process.terminate()

    def stop(self):
        self.running = False
