import asyncio
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.models import CollectRequest, CollectResponse
from app.weather_client import fetch_weather
from app.storage import save_raw, rebuild_curated

scheduler = AsyncIOScheduler()

DEFAULT_CITIES = [
    "Rio Claro,SP",
    "Americana,SP"
    "Campinas,SP",
    "São Paulo,SP",
    "Rio de Janeiro,RJ",
    "Belo Horizonte,MG"
]

async def collect_cities(cities: list[str]) -> CollectResponse:
    tasks = [fetch_weather(city) for city in cities]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    collected = 0
    failed = []

    for city, result in zip(cities, results):
        if result is None or isinstance(result, Exception):
            failed.append(city)
            continue
        save_raw(result)
        collected += 1
    
    if collected > 0:
        rebuild_curated()

    return CollectResponse(collected=collected, failed=failed)

async def scheduled_job():
    print(f"[scheduler] Rodando em {datetime.utcnow().isoformat()}")
    result = await collect_cities(DEFAULT_CITIES)
    print(f"[scheduler] Coletados: {result.collected} | Falhas: {result.failed}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        scheduled_job,
        "interval",
        minutes= settings.collect_interval_minutes,
        id= "weather_job"
    )
    scheduler.start()
    await scheduled_job()
    yield
    scheduler.shutdown()

app= FastAPI(title= "Weather API", lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.utcnow()}

@app.post("/collect", response_model= CollectResponse)
async def collect(request: CollectRequest):
    result = await collect_cities(request.cities)
    if result.collected == 0:
        raise HTTPException(status_code=422, detail=f"Falhas: {result.failed}")
    return result

@app.get("/status")
async def status():
    job = scheduler.get_job("weather_job")
    return {
        "next_run": str(job.next_run_time),
        "interval_minutes": settings.collect_interval_minutes
    }