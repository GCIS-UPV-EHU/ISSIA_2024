import psutil
import time


def cpu_ram():
    while True:
        cpu = psutil.cpu_percent(interval=5)
        ram = psutil.virtual_memory().percent
        print("CPU: %" + str(cpu) + "\tRAM: %" + str(ram))


if __name__ == "__main__":
    cpu_ram()

