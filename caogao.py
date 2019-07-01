for i in range(2, -1 ,-1 ):
    print(i)


    # 初始化进程
    def initialize(self):
        pcb_info = "PID:"+str(self.Pid) + ' ' + "Status:"+ str(self.Status) + \
                   ' ' + "Priority:"+str(self.Priority) + ' ' + "Runtime:"+str(self.Runtime)
        print("A process have initialized")
        return pcb_info

    # 销毁进程
    def destroy(self):
        self.Status = "killed"
        self.CPU_req = 0
        self.IO_req = 0
        # 从队列中消失

    # 请求资源
    def request():
        pass
    #   if self.CPU_req>CPU_sou||self.IO_req>IO_sou:
    #     #      self.status = "blocked" #被阻塞，进入阻塞队列
    #   else
            # 分配资源，进入执行队列

    # 释放资源,进程正常结束
    def release(self):
        self.IO_req = 0
        self.CPU_req = 0
        self.Status = "finished"
    # wakeup 从阻塞到就绪
    def wakeup(self):
        self.Status = "ready"
        #加入到就绪队列中
    # timeout 从执行到就绪
    def timeout(self):
        self.Status = "ready"