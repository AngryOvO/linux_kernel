import time
import os
import psutil
import dis


def check_cpu_memory():

    pid = os.getpid()
    py = psutil.Process(pid)

    memory_usage = round(py.memory_info()[0] / 2.**30, 2)
    print("memory usage :", memory_usage, "%")

def memory_allocation():

    print("Python_memory_allocation")
    print("data type: list")
    print("data size: 100000000")

    starttime = time.time()

    y = []
    for i in range(100000000):
        y.append(i)

    endtime = time.time()
    print("process time :", endtime - starttime)

    check_cpu_memory()

if __name__ == "__main__":

    dis.dis(memory_allocation)


