import json

with open("config.json", 'r') as file:
    Config = json.loads(file.read())
