import random
import time
import json 


class pycomm3:
    def __init__(self):
        self.count = 500
        self.data = []

<<<<<<< Updated upstream

    def read_tip_dress_tags(self):
=======
    def read_tip_dress_count_tags(self):
        # step-1 : read the json
        tags_data = {}
        try:
            file_path = "plc_custom_user_tags\\tip_dress_tags.json"
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
                    tags_data[stations[index]] = random.randint(0,100)  #self.plc.read(tag).value

        except Exception as e:
            pass
        return tags_data


    def read_last_tip_dress_tags(self):
        # step-1 : read the json
        tags_data = {}
        try:
            file_path = "plc_custom_user_tags\\tip_dress_tags.json"
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
                    tags_data[stations[index]] = random.randint(0,100)  #self.plc.read(tag).value

        except Exception as e:
            pass
        return tags_data

    def read_station_fault_tags(self):
>>>>>>> Stashed changes
        # step-1 : read the json
        tags_data = {}
        try:
            # Read set_names_tags.json
            set_file_path = "plc_custom_user_tags\\set_names_tags.json"
            with open(set_file_path, "r") as file:
                set_data = json.load(file)

            # Read actual_names_tags.json
            actual_file_path = "plc_custom_user_tags\\actual_names_tags.json"
            with open(actual_file_path, "r") as file:
                actual_data = json.load(file)

            # Ensure common robot names
            common_robots = set(set_data.keys()) & set(actual_data.keys())

            set_tags = []  # separate array for set tags
            actual_tags = []  # separate array for actual tags
            robots = []

            if len(common_robots) > 0:
                # step-2 : generate tag lists from the json data to read it
                for robot in common_robots:
                    set_tags.append(set_data[robot][0])
                    actual_tags.append(actual_data[robot][0])
                    robots.append(robot)
                for index, robot in enumerate(robots):
                    set_value = random.randint(1, 100) #self.plc.read(set_tags[index]).value
                    actual_value = random.randint(1, 100) #self.plc.read(actual_tags[index]).value
                    tags_data[robot] = [set_value, actual_value]
        except Exception as e:
            pass
    
        return tags_data




    def read_cycletime_tags(self,tag_name):
        print(tag_name)
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