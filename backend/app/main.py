from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import health, auth, scan, requests

app = FastAPI(
    title="Dijital Arınma Sistemi API",
    description="Gmail verilerinizi tarayarak kayıtlı olduğunuz platformları bulan ve KVKK veri silme talepleri oluşturan backend API.",
    version="1.0.0",
)

origins = [
    settings.FRONTEND_URL,
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(scan.router)
app.include_router(requests.router)
