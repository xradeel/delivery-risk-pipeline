import requests, os
from dotenv import load_dotenv

load_dotenv()

class AQIClient:

    @staticmethod
    def call(lat, lon):
        LAT = lat
        LON = lon

        BASE_URL = os.getenv("AQI_Base_URL")
        API_KEY = os.getenv("AQI_API_KEY")
        url = f"{BASE_URL}:{LAT};{LON}/"
        params = {"token": API_KEY}
        response = requests.get(url, params=params)
        return response.json()