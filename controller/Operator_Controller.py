import json
import os
import time
import threading
import multiprocessing
import shutil

from controller.Battery_Controller import Battery_Controller
from controller.Memory_Controller import Memory_Controller
from controller.Cpu_Controller import Cpu_Controller


class Operator_Controller():
    def __init__(self,path):
        with open(path,"r") as f:
            self._json = json.load(f)

    def _check_connect_status(self,device_ip):
        main_devices = self._json["Command"]["status"] % device_ip
        op_1 = os.popen(main_devices)
        main_info = op_1.readline()
        op_1.close()
        main_status = True
        if "offline" in main_info or main_info == "":
            main_status = False
        return main_status

    def _bad_connect_handle(self):
        kill_server = self._json["Command"]["kill_server"]
        restart_server = self._json["Command"]["restart_server"]
        os.system(kill_server)
        os.system(restart_server)
        self._connect_devices()

    def _finish(self):
        self._json["Run_Control"] = False

    def factory(self, key):
        main_dir = self._json["Path"]["data_path"] % self._json["Test_Title"]
        branch_dir = self._json["Path"]["result_path"]["memory"] % self._json["Devices"][key][
            "name"]
        target_dir = os.path.join(main_dir, os.path.split(branch_dir)[0])
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        os.makedirs(target_dir)

        run_time = self._json["Run_Duration_Time"]
        timer = threading.Timer(run_time, self._finish)
        timer.start()
        cpuer = Cpu_Controller(self._json)
        battery_er = Battery_Controller(self._json)
        memory_er = Memory_Controller(self._json)
        cpu = threading.Thread(target=cpuer._get_cpu_data, args=(key, ))
        cpu.start()
        battery = threading.Thread(target=battery_er._get_battery_data, args=(key, ))
        battery.start()
        mem = threading.Thread(target=memory_er._get_mem_data, args=(key, ))
        mem.start()
        Polling_Time = (int)(self._json["Polling_Time"])
        while self._json["Run_Control"]:
            for key in self._json["Devices"].keys():
                device = self._json["Devices"][key]
                device_ip = device["ip"]
                connect_status = self._check_connect_status(device_ip)
                if not connect_status:
                    self._bad_connect_handle()
            time.sleep(Polling_Time)
        cpu.join()
        mem.join()
        battery.join()

    def _connect_devices(self):
        list_devices = self._json["Devices"]
        for key in list_devices.keys():
            connect_device = self._json["Command"]["connect"] % self._json["Devices"][key]["ip"]
            os.system(connect_device)

if __name__ == '__main__':
    config_path = "D:\workspace\python\AppPerf\config.json"
    with open(config_path, "r") as f:
        json_file = json.load(f)
    list_devices = json_file["Devices"]
    task = []
    operator = Operator_Controller(config_path)
    for key in list_devices.keys():
        p = multiprocessing.Process(target=operator.factory, args=(key, ))
        p.start()
        task.append(p)
    for t in task:
        t.join()



