from datetime import datetime
from pydantic import ValidationError
from src.utils.data_ops import DataOps
from src.validations.schemas.api_models import (
    OpenWeatherRawResponse,
    TomTomRawResponse,
    WAQIRawResponse,
    HolidayItem,
)

def validate_all_inputs(weather_path: str, traffic_path: str, aqi_path: str, holidays_path: str):
    try:
        # Read raw JSON data from files
        weather_raw = DataOps().read_json(weather_path)
        traffic_raw = DataOps().read_json(traffic_path)
        aqi_raw = DataOps().read_json(aqi_path)
        holidays_raw = DataOps().read_json(holidays_path)
        

        # Validate each API independently
        v_weather = OpenWeatherRawResponse.model_validate(weather_raw)
        v_traffic = TomTomRawResponse.model_validate(traffic_raw)
        v_aqi = WAQIRawResponse.model_validate(aqi_raw)
        v_holidays = [HolidayItem.model_validate(item) for item in holidays_raw]

        return {
            "weather": v_weather,
            "traffic": v_traffic,
            "aqi": v_aqi,
            "holidays": v_holidays,
        }

    except ValidationError as e:
        # Log exact field errors (e.g., missing freeFlowSpeed, invalid types)
        print(f"Data Contract Failure: {e.json()}")
        raise e