import requests
from dotenv import load_dotenv
import os

load_dotenv()

class WeatherAPI:
    def get_weather(self):
        API_KEY = os.getenv('WEATHER_API_KEY')
        if not API_KEY:
            raise ValueError("Missing WEATHER_API_KEY in .env file")

        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                'q': 'Hanoi,VN',
                'appid': API_KEY,
                'units': 'metric'  # Sử dụng độ Celsius
            }
        )
        data = response.json()
        return {
            'temp': data['main']['temp'],
            # 'temp': 40,
            'description': data['weather'][0]['description']
        }
