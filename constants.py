import json

with open('wheights.json') as f:
    data = json.load(f)

weights = data['weights']
equipped_items = data['my_items']