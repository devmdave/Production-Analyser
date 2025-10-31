import json
from logging.handlers import DatagramHandler
from unittest import mock
from MockPLCServer import mock_plc
from my_plc import data_writer 
 
# step-1 : read the json
file_path = "plc_custom_user_tags\\cycle_time_tags.json"
with open(file_path, "r") as file:
    data = json.load(file)

if len(data) > 0:
    #step-2 : generate a taglist from the json data to read it 
    tags = [] # tag list is a requirement
    stations = []
    for i in data:
        tags.append(data[i][0])
        stations.append(i)

    # for index, tag in enumerate(tags):
    #     print(stations[index])

    tags_data = {}  
    for index,tag in enumerate(tags):
        tags_data[stations[index]] = mock_plc.pycomm3().read_cycletime_tags(tag)

    #step-3: write to excel
    dw = data_writer()
    dw.write_to_excel(tags_data)
