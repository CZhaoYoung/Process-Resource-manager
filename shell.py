from process import *
from resource import ResourceError
from scheduler import *

ReadyList = []
RunningList = []

class Shell:
    def __init__(self, input_path: str = None, output_path: str = None):
        self.__run(input_path, output_path)

    def _validate_command(self, command: list):
        command_argc = {"init": 1,  # initialize
                        "cr": 3,    # create process
                        "de": 2,    # delete process
                        "req": 3,   # request process
                        "rel": 3,   # release process
                        "to": 1,    # time out
                        "ps": 1,    # process status
                        "rl": 1,   # ready_list
                        "bl": 1,    # list blocked
                        "lu": 1,}      # list running list

        argc = len(command)
        if argc < 1:
            raise CommandError("ERROR: 没有指定参数")

        if len(command) == 1 and command[0] == "quit":
            raise QuitError

        if command[0] not in command_argc:
            raise ShellError("ERROR: 没有此命令")

        if argc != command_argc[command[0]]:
            raise ShellError("ERROR: 非法的参数")

    def _execute_command(self, command: list):
        commands = {"init": "Shell.init",
                    "cr": "Shell.create_process",
                    "de": "Shell.destroy_process",
                    "req": "Shell.request_resource",
                    "rel": "Shell.release_resource",
                    "to": "Shell.timeout",
                    "ps": "Shell.process_status",
                    "rl": "Shell.ready_list",
                    "bl": "Shell.blocked_list",
                    "lu": "Shell.list_running_process",}

        cmd = commands[command[0]]
        param_string = ""
        if (len(command[1:])):
            param_string = ", '" + "', '".join(command[1:]) + "'"

        exec(cmd + "(self" + param_string + ")")

        if(command[0] in ["init", "cr", "de", "req", "rel", "to"]):
            scheduler()

    def init(self):
        for child in self.init.tree.children:
            child.kill()

        PCB.CurrentProcess = self.init

    def create_process(self, PID: str, priority: str):
        priority = int(priority)

        if priority not in [0,1,2]:
            raise ProcessError("Priority must be 0, 1, or 2")

        PCB.CurrentProcess.child_process(PID, priority)
        ReadyList.append(PID)

    def destroy_process(self, PID: str):
        if PID not in ProcessTable.table:
            raise ProcessError("ERROR: Process " + PID + " 不存在")

        process = ProcessTable.table[PID]

        if process.priority == 0:
            raise ProcessError("ERROR: 不能删除此进程")

        if not PCB.CurrentProcess.has_child(process):
            raise ProcessError("ERROR: Process " + PID + " is not the current process nor a descendant of it")

        ProcessTable.table[PID].kill()
        ReadyList.remove(PID)

    def request_resource(self, RID: str, units: str):
        units = int(units)
        PCB.CurrentProcess.request(RID, units)
        print("process " + PCB.CurrentProcess.PID +" requests "+ str(units)+ " " +RID )

    def release_resource(self, RID: str, units: str):
        units = int(units)
        PCB.CurrentProcess.release(RID, units)

# 时间片切换，实现调度
    def timeout(self):
        PCB.CurrentProcess.timeout()

    def process_status(self):
        print("process status"+PCB.status)

    def ready_list(self):
        if List.BlockedList:
            for i in List.BlockedList:
                ReadyList.remove(i)
                print("Ready List" + str((ReadyList)))
        else:
            print("Ready List" + str(ReadyList))
    def blocked_list(self):
        print("Blocked list" + str(List.BlockedList))


# 列出正在运行的进程
    def list_running_process(self):
        print(" The running process is " + PCB.CurrentProcess.PID)

# 列出阻塞进程
    def list_blocked_process(self):
        print(PCB.CurrentProcess.request)

    def __process_command(self, command):
        try:
            self._validate_command(command)
            self._execute_command(command)
            return PCB.CurrentProcess.PID
        except QuitError:
            return
        except CommandError:
            return "\n"
        except (ShellError, ResourceError, ProcessError) as e:
            print("*", e)
            return "error"

    def __run(self, input_path, output_path):

        self.init = PCB("init", 0)
        scheduler()

        if input_path is None:
            while (True):
                print("> ", end="")
                command_line = input()
                command = command_line.split()
                self.__process_command(command)
        else:
            output_list = []
            with open(input_path, mode="r") as in_file:
                line = ["init"]
                for command_line in in_file:
                    if command_line.strip() == '':
                        to_append = " ".join(line)
                        if to_append.strip() != '':
                            output_list.append(to_append)
                        line = []
                    else:
                        result = self.__process_command(command_line.split())
                        line.append(result)

                if len(line):
                    output_list.append(" ".join(line))

            output_str = "\n".join(output_list)
            if output_path is not None:
                with open(output_path, mode="w") as out_file:
                    out_file.write(output_str)
            else:
                print(output_str)


class ShellError(Exception):
    pass


class CommandError(Exception):
    pass


class QuitError(Exception):
    pass