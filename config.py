"""Configuración central de EdgeSignal."""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _database_uri():
    """Usa Postgres si DATABASE_URL está seteada (Render), si no cae a SQLite local."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        return "sqlite:///" + os.path.join(BASE_DIR, "edgesignal.db")
    # Render (como Heroku) provee "postgres://", pero SQLAlchemy 1.4+ exige "postgresql://"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    # Cambiá esto en producción (variable de entorno EDGESIGNAL_SECRET)
    SECRET_KEY = os.environ.get("EDGESIGNAL_SECRET", "dev-secret-change-me-in-prod")

    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Tiempo de caché de datos de Yahoo Finance (segundos). 15 minutos por defecto.
    CACHE_TTL = int(os.environ.get("EDGESIGNAL_CACHE_TTL", 15 * 60))

    # Cuántos tickers escanea el screener / landing como máximo en una pasada.
    # Bajalo si tu conexión a Yahoo Finance es lenta.
    SCAN_UNIVERSE_LIMIT = int(os.environ.get("EDGESIGNAL_SCAN_LIMIT", 120))

    # Hilos concurrentes para descargar datos en paralelo.
    MAX_WORKERS = int(os.environ.get("EDGESIGNAL_WORKERS", 8))
