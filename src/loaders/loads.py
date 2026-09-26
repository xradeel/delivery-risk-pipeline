from datetime import datetime
from src.warehouse.session import get_db_session
from src.warehouse.models import FactDeliveryRisk
from src.utils.data_ops import DataOps


def insert_delivery_risk_record(processed_path):
    
    with get_db_session() as session:
        # Parse ISO string to datetime object if needed
        record_data = DataOps().read_json(processed_path)
        
        if isinstance(record_data.get("timestamp_utc"), str):
            record_data["timestamp_utc"] = datetime.fromisoformat(
                record_data["timestamp_utc"]
            )

        new_record = FactDeliveryRisk(**record_data)
        session.add(new_record)
        session.flush()  # Populates new_record.id
        return new_record.id