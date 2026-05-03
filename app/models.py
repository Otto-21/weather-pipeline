from pydantic import BaseModel, Field
from datetime import datetime

#O que será salvo nos parquets

class WeatherRaw(BaseModel):
    city: str
    country: str
    latitude: float
    longitude: float
    temp_celsius: float
    feels_like_celsius: float
    humidity_pct: int
    pressure_hpa: int
    wind_speed_ms: float
    cloudiness_pct: int
    weather_description: str
    weather_main: str
    collected_at: datetime = Field(default_factory=datetime.now)

class CollectRequest(BaseModel):
    cidades: list[str]

class CollectResponse(BaseModel):
    collected: int
    failed: list[str]
    timestamp: datetime = Field(default_factory=datetime.now)