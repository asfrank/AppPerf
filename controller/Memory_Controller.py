import os
import time
import shutil
import csv
import threading
import re
from datetime import datetime


class Memory_Controller():
    def __init__(self,json):
        self._json = json


    def _get_mem_data(self, key):
        print("设备"+key+"开始采集mem数据")
        print(threading.current_thread())
        while self._json["Run_Control"]:
            list_devices = self._json["Devices"]
            path = self._get_path(key)
            device_ip = list_devices[key]["ip"]
            memory_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')
            Native, Dalvik, TOTAL = self._mem_data_snapshoot(device_ip, key)

            if Native != -1 and Dalvik != -1 and TOTAL != -1:
                with open(path, "a+") as f:
                    csv_write = csv.writer(f)
                    data_row = [memory_time, Native, Dalvik, TOTAL]
                    csv_write.writerow(data_row)

            sleep_time = (int)(self._json["Memory_Time"])
            time.sleep(sleep_time)
        print("设备" + key + "内存采集结束...")

    def _mem_data_snapshoot(self,device_ip, device_key):
        Native = -1
        Dalvik = -1
        TOTAL = -1
        app = self._json["Devices"][device_key]["Application_Under_test"]
        command = self._json["Command"]["Memory_Command"] % (device_ip, app)
        try:
            mem = os.popen(command)
        except Exception as e:
            time.sleep(5)
            return Native, Dalvik, TOTAL
        for line in mem.readlines():
            str_list = re.split("\\s+", line)
            if "Native" in str_list and "Heap" in str_list:
                Native = str_list[3]
            elif "Dalvik" in str_list and "Heap" in str_list:
                Dalvik = str_list[3]
            elif "TOTAL" in str_list:
                TOTAL = str_list[2]
        mem.close()
        return Native, Dalvik, TOTAL

    def _get_path(self,key):
        main_dir = self._json["Path"]["data_path"] % self._json["Test_Title"]
        branch_dir = self._json["Path"]["result_path"]["memory"] % self._json["Devices"][key]["name"]
        path = os.path.join(main_dir, branch_dir)
        return path

