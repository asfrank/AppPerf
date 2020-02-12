import os
import time
import shutil
import csv
import threading
from datetime import datetime

class Cpu_Controller():
    def __init__(self,json):
        self._json = json



    def _get_cpu_data(self, key):
        print("设备"+key+"开始采集cpu数据")
        print(threading.current_thread())
        while self._json["Run_Control"]:
            list_devices = self._json["Devices"]
            path = self._get_path(key)
            device_ip = list_devices[key]["ip"]
            cpu_info_total_first, cpu_info_process_first = self._cpu_data_snapshoot(device_ip, key)
            cpu_info_total_second, cpu_info_process_second = self._cpu_data_snapshoot(device_ip, key)

            if cpu_info_total_first != -1 and cpu_info_process_first != -1 and cpu_info_total_second != -1 and cpu_info_process_second != -1:
                cpu_info = 100 * (cpu_info_process_second - cpu_info_process_first) / (
                        cpu_info_total_second - cpu_info_total_first)
                cpu_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')
                with open(path, "a+") as f:
                    csv_write = csv.writer(f)
                    data_row = [cpu_time, cpu_info]
                    csv_write.writerow(data_row)

            sleep_time = (int)(self._json["CPU_Time"])
            time.sleep(sleep_time)
        print("设备" + key + "cpu采集结束...")

    def _cpu_data_snapshoot(self, device_ip, device_key):
        cpu_info_total_first = -1
        cpu_info_process_first = -1
        command_total = self._json["Command"]["CPU_Command_Total"] % device_ip
        try:
            cpu_get_total_first = os.popen(command_total)
            pid = self._get_pid(device_ip, device_key)
            command_process = self._json["Command"]["CPU_Command_Process"] % (device_ip, pid)
            cpu_get_process_first = os.popen(command_process)
        except Exception as e:
            time.sleep(5)
            return cpu_info_total_first, cpu_info_process_first


        cpu_info_total_list = cpu_get_total_first.read().split()
        cpu_info_process_list = cpu_get_process_first.read().split()
        cpu_get_total_first.close()
        cpu_get_process_first.close()

        for i in range(7):
            cpu_info_total_first += (int)(cpu_info_total_list[i + 2])
        for i in range(4):
            cpu_info_process_first += (int)(cpu_info_process_list[i + 13])

        return cpu_info_total_first, cpu_info_process_first

    def _get_pid(self, device_ip, device_key):
        cmd = self._json["Command"]["Pid_Command"] % (device_ip, self._json["Devices"][device_key]["Application_Under_test"])
        pid_info = os.popen(cmd)
        pid = pid_info.read().split()[1]
        pid_info.close()
        return pid

    def _get_path(self,key):
        main_dir = self._json["Path"]["data_path"] % self._json["Test_Title"]
        branch_dir = self._json["Path"]["result_path"]["cpu"] % self._json["Devices"][key]["name"]
        path = os.path.join(main_dir, branch_dir)
        return path
