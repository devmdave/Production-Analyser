from cProfile import label
from tkinter.tix import ListNoteBook
from pycomm3 import LogixDriver
import os
import pandas as pd
import datetime
import json
from Dialog import Dialog
from PyQt5.QtWidgets import QApplication, QDialog


class Plc:  
    TOTAL_PRODUCTION_TAG = "UBG_LINE_PC_DAY_Total_1"
   #TOTAL_DELAY_TAG = "T_DELAY"
    SHIFT_A_PRODUCTION = "UBG_LINE_PC.Shift_A_Total[0]"
    SHIFT_B_PRODUCTION = "UBG_LINE_PC.Shift_B_Total[0]"

    def __init__(self, ip):
        self.ip = ip
        self.plc_status = False
        try:
            with LogixDriver(self.ip) as self.plc:
                self.plc_status = True
                # self.disconnect()
        except Exception as e:
            self.plc_status = False

    def read_cycletime_tags(self):
        print("reading cycle time tags line 27 of my_plc.py ")
        # step-1 : read the json
        tags_data = {}
        try:
            file_path = "plc_custom_user_tags\\cycle_time_tags.json"
            with open(file_path, "r") as file:
                data = json.load(file)

            tags = []  # tag list is a requirement
            stations = []
            if len(data) > 0:
                # step-2 : generate a taglist from the json data to read it
                for i in data:
                    tags.append(data[i][0])
                    stations.append(i)
                    
                with LogixDriver(self.ip) as self.plc:
                    if self.plc.connected:
                        for index, tag in enumerate(tags):
                            tags_data[stations[index]] = list(self.plc.read(tag).value)                          
                    else:
                        pass
        except Exception as e:
            pass      
        return tags_data

    def read_fault_delay_tags(self):
        # step-1 : read the json
        tags_data = {}
        try:
            file_path = "plc_custom_user_tags\\fault_delay_tags.json"
            with open(file_path, "r") as file:
                data = json.load(file)

            tags = []  # tag list is a requirement
            stations = []

            if len(data) > 0:
                # step-2 : generate a taglist from the json data to read it

                for i in data:
                    tags.append(data[i][0])
                    stations.append(i)

                with LogixDriver(self.ip) as self.plc:
                    if self.plc.connected:
                        for index, tag in enumerate(tags):
                            tags_data[stations[index]] = self.plc.read(tag).value
                    else:
                        pass
        except Exception as e:
            pass
        return tags_data

    def read_delay_tags(self):
        tags = [
            "LC",
            "EMG",
            "GATE_SW",
            "MAT_SW",
            "UBG10_delay",
            "UBG20_delay",
            "UBG30_delay",
            "UBG40_delay",
            "UBG50_delay",
            "UBG60_delay",
            "UBG70_delay",
            "UBG80_delay",
            "UBG90_delay",
            "UBG100_delay",
        ]
        # Dictionary to store the PLC data
        tags_data = {}
        # Connect to the PLC using LogixDriver
        with LogixDriver(self.ip) as self.plc:
            if self.plc.connected:
                for tag in tags:
                    tags_data[tag.replace("_delay", "")] = self.plc.read(tag).value
            else:
                pass
        return tags_data

    def read_dashboard_tags(self):
        try:
            with open('config.json', 'r') as f:
                data = json.load(f)

            parameters = data.get('parameters', [])
            tags = []
            labels = []

            for param in parameters:
                tags.append(param.get('value', '0'))
                labels.append(param.get('name'))
            # Dictionary to store the PLC data
            tags_data = {}
            # Connect to the PLC using LogixDriver
            with LogixDriver(self.ip) as self.plc:
                if self.plc.connected:
                    for index,tag in enumerate(tags):
                        tags_data[labels[index]] = self.plc.read(tag).value
                else:
                    tags_data = None
        except Exception as e:
            tags_data = None
        return tags_data

    def read_station_fault_tags(self):
        # step-1 : read the json
        tags_data = {}
        try:
            file_path = "plc_custom_user_tags\\station_fault_tags.json"
            with open(file_path, "r") as file:
                data = json.load(file)

            tags = []  # tag list is a requirement
            stations = []

            if len(data) > 0:
                # step-2 : generate a taglist from the json data to read it

                for i in data:
                    tags.append(data[i][0])
                    stations.append(i)

                with LogixDriver(self.ip) as self.plc:
                    if self.plc.connected:
                        for index, tag in enumerate(tags):
                            tags_data[stations[index]] = self.plc.read(tag).value
                            
                    else:
                        pass
        except Exception as e:
            pass
        return tags_data

    def get_plc_status(self):
        if self.plc_status:
            if not self.plc:
                return False
            else:
                return self.plc.connected
        elif not self.plc_status:
            return self.plc_status  # this will be always be false if condition occurs

    def disconnect(self):
        if self.plc:
            self.plc.close()


class data_writer:

    FAULT_DELAY_BACKUP_DIR = "FaultDelayBackup"
    CYCLETIME_BACKUP_DIR = "CycleTimeBackup"
    STATION_FAULT_DIR = "StationFaultBackup"

    def __init__(self):
        pass

    def write_to_excel(self, tags_data,directory):
        print("at line 183 write_to_excel in my_plc.py")
        os.makedirs(directory, exist_ok=True)
        # Convert dictionary to DataFrame
        if len(tags_data) > 0:
            df = pd.DataFrame(tags_data)
            df.index = range(1, len(df) + 1)
            # Transpose the DataFrame to have tags as rows and their values as columns
            df = df.transpose()
            # get todays date in the format 'dd-mm-yyyy'
            today_str = datetime.datetime.now().strftime("%d-%m-%Y")
            with pd.ExcelWriter(f"./{directory}/{today_str}.xlsx") as writer:
                df.to_excel(writer, sheet_name=today_str, index=True)
