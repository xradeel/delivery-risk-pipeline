from datetime import datetime, timedelta
from airflow.sdk import dag, task

from src.utils.data_ops import DataOps
from src.clients.aqi import AQIClient
from src.clients.tomtom import TomTomClient
from src.clients.open_weather import OpenWeatherClient
from src.clients.negar_holidays import NegarHolidaysClient
from src.validations.validates import validate_all_inputs

from src.transformations.transformer import DeliveryRiskTransformer


@dag(
    dag_id="delivery_risk",
    schedule=None,
    start_date=datetime(2026, 9, 26),
    catchup=False,
)
def delivery_risk_dag():

    @task
    def fetch_traffic(lon, lat):
        response = TomTomClient.call(lat, lon)
        path = DataOps().save_json(response, is_processed=False, api_name="traffic")
        return path

    @task
    def fetch_aqi(lon, lat):
        response = AQIClient.call(lat, lon)
        path = DataOps().save_json(response, is_processed=False, api_name="aqi")
        return path

    @task
    def fetch_weather(lon, lat):
        response = OpenWeatherClient.call(lat, lon)
        path = DataOps().save_json(response, is_processed=False, api_name="weather")
        return path

    @task
    def fetch_holidays(country_code, year):
        response = NegarHolidaysClient.call(country_code, year)
        path = DataOps().save_json(response, is_processed=False, api_name="holidays")
        return path

    @task
    def validate_data(traffic_path, aqi_path, weather_path, holidays_path):
        return validate_all_inputs(traffic_path=traffic_path, aqi_path=aqi_path, weather_path=weather_path, holidays_path=holidays_path)

    @task
    def transform_task(weather_path, traffic_path, aqi_path, holidays_path):
        return DeliveryRiskTransformer.transform(
            lat=lat,
            lon=lon,
            weather_path=weather_path,
            traffic_path=traffic_path,
            aqi_path=aqi_path,
            holidays_path=holidays_path,
        )


    #new york coordinates
    lon = -74.0060
    lat = 40.7128

    traffic_data = fetch_traffic(lon, lat)
    aqi_data = fetch_aqi(lon, lat)
    weather_data = fetch_weather(lon, lat)
    holidays_data = fetch_holidays("US", 2026)

    validated_data = validate_data(traffic_data, aqi_data, weather_data, holidays_data)


    transformed_data = transform_task(weather_data, traffic_data, aqi_data, holidays_data)


delivery_risk_dag()
