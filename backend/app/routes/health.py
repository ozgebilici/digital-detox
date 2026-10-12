from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok", "app": "Dijital Arınma Sistemi API"}

@router.get("/")
def home():
    return {"message": "Dijital Arınma Sistemi Backend Servisine Hoş Geldiniz!"}
