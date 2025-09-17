import random
import time
import json 


class pycomm3:
    def __init__(self):
        self.count = 500
        self.data = []

    def read_cycletime_tags(self,tag_name):
        print(tag_name)
        # Simulate 500 random values (e.g., integers between 0 and 1000)
        self.data = [random.randint(0, 1000) for _ in range(self.count)]
        return self.data
    def read_dashboard_tags(self):
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
        for index,tag in enumerate(tags):
            tags_data[labels[index]] = random.randint(0,100)
        
        return tags_data
# Usage
plc = pycomm3()
tag_data = plc.read_dashboard_tags()

# Display a sample
print(tag_data)