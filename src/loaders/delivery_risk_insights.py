from typing import Any, Dict
import uuid
from src.warehouse.models import DeliveryRiskInsight
from src.warehouse.session import SessionLocal


class DeliveryRiskInsightLoader:

  @staticmethod
  def insert_insight(
      risk_record_id: uuid.UUID | str,
      insight_payload: Dict[str, Any],
      model_meta: Dict[str, Any],
  ) -> uuid.UUID:
    """Persists an LLM-generated insight attached to a fact_delivery_risks ID."""
    if isinstance(risk_record_id, str):
      risk_record_id = uuid.UUID(risk_record_id)

    record = DeliveryRiskInsight(
        risk_record_id=risk_record_id,
        urgency_level=insight_payload.get("urgency_level", "MODERATE"),
        headline=insight_payload.get("headline", ""),
        dispatch_recommendation=insight_payload.get(
            "dispatch_recommendation", ""
        ),
        customer_advisory=insight_payload.get("customer_advisory"),
        structured_output=insight_payload,
        model_name=model_meta.get("model_name", "unknown"),
        prompt_tokens=model_meta.get("prompt_tokens", 0),
        completion_tokens=model_meta.get("completion_tokens", 0),
        total_tokens=model_meta.get("total_tokens", 0),
        execution_duration_ms=model_meta.get("execution_duration_ms", 0),
    )

    with SessionLocal() as session:
      session.add(record)
      session.commit()
      session.refresh(record)
      return record.id