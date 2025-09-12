import json
from pycomm3 import LogixDriver
# step-1 : read the json
tags_data = {}
try:
    file_path = "plc_custom_user_tags\\cycle_time_tags.json"
    with open(file_path, "r") as file:
        data = json.load(file)

    # print(data)
    tags = []  # tag list is a requirement
    stations = []
    if len(data) > 0:
        # step-2 : generate a taglist from the json data to read it
        for i in data:
            tags.append(data[i][0])
            stations.append(i)
            
        with LogixDriver('192.168.0.10') as plc:
            if plc.connected:
                for index, tag in enumerate(tags):
                    tags_data[stations[index]] = 500                         
            else:
                pass
except Exception as e:
    print("Exception occured:")      




print(tags_data)