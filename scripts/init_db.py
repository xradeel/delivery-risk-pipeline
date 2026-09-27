import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(PROJECT_ROOT))

# Ensure both models are imported so their DDL is registered with Base
from src.warehouse.models import DeliveryRiskInsight, FactDeliveryRisk
from src.warehouse.session import Base, engine


def init_database() -> None:
  print("Creating tables in warehouse database...")
  Base.metadata.create_all(bind=engine)
  print("Tables successfully initialized.")


if __name__ == "__main__":
  init_database()