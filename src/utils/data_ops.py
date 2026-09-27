from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


class DataOps:

  def __init__(self, base_dir: str = "/opt/airflow/data"):
    self.base_dir = Path(base_dir)

  def read_json(self, path: str | Path) -> Any:
    file_path = Path(path)
    with open(file_path, "r", encoding="utf-8") as file:
      return json.load(file)

  def save_json(
      self,
      data: Any,
      is_processed: bool = False,
      api_name: str = "weather",
  ) -> str:
    current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if is_processed:
      file_path = self.base_dir / "processed" / f"{current_date}.json"
    else:
      file_path = self.base_dir / "raw" / api_name / f"{current_date}.json"

    # Now file_path is a Path object, so .parent works
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
      json.dump(data, file, indent=2)

    return str(file_path)