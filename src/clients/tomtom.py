import requests, os
from dotenv import load_dotenv

load_dotenv()

class TomTomClient:

    @staticmethod
    def call(lat, lon):
        LAT = lat
        LON = lon

        ZOOM = 10

        url = os.getenv("TOMTOM_Base_URL")
        endpoint = f"{url}/{ZOOM}/json"

        params = {
            "key": os.getenv("TOMTOM_API_KEY"),
            "point": f"{LAT},{LON}",
            "unit": "KMPH",
        }

        response = requests.get(endpoint, params=params)
        print(f"response: {response.json()}")
        return response.json()