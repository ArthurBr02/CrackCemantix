import json
from datetime import datetime

json_file = open(f"Data/data{datetime.now().day}-{datetime.now().month}-{datetime.now().year}.json", "r", encoding="utf_8")
json_data = json.load(json_file)
json_file.close()

max = -1
max_mot = "NULL"

for mot in json_data.keys():
    if json_data[mot]["score"] > max:
        max = json_data[mot]["score"]
        max_mot = mot

print("Max: ", max_mot, str(max))