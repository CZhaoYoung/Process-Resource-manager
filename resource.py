
class RRCB:
    """资源管理器"""
    def __init__(self, RID: str, units: int):
        self.RID = RID
        self.units_max = units  # 资源最大限额
        self.units_available = units  # 可用资源数量
        self.units_allocated = 0
        self.waiting_list = []
        self.allocated = dict() # 已经分配的列表

    def request(self, units: int, process: 'Process') -> bool:
        if units > self.units_max:
            raise ResourceError('ERROR: 请求超出了资源限额')

        if units <= 0:
            raise ResourceError('ERROR: 请求资源不能为空或者负')

        if self.RID in process.resources:
            if process.resources[self.RID] + units > self.units_max:
                raise ResourceError("ERROR: Units requested would allow process to have more than the existing units")

        if units <= self.units_available:
            self.units_allocated += units
            self.units_available -= units
            self.allocated[process] = units
            return True
        else:
            self.waiting_list.append((process, units))
            return False

    def release(self, units: int, process: 'Process'):

        if self.allocated[process] < units:
            raise ResourceError("ERROR: cannot release more units than held")

        if units <= 0:
            raise ResourceError("ERROR: cannot release 0/negative units")

        self.units_available += units
        self.units_allocated -= units

        self.allocated[process] -= units
        if self.allocated[process] == 0:
            self.allocated.pop(process, None)

    def status(self) -> bool:
        return self.units_available > 0


class ResourceTable():
        _instance = None
        table = dict()

        for i in range(1, 5):
            id = "R" + str(i)
            table[id] = RRCB(id, i)

        def __init__(self):
            self.table = ResourceTable.table


class ResourceError(Exception):
        pass

