from resource import *
from process import *


class List():

    BlockedList = []
    ReadyList = []
    RunningList = {}

# 抢占式调度
def _preempt(process: PCB):
    prev_process = PCB.CurrentProcess
    # 判断正在执行的进程状态
    # 将进程的状态置为就绪
    if prev_process is not None and prev_process.status.type == Status.RUNNING:
            prev_process.status.type = Status.READY

    process.status.type = Status.RUNNING
    output = "* "
    current = PCB.CurrentProcess

    if current is not None and current.status.type == Status.BLOCKED:
        output += "Process " + current.PID + " is blocked; "
        List.BlockedList.append(current.PID)
        # List.RunningList = process.PID
    output += "Process " + process.PID + " is running"
    # List.RunningList = process.PID
    PCB.CurrentProcess = process
    print(output)


# 判断进程的优先级
def scheduler():
    process = PCB.ReadyList.find_priority()
    if (PCB.CurrentProcess is None or
        PCB.CurrentProcess.priority < process.priority or
        PCB.CurrentProcess.status.type != Status.RUNNING):
        # 抢占当前进程
        _preempt(process)