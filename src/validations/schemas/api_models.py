from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

# Base configuration to discard unmapped API fields automatically
class APIBaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


# 1. OpenWeatherMap Models
class WeatherCondition(APIBaseModel):
    main: str
    description: str

class WeatherMain(APIBaseModel):
    temp: float
    humidity: int

class WeatherWind(APIBaseModel):
    speed: float
    gust: Optional[float] = None

class OpenWeatherRawResponse(APIBaseModel):
    name: str = "Unknown City"
    weather: List[WeatherCondition] = Field(default_factory=list)
    main: WeatherMain
    visibility: int = 10000
    wind: WeatherWind
    rain: Optional[dict] = Field(default_factory=dict)  # Handles missing rain object


# 2. TomTom Traffic Models
class TrafficFlowSegment(APIBaseModel):
    frc: str = "Unknown"
    currentSpeed: float
    freeFlowSpeed: float
    currentTravelTime: int
    freeFlowTravelTime: int
    confidence: float = 1.0
    roadClosure: bool = False

class TomTomRawResponse(APIBaseModel):
    flowSegmentData: TrafficFlowSegment


# 3. WAQI (Air Quality) Models
class IAQIPollutant(APIBaseModel):
    v: Optional[float] = None

class IAQI(APIBaseModel):
    pm25: Optional[IAQIPollutant] = None

class WAQIData(APIBaseModel):
    aqi: int
    dominentpol: str = "pm25"
    iaqi: IAQI = Field(default_factory=IAQI)

class WAQIRawResponse(APIBaseModel):
    status: str
    data: WAQIData


# 4. Nager.Date (Holidays) Model
class HolidayItem(APIBaseModel):
    date: str
    name: str
    countryCode: str
    nationalHoliday: bool = True