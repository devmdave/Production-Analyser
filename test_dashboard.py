import json
from pycomm3 import LogixDriver
import random

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
for index,tag in enumerate(tags):
    tags_data[labels[index]] = random.randint(0,100)

print(tags_data)