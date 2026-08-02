import requests
import json

API = "https://stremio-next.vercel.app/api/home"

response = requests.get(API)
data = response.json()

def add_iframe(items):
    result = []
    for item in items:
        new_item = dict(item)
        new_item["iframe"] = f"https://peachify.top/embed/{item['type']}/{item['id']}?accent=7c5cff&dub=Hindi&quality=1080"
        result.append(new_item)
    return result

data["data"]["spotlight"] = add_iframe(data["data"]["spotlight"])
data["data"]["trending"] = add_iframe(data["data"]["trending"])

with open("movie.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated movie.json")
