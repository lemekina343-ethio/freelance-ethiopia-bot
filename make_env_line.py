import json

with open("credentials.json", "r") as f:
    data = json.load(f)

print("GOOGLE_CREDENTIALS=" + json.dumps(data))