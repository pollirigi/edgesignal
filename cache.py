"""Caché simple en memoria con TTL (thread-safe) para datos de Yahoo Finance."""
import threading
import time

from config import Config

_store = {}
_lock = threading.Lock()


def get(key):
    """Devuelve el valor cacheado si sigue vigente, o None."""
    with _lock:
        item = _store.get(key)
        if not item:
            return None
        value, expires_at = item
        if time.time() > expires_at:
            _store.pop(key, None)
            return None
        return value


def set(key, value, ttl=None):
    """Guarda un valor con un TTL (segundos). Usa el TTL global por defecto."""
    ttl = Config.CACHE_TTL if ttl is None else ttl
    with _lock:
        _store[key] = (value, time.time() + ttl)


def get_or_set(key, producer, ttl=None):
    """Devuelve lo cacheado o ejecuta producer(), cachea el resultado y lo devuelve."""
    cached = get(key)
    if cached is not None:
        return cached
    value = producer()
    if value is not None:
        set(key, value, ttl)
    return value


def clear():
    with _lock:
        _store.clear()
