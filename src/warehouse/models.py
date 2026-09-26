from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

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

  # Geographic & Temporal Dimensions
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