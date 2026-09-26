import requests, os
from dotenv import load_dotenv

load_dotenv()

class OpenWeatherClient:

    @staticmethod
    def call(lat: float, lon: float, units: str = "metric"):
        url = os.getenv("OpenWeatherMap_Base_URL")
        API_KEY = os.getenv("OpenWeatherMap_API_KEY")
        params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": units  # "metric" for Celsius, "imperial" for Fahrenheit
        }
        response = requests.get(url, params=params)
        return response.json()