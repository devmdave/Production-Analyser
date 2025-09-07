import random
import time

class pycomm3:
    def __init__(self):
        self.count = 500
        self.data = []

    def read_cycletime_tags(self,tag_name):
        print(tag_name)
        # Simulate 500 random values (e.g., integers between 0 and 1000)
        self.data = [random.randint(0, 1000) for _ in range(self.count)]
        return self.data


# Usage
plc = pycomm3()
tag_data = plc.read_cycletime_tags("UBG10")

# Display a sample
print(tag_data)