
'''
import os
from io import StringIO

import pandas as pd

process_info_file = os.popen("wmic process get ExecutablePath,Name,ProcessId")
#print(process_info_file.read())
process_info = StringIO(process_info_file.read())

process_info_file.close()
#ddd
process_info_df = pd.read_csv(process_info,sep="\s{2,}")
process_info_df.columns=["ExecutablePath","Name","PID"]

netstat_info_file =os.popen("nestat -ano")
'''
import psutil
import pandas as pd

# 获取全部进程信息
def processInfo():
    """
    获取全部进程信息
    :return: list
    """

    # 定义一个获取进程属性的方法
    def getProperty(process, pro: str):
        try:
            ret = eval('process.' + pro)()
        except Exception as e:
            return ''
        return ret

    pids = psutil.pids()

    output = {}
    for pid in pids:
        process = psutil.Process(pid)
        parent = getProperty(process, 'parent')
        if parent is str or parent is None:
            parentName = ''
        else:
            parentName = parent.name()
        output[pid] = {
            '进程编号': pid,
            '进程名称': process.name(),
            '执行路径': getProperty(process, 'exe'),
            '当前路径': getProperty(process, 'cwd'),
            '启动命令': getProperty(process, 'cmdline'),
            '父进程ID': process.ppid(),
            '父进程': parentName,
            '状态': process.status(),
            '进程用户名': getProperty(process, 'username'),
            '进程创建时间': process.create_time(),
            '终端': getProperty(process, 'terminal'),
            '执行时间': process.cpu_times(),
            '内存信息': process.memory_info(),
            '打开的文件': getProperty(process, 'open_files'),
            '相关网络连接': process.connections(),
            '线程数': process.num_threads(),
            '线程': getProperty(process, 'threads'),
            '环境变量': getProperty(process, 'environ'),
        }
    return output

df = pd.DataFrame(processInfo()).T

df.to_csv("process.csv")
