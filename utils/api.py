import requests
from dotenv import load_dotenv
import os

load_dotenv()

class WeatherAPI:
    def get_weather(self):
        response = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q=Hanoi&appid={os.getenv('WEATHER_API_KEY')}"
        )
        data = response.json()
        return {
            'temp': round(data['main']['temp'] - 273.15, 1),
            'description': data['weather'][0]['description']
        }
