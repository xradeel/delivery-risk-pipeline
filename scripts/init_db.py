import sys
from pathlib import Path

# Ensure project root is on sys.path if run directly
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.warehouse.session import Base, engine
from src.warehouse.models import FactDeliveryRisk  # Required so Base knows about the model


def init_database() -> None:
    """Creates all database tables defined in metadata."""
    print("Connecting to database and creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Table 'fact_delivery_risks' successfully created.")


if __name__ == "__main__":
    init_database()