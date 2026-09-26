import json
from datetime import datetime
from pathlib import Path


class DataOps:

    def read_json(self, path: str):
        with open(path, "r") as file:
            data = json.load(file)
        return data

    def save_json(self, data:json, is_processed: bool = False, api_name: str = "weather"):
        current_date = datetime.now().strftime("%Y-%m-%d")
        if is_processed:
            path = f"data/processed/{current_date}.json"
        else:
            path = f"data/raw/{api_name}/{current_date}.json"

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as file:
            json.dump(data, file, indent=2)

        return path

