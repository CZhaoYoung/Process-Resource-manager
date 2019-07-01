from resource import *


class ProcessPriority:
    def __init__(self):
        self.PPL = [[], [],[]];  # "PPL,ProcessPrioriryList,has three sub-list stand for 3 priority level represented by index."

    # 添加优先级
    def append(self, process: 'PCB'):
        if process not in self.PPL[process.priority]:
            self.PPL[process.priority].append(process)

    # 移除优先级
    def remove(self, process: 'PCB'):
        if process in self.PPL[process.priority]:
            self.PPL[process.priority].remove(process)

    # 查找最高优先级
    def find_priority(self) -> 'PCB':
        for i in range(2, -1, -1):  # i= 2 1 0
            if (len(self.PPL[i]) > 0):
                return self.PPL[i][0]

    def __getitem__(self, index: int):
        return self.PPL[index]

    def __setitem__(self, key, value):
        self.PPL[key] = value

    def __contains__(self, process):
        return process in self.PPL[process.priority]


class PCB:
    INIT, USER, SYSTEM = 0, 1, 2
    PriorityMap = {0: "INIT", 1: "USER", 2: "SYSTEM"}

    ReadyList = ProcessPriority()  # 就绪队列

    CurrentProcess = None

    def __init__(self, PID: str, priority: int, parent: 'PCB' = None):
        self.PID = PID # 标识号
        self.priority = priority # 优先级
        self.tree = CreationTree(parent) #父子进程树
        self.status = Status(Status.READY) # 进程状态
        self.resources = dict() # 进程资源列表

        self.pending_request = None

        ProcessTable.table[PID] = self
        PCB.ReadyList[priority].append(self) # 就绪队列

    def child_process(self, PID: str, priority: int) -> 'PCB':
        # 判断进程是否存在
        if PID in ProcessTable.table:
            raise ProcessError("ERROR: Process " + PID + " already exists!")
        # 判断优先级是否为0，判断init 进程
        if priority == 0:
            raise ProcessError("ERROR: there can only be one init process")

        child_process = PCB(PID, priority, self)
        self.tree.add_child(child_process)
        return child_process

    def kill(self):
        while len(self.tree.children) > 0:
            child = self.tree.children[0]
            child.kill()

        self._free()

        if self.status.type == Status.BLOCKED:
            self.status.list.remove(self.pending_request)
        else:
            self.status.list.remove(self)

        self.tree.parent.tree.children.remove(self)

        ProcessTable.table.pop(self.PID, None)
        if (self == PCB.CurrentProcess):
            PCB.CurrentProcess = None

    def timeout(self):
        self.status.type = Status.READY
        ready_list_ref = PCB.ReadyList
        PCB.ReadyList[self.priority] = ready_list_ref[self.priority][1:] + \
                                       ready_list_ref[self.priority][0:1]

    def request(self, RID: str, units: int):

        if self.priority == 0:
            raise ProcessError("ERROR: init process cannot request resources")

        resource = ResourceTable.table[RID]
        # 请求资源
        success = resource.request(units, self)

        if success:
            self.status.type = Status.READY
            self.status.list = PCB.ReadyList
            self.resources[RID] = units
            PCB.ReadyList.append(self)
        else:
            self.status.type = Status.BLOCKED
            self.pending_request = (self, units)
            self.status.list = resource.waiting_list
            PCB.ReadyList.remove(self)

    def release(self, RID: str, units: int):
        if RID not in self.resources:
            raise ProcessError("ERROR: process " + self.PID + " does not hold resource " + RID)

        resource = ResourceTable.table[RID]
        resource.release(units, self)
        self.resources[RID] -= units
        if self.resources[RID] == 0:
            self.resources.pop(RID, None)

        while (len(resource.waiting_list) and
               resource.waiting_list[0][1] <= resource.units_available):
            blocked_request = resource.waiting_list.pop(0)
            requesting_process = blocked_request[0]
            requested_units = blocked_request[1]

            requesting_process.status.type = Status.READY
            requesting_process.status.list = PCB.ReadyList
            PCB.ReadyList.append(requesting_process)
            requesting_process.request(resource.RID, requested_units)

    def has_child(self, process):
        if process == PCB.CurrentProcess:
            return True

        for child in self.tree.children:
            if child.PID == process.PID:
                return True
            if child.has_child(process):
                return True
        return False

    def _free(self):
        resources = list(self.resources.items())

        while len(resources):
            to_release = resources.pop(0)
            rid = to_release[0]
            units = to_release[1]
            self.release(rid, units)


class CreationTree:
    def __init__(self, parent: PCB):
        self.parent = parent
        self.children = []

    def add_child(self, process: PCB):
        if not isinstance(process, PCB): # 判断process是否符合PCB规范
            raise TypeError("Process must be of type ProcessControlBlock")
        self.children.append(process)


class Status:
    RUNNING, READY, BLOCKED = 0, 1, 2
    TypeMap = {0: "RUNNING", 1: "READY", 2: "BLOCKED"}

    def __init__(self, type: int, list: list = PCB.ReadyList):
        self.type = type
        self.list = list


class ProcessTable():
    _instance = None
    table = dict()

    def __init__(self):
        self.table = ProcessTable.table


class ProcessError(Exception):
    pass


