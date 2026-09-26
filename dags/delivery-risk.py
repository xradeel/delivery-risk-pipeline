from datetime import datetime
from airflow.sdk import dag, task



@dag(
    dag_id="delivery_risk",
    schedule=None,
    start_date=datetime(2026, 9, 26),
    catchup=False,
)
def delivery_risk_dag():

    @task
    def fetch_traffic(lon, lat):
        from src.clients.tomtom import TomTomClient
        return TomTomClient.call(lat, lon)

    @task
    def fetch_aqi(lon, lat):
        from src.clients.aqi import AQIClient
        return AQIClient.call(lat, lon)

    @task
    def fetch_weather(lon, lat):
        from src.clients.open_weather import OpenWeatherClient
        return OpenWeatherClient.call(lat, lon)

    @task
    def fetch_holidays(country_code, year):
        from src.clients.negar_holidays import NegarHolidaysClient
        return NegarHolidaysClient.call(country_code, year)


    #new york coordinates
    lon = -74.0060
    lat = 40.7128

    traffic_data = fetch_traffic(lon, lat)
    aqi_data = fetch_aqi(lon, lat)
    weather_data = fetch_weather(lon, lat)
    holidays_data = fetch_holidays("US", 2023)


delivery_risk_dag()
