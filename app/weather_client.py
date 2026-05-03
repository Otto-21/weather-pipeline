import hpptx
from datetime import datetime
from app.models import WeatherRaw
from app.config import settings

BASE_URL = "https://api.openweathermap.org/data/3.0/weather"

async def fetch_weather(city: str) -> WeatherRaw | None:
    params = {
        "q": city,
        "appid": settings.openweather_api_key,
        "units": "metric",
        "lang": "pt_br"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response= await client.get(BASE_URL, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"Error fetching weather data for {city}: {e}")
            return None
        except httpx.RequestError as e:
            print(f"Network error while fetching weather data for {city}: {e}")
            return None
    
    data= response.json()

    return WeatherRaw(
        city= data["name"],
        country=data["sys"]["country"],
        latitude=data["coord"]["lat"],
        longitude=data["coord"]["lon"],
        temp_celsius=data["main"]["temp"],
        feels_like_celsius=data["main"]["feels_like"],
        humidity_pct=data["main"]["humidity"],
        pressure_hpa=data["main"]["pressure"],
        wind_speed_ms=data["wind"]["speed"],
        cloudiness_pct=data["clouds"]["all"],
        weather_main=data["weather"][0]["main"],
        weather_description=data["weather"][0]["description"],
    )