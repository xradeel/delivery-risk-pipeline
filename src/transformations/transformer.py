from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from utils.data_ops import DataOps


class DeliveryRiskTransformer:

    @staticmethod
    def transform_weather(weather_raw: Dict[str, Any]) -> Dict[str, Any]:

        main_data = weather_raw.get("main", {})
        wind_data = weather_raw.get("wind", {})
        weather_list = weather_raw.get("weather", [{}])
        first_condition = weather_list[0] if weather_list else {}

        # Safely handle rain volume (can be nested under '1h' or absent)
        rain_data = weather_raw.get("rain", {})
        precip_mm = float(rain_data.get("1h", 0.0))

        # Safely fallback for wind gusts if not present
        wind_speed = float(wind_data.get("speed", 0.0))
        wind_gust = float(wind_data.get("gust", wind_speed))

        return {
            "city": weather_raw.get("name", "Unknown"),
            "weather_condition": first_condition.get("main", "Clear"),
            "weather_desc": first_condition.get("description", "clear sky"),
            "temp_c": round(float(main_data.get("temp", 0.0)), 1),
            "humidity_pct": int(main_data.get("humidity", 0)),
            "visibility_meters": int(weather_raw.get("visibility", 10000)),
            "wind_speed_mps": round(wind_speed, 1),
            "wind_gust_mps": round(wind_gust, 1),
            "precipitation_mm": round(precip_mm, 1),
        }

    @staticmethod
    def transform_traffic(traffic_raw: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts and derives traffic congestion and delay metrics from TomTom."""
        flow = traffic_raw.get("flowSegmentData", {})

        current_speed = float(flow.get("currentSpeed", 0.0))
        free_flow_speed = float(flow.get("freeFlowSpeed", 0.0))
        current_travel_time = float(flow.get("currentTravelTime", 0.0))
        free_flow_travel_time = float(flow.get("freeFlowTravelTime", 0.0))

        # Avoid ZeroDivisionError on speed and travel time ratios
        speed_ratio = (
            round(current_speed / free_flow_speed, 2)
            if free_flow_speed > 0
            else 1.0
        )

        delay_pct = 0.0
        if free_flow_travel_time > 0:
            delay_pct = round(
                (
                    (current_travel_time - free_flow_travel_time)
                    / free_flow_travel_time
                )
                * 100,
                1,
            )

        return {
            "current_speed_kmh": round(current_speed, 1),
            "free_flow_speed_kmh": round(free_flow_speed, 1),
            "speed_ratio": speed_ratio,
            "delay_pct": max(0.0, delay_pct),
            "road_class": flow.get("frc", "Unknown"),
            "is_road_closed": bool(flow.get("roadClosure", False)),
            "traffic_confidence": float(flow.get("confidence", 1.0)),
        }

    @staticmethod
    def transform_aqi(aqi_raw: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts particulate matter and air quality metrics from WAQI."""
        data = aqi_raw.get("data", {})
        iaqi = data.get("iaqi", {})

        pm25_val = iaqi.get("pm25", {}).get("v")

        return {
            "aqi": int(data.get("aqi", 0)),
            "primary_pollutant": data.get("dominentpol", "pm25"),
            "pm25_value": float(pm25_val) if pm25_val is not None else None,
        }

    @staticmethod
    def transform_holidays(
        holidays_raw: List[Dict[str, Any]], target_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Checks if target_date (defaulting to today UTC) is a registered public holiday."""
        if not target_date:
            target_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        is_holiday = False
        holiday_name = None

        for holiday in holidays_raw:
            if holiday.get("date") == target_date:
                is_holiday = True
                holiday_name = holiday.get("name")
                break

        return {
            "is_holiday": is_holiday,
            "holiday_name": holiday_name,
        }

    @classmethod
    def transform(
        cls,
        lat: float,
        lon: float,
        weather_path: str,
        traffic_path: str,
        aqi_path: str,
        holidays_path: str,
        target_date: Optional[str] = None,
    ) -> Dict[str, Any]:

        # Read raw data from files
        weather_raw = DataOps().read_json(weather_path)
        traffic_raw = DataOps().read_json(traffic_path)
        aqi_raw = DataOps().read_json(aqi_path)
        holidays_raw = DataOps().read_json(holidays_path)

        weather_metrics = cls.transform_weather(weather_raw)
        traffic_metrics = cls.transform_traffic(traffic_raw)
        aqi_metrics = cls.transform_aqi(aqi_raw)
        holiday_metrics = cls.transform_holidays(holidays_raw, target_date)

        # Merge all into the final flat contract
        result = {
            # Metadata & Geographic Dimension
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "city": weather_metrics.pop("city"),
            "lat": lat,
            "lon": lon,
            # Weather Metrics
            **weather_metrics,
            # Traffic Metrics
            **traffic_metrics,
            # Air Quality Metrics
            **aqi_metrics,
            # Calendar Context
            **holiday_metrics,
        }
        processed_path = DataOps.save_json(result, is_processed=True)
        return processed_path