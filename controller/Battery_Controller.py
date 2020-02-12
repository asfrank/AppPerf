import os
import time
import csv
import threading
import re
from datetime import datetime


class Battery_Controller():
    def __init__(self,json):
        self._json = json
        list_devices = self._json["Devices"]
        for key in list_devices.keys():
            device_ip = list_devices[key]["ip"]
            reset_battery = self._json["Command"]["reset_battery"] % device_ip
            start_to_collect = self._json["Command"]["start_to_collect"] % device_ip
            os.system(reset_battery)
            os.system(start_to_collect)




    def _get_battery_data(self, key):
        print("设备"+key+"开始采集电量数据")
        print(threading.current_thread())
        i = 1
        while self._json["Run_Control"]:
            list_devices = self._json["Devices"]
            path = self._get_path(key)
            device_ip = list_devices[key]["ip"]
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')
            result_data = self._battery_data_snapshoot(device_ip)

            if result_data != -1:
                with open(path, "a+") as f:
                    csv_write = csv.writer(f)
                    data_row = [current_time, result_data]
                    csv_write.writerow(data_row)
            else:
                with open(path, "a+") as f:
                    csv_write = csv.writer(f)
                    data_row = [current_time, "这次没拿到数据"]
                    csv_write.writerow(data_row)

            sleep_time = (int)(self._json["Battery_Time"])
            time.sleep(sleep_time)

            if self._json["Run_Control"]:
                print("设备" + key + "，第" + str(i) + "次采集电量数据...")
                i += 1
            else:
                print("设备"+key+"电量采集结束...")

        if self._json["Run_Control"] == False:
            print("start to get file")
            list_devices = self._json["Devices"]
            path = self._get_path(key)
            target_dir = os.path.split(path)[0]
            device_ip = list_devices[key]["ip"]
            check_android_version = self._json["Command"]["check_android_version"] % device_ip
            operator = os.popen(check_android_version)
            device_version = (float)(re.split("\\.", operator.readline())[0])
            operator.close()
            if device_version >= 7:
                cmd_1 = self._json["Command"]["exceed_android_7"] % (device_ip, (str)(target_dir))
                cmd_3 = self._json["Command"]["end_collect"] % device_ip
                print("设备"+key+',bugreport生成中...')
                os.system(cmd_1)
                os.system(cmd_3)
                print("android_7+  bugreport生成完成")
            else:
                cmd_2 = self._json["Command"]["under_android_7"] % (device_ip, (str)(target_dir))
                cmd_4 = self._json["Command"]["end_collect"] % device_ip
                print("设备"+key+',bugreport生成中...')
                os.system(cmd_2)
                os.system(cmd_4)
                print("android_6   bugreport生成完成")



    def _battery_data_snapshoot(self,device_ip):
        result_data = -1
        try:
            cmd = self._json["Command"]["Battery_Command"] % device_ip
            operator = os.popen(cmd)
        except Exception as e:
            time.sleep(5)
            return result_data

        battery_info = operator.readline()
        operator.close()
        result_data = battery_info[9:]
        return result_data

    def _get_path(self, key):
        main_dir = self._json["Path"]["data_path"] % self._json["Test_Title"]
        branch_dir = self._json["Path"]["result_path"]["battery"] % self._json["Devices"][key]["name"]
        path = os.path.join(main_dir, branch_dir)
        return path

