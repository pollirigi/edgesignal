"""Configuración central de EdgeSignal."""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Cambiá esto en producción (variable de entorno EDGESIGNAL_SECRET)
    SECRET_KEY = os.environ.get("EDGESIGNAL_SECRET", "dev-secret-change-me-in-prod")

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "edgesignal.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Tiempo de caché de datos de Yahoo Finance (segundos). 15 minutos por defecto.
    CACHE_TTL = int(os.environ.get("EDGESIGNAL_CACHE_TTL", 15 * 60))

    # Cuántos tickers escanea el screener / landing como máximo en una pasada.
    # Bajalo si tu conexión a Yahoo Finance es lenta.
    SCAN_UNIVERSE_LIMIT = int(os.environ.get("EDGESIGNAL_SCAN_LIMIT", 120))

    # Hilos concurrentes para descargar datos en paralelo.
    MAX_WORKERS = int(os.environ.get("EDGESIGNAL_WORKERS", 8))
