import json

def getUsernames():
    with open("following.json", "r") as f:
        return json.load(f)
