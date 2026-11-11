from fastapi import FastAPI

from anibattle.api.battles.router import router as battles_router
from anibattle.api.dependencies import lifespan
from anibattle.api.health.router import router as health_router

app: FastAPI = FastAPI(lifespan=lifespan)


app.include_router(battles_router)
app.include_router(health_router)
