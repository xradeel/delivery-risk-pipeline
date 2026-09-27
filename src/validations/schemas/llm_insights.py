from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class UrgencyLevel(str, Enum):
  LOW = "LOW"
  MODERATE = "MODERATE"
  CRITICAL = "CRITICAL"


class DeliveryInsightContract(BaseModel):
  urgency_level: UrgencyLevel = Field(
      description=(
          "Operational risk severity: LOW, MODERATE, or CRITICAL based on"
          " conditions."
      )
  )
  headline: str = Field(
      max_length=255,
      description="One-sentence executive summary of current delivery risk.",
  )
  dispatch_recommendation: str = Field(
      description=(
          "Tactical instructions for fleet/dispatch (e.g. re-routing,"
          " adjusting ETA, bike vs van assignment)."
      )
  )
  customer_advisory: Optional[str] = Field(
      default=None,
      description=(
          "Customer-ready SMS/notification message explaining potential delays"
          " without technical jargon."
      ),
  )