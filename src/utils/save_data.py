import json
from datetime import datetime
from pathlib import Path


class SaveData:

    def json(self, data:json, is_processed: bool = False, api_name: str = "weather"):
        current_date = datetime.now().strftime("%Y-%m-%d")
        if is_processed:
            path = f"data/processed/{api_name}/{current_date}.json"
        else:
            path = f"data/raw/{api_name}/{current_date}.json"

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as file:
            json.dump(data, file, indent=2)

        return path