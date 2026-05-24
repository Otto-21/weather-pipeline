import pyarrow as pa
import pyarrow.parquet as pq
import duckdb
from app.config import settings
from app.models import WeatherRaw

CURATED_PATH = settings.curated_dir / "weather.parquet"


def save_raw(record: WeatherRaw) -> None:
    day = record.collected_at.strftime("%Y-%m-%d")
    city = record.city.lower().replace(" ", "_")

    folder = settings.raw_dir / day
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{city}.parquet"

    row = pa.table({
        "city": [record.city],
        "country": [record.country],
        "latitude": [record.latitude],
        "longitude": [record.longitude],
        "temp_celsius": [record.temp_celsius],
        "feels_like_celsius": [record.feels_like_celsius],
        "humidity_pct": [record.humidity_pct],
        "pressure_hpa": [record.pressure_hpa],
        "wind_speed_ms": [record.wind_speed_ms],
        "cloudiness_pct": [record.cloudiness_pct],
        "weather_main": [record.weather_main],
        "weather_description": [record.weather_description],
        "collected_at": [record.collected_at]
    })

    if path.exists():
        existing = pq.read_table(path)
        pq.write_table(pa.concat_tables([existing, row]), path)