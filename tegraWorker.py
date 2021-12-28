from PyQt5.QtCore import QThread, pyqtSignal

from jtop import jtop
import subprocess

class TegraWorker(QThread):

    CpuUsage = pyqtSignal(str)
    GpuUsage = pyqtSignal(str)
    def run(self):

        cmd = f"tegrastats"
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        self.running = True
        try:
            while self.running:
                x = self.process.stdout.readline().decode().strip()
                data = x.split(" ")
                
                cpus = data[9].replace("[", "").replace("]", "")
                cpu_usage = 0
                for cpu in cpus.split(","):
                    c = cpu.split("@")[0].replace("%","")
                    cpu_usage += int(c)
                cpu_usage = f"{(cpu_usage / 6):.2f}"
                gpu_usage = data[13].replace("%", "")

                self.CpuUsage.emit(cpu_usage)
                self.GpuUsage.emit(gpu_usage)
                
        
        except Exception as e:
            print(e)
        finally:
            print("END")
            self.process.kill()

    def stop(self):
        print("stop")
        self.running = False