from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.warehouse.session import Base


class FactDeliveryRisk(Base):
  __tablename__ = "fact_delivery_risks"

  # Automatic UUID Primary Key
  id: Mapped[uuid.UUID] = mapped_column(
      UUID(as_uuid=True),
      primary_key=True,
      default=uuid.uuid4,
      server_default=func.gen_random_uuid(),
  )

  # Spatial & Temporal Dimensions
  timestamp_utc: Mapped[datetime] = mapped_column(
      DateTime(timezone=True), index=True, nullable=False
  )
  city: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
  lat: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False)
  lon: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False)

  # Weather Metrics
  weather_condition: Mapped[str] = mapped_column(String(50), nullable=False)
  weather_desc: Mapped[str] = mapped_column(String(100), nullable=False)
  temp_c: Mapped[float] = mapped_column(Numeric(4, 1), nullable=False)
  humidity_pct: Mapped[int] = mapped_column(Integer, nullable=False)
  visibility_meters: Mapped[int] = mapped_column(Integer, nullable=False)
  wind_speed_mps: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
  wind_gust_mps: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
  precipitation_mm: Mapped[float] = mapped_column(
      Numeric(5, 2), default=0.0, nullable=False
  )

  # Traffic Metrics
  current_speed_kmh: Mapped[float] = mapped_column(
      Numeric(5, 1), nullable=False
  )
  free_flow_speed_kmh: Mapped[float] = mapped_column(
      Numeric(5, 1), nullable=False
  )
  speed_ratio: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
  delay_pct: Mapped[float] = mapped_column(Numeric(5, 1), nullable=False)
  road_class: Mapped[str] = mapped_column(String(20), nullable=False)
  is_road_closed: Mapped[bool] = mapped_column(
      Boolean, default=False, nullable=False
  )
  traffic_confidence: Mapped[float] = mapped_column(
      Float, default=1.0, nullable=False
  )

  # Air Quality Metrics
  aqi: Mapped[int] = mapped_column(Integer, nullable=False)
  primary_pollutant: Mapped[str] = mapped_column(
      String(20), default="pm25", nullable=False
  )
  pm25_value: Mapped[Optional[float]] = mapped_column(
      Numeric(5, 2), nullable=True
  )

  # Calendar Context
  is_holiday: Mapped[bool] = mapped_column(
      Boolean, default=False, nullable=False
  )
  holiday_name: Mapped[Optional[str]] = mapped_column(
      String(100), nullable=True
  )

  # Metadata
  created_at: Mapped[datetime] = mapped_column(
      DateTime(timezone=True),
      server_default=func.now(),
      nullable=False,
  )

  # Relationship to insights table
  insights: Mapped[List["DeliveryRiskInsight"]] = relationship(
      back_populates="risk_fact",
      cascade="all, delete-orphan",
  )


class DeliveryRiskInsight(Base):
  __tablename__ = "delivery_risk_insights"

  # Automatic UUID Primary Key
  id: Mapped[uuid.UUID] = mapped_column(
      UUID(as_uuid=True),
      primary_key=True,
      default=uuid.uuid4,
      server_default=func.gen_random_uuid(),
  )

  # Foreign Key linking to the telemetry record
  risk_record_id: Mapped[uuid.UUID] = mapped_column(
      UUID(as_uuid=True),
      ForeignKey("fact_delivery_risks.id", ondelete="CASCADE"),
      index=True,
      nullable=False,
  )

  # Operational Insights
  urgency_level: Mapped[str] = mapped_column(
      String(20), nullable=False
  )  # e.g., 'LOW', 'MODERATE', 'CRITICAL'
  headline: Mapped[str] = mapped_column(String(255), nullable=False)
  dispatch_recommendation: Mapped[str] = mapped_column(Text, nullable=False)
  customer_advisory: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

  # Raw LLM response payload
  structured_output: Mapped[Optional[Dict[str, Any]]] = mapped_column(
      JSONB, nullable=True
  )

  # Observability & Cost Metrics
  model_name: Mapped[str] = mapped_column(String(50), nullable=False)
  prompt_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
  completion_tokens: Mapped[int] = mapped_column(
      Integer, default=0, nullable=False
  )
  total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
  execution_duration_ms: Mapped[int] = mapped_column(
      Integer, default=0, nullable=False
  )

  created_at: Mapped[datetime] = mapped_column(
      DateTime(timezone=True),
      server_default=func.now(),
      nullable=False,
  )

  # Relationship back to the fact record
  risk_fact: Mapped["FactDeliveryRisk"] = relationship(back_populates="insights")