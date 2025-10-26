import random
import time
import json 


class pycomm3:
    def __init__(self):
        self.count = 500
        self.data = []

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

                for index, tag in enumerate(tags):
                    tags_data[stations[index]] = random.randint(0,100)
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

            
                for index, tag in enumerate(tags):
                    tags_data[stations[index]] = random.randint(0,100)
        
        except Exception as e:
            pass
        return tags_data

    def read_cycletime_tags(self):
        # Simulate 500 random values (e.g., integers between 0 and 1000)
        self.data = [random.randint(0, 1000) for _ in range(self.count)]
        return self.data
    
    def read_dashboard_tags(self):
        with open('plc_custom_user_tags\\dashboard_tags.json', 'r') as f:
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
        for index,tag in enumerate(tags):
            tags_data[labels[index]] = random.randint(0,100)
        
        return tags_data
# Usage
plc = pycomm3()
tag_data = plc.read_dashboard_tags()

# Display a sample
print(tag_data)