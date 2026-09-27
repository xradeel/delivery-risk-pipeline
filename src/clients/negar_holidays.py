import requests, os
from dotenv import load_dotenv

load_dotenv()

class NegarHolidaysClient:

    @staticmethod
    def call(country_code="US", year=2026):

        url = f"{os.getenv('NegarHolidays_Base_URL')}/{country_code}/{year}"
        response = requests.get(url)
        return response.json()