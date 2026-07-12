"""
Motor de análisis estadístico de EdgeSignal.

Calcula, para cada acción del S&P 500:
  1. Desviación del promedio histórico de 52 semanas.
  2. Bandas de Bollinger (20 días, 2 desviaciones estándar).
  3. RSI (Índice de Fuerza Relativa, 14 días).
  4. Score de Oportunidad (1-100) combinando los tres anteriores.
  5. Posición dentro del rango máximo/mínimo de 52 semanas.

Todos los datos se descargan con yfinance y se cachean según Config.CACHE_TTL.
"""
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import yfinance as yf

import cache
from config import Config
from sp500 import SYMBOL_TO_NAME, SYMBOL_TO_SECTOR

# Sesión que imita un navegador real (curl_cffi). Yahoo Finance limita (HTTP 429)
# las peticiones que parecen automatizadas; un fingerprint de Chrome reduce el bloqueo.
# Si curl_cffi no está instalado, caemos a la sesión por defecto de yfinance.
try:
    from curl_cffi import requests as _curl_requests

    _SESSION = _curl_requests.Session(impersonate="chrome")
except Exception:  # noqa: BLE001
    _SESSION = None

# Reintentos ante rate-limiting (429) o fallos transitorios de red.
_MAX_RETRIES = 3
_RETRY_BACKOFF = 1.5  # segundos base; crece de forma exponencial

# --- Parámetros de los indicadores ---
RSI_PERIOD = 14
BOLLINGER_PERIOD = 20
BOLLINGER_STD = 2

# Umbrales de alerta
DEVIATION_ALERT = -10.0  # caída del 10% bajo el promedio
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# Pesos del Score de Oportunidad
W_DEVIATION = 0.35
W_RSI = 0.35
W_BOLLINGER = 0.30


class SymbolError(Exception):
    """El símbolo no existe o no hay datos disponibles."""


# --------------------------------------------------------------------------- #
# Descarga de datos
# --------------------------------------------------------------------------- #
def _download_history(symbol):
    """Descarga 1 año de datos diarios, con reintentos ante rate-limiting (429).

    Lanza SymbolError si el símbolo no existe o no hay datos tras los reintentos.
    """
    last_exc = None
    for attempt in range(_MAX_RETRIES):
        try:
            kwargs = {"session": _SESSION} if _SESSION is not None else {}
            ticker = yf.Ticker(symbol, **kwargs)
            hist = ticker.history(period="1y", interval="1d", auto_adjust=True)
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            hist = None

        if hist is not None and not hist.empty and "Close" in hist:
            hist = hist.dropna(subset=["Close"])
            if len(hist) < BOLLINGER_PERIOD + 1:
                raise SymbolError(f"Datos insuficientes para analizar '{symbol}'.")
            return hist

        # Sin datos: esperamos con backoff exponencial antes de reintentar.
        if attempt < _MAX_RETRIES - 1:
            time.sleep(_RETRY_BACKOFF * (2 ** attempt))

    if last_exc is not None:
        raise SymbolError(f"No se pudieron obtener datos para {symbol}: {last_exc}")
    raise SymbolError(f"El símbolo '{symbol}' no existe o no tiene datos.")


def get_history(symbol):
    """Versión cacheada de la descarga (DataFrame serializado a dict)."""
    symbol = symbol.upper().strip()
    key = f"hist:{symbol}"
    cached = cache.get(key)
    if cached is not None:
        return pd.DataFrame(cached)

    hist = _download_history(symbol)
    # Guardamos como dict de columnas + índice ISO para poder cachear/serializar.
    payload = {col: hist[col].tolist() for col in ["Open", "High", "Low", "Close", "Volume"]}
    payload["Date"] = [d.strftime("%Y-%m-%d") for d in hist.index]
    cache.set(key, payload)

    df = pd.DataFrame(payload)
    return df


# --------------------------------------------------------------------------- #
# Indicadores individuales
# --------------------------------------------------------------------------- #
def compute_rsi(close, period=RSI_PERIOD):
    """RSI de Wilder. Devuelve la serie completa."""
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


def compute_bollinger(close, period=BOLLINGER_PERIOD, num_std=BOLLINGER_STD):
    """Devuelve (banda_media, banda_superior, banda_inferior) como series."""
    sma = close.rolling(period).mean()
    std = close.rolling(period).std()
    upper = sma + num_std * std
    lower = sma - num_std * std
    return sma, upper, lower


# --------------------------------------------------------------------------- #
# Sub-scores (cada uno 0-100, mayor = más "barata" históricamente)
# --------------------------------------------------------------------------- #
def _deviation_score(deviation_pct):
    # -20% o menos → 100 ; 0% → 50 ; +20% o más → 0
    return float(np.clip(50 - deviation_pct * 2.5, 0, 100))


def _rsi_score(rsi):
    # RSI bajo (sobreventa) → score alto
    return float(np.clip(100 - rsi, 0, 100))


def _bollinger_score(percent_b):
    # %b = posición entre banda inferior (0) y superior (1).
    # Debajo de la inferior (<0) → 100 ; en la superior (1) → 0.
    return float(np.clip(100 - percent_b * 100, 0, 100))


# --------------------------------------------------------------------------- #
# Análisis completo de una acción
# --------------------------------------------------------------------------- #
def analyze(symbol):
    """Devuelve un dict con todos los indicadores y el Score de Oportunidad."""
    symbol = symbol.upper().strip()
    key = f"analysis:{symbol}"
    cached = cache.get(key)
    if cached is not None:
        return cached

    df = get_history(symbol)
    close = pd.Series(df["Close"], dtype="float64")

    current = float(close.iloc[-1])
    mean_52 = float(close.mean())
    high_52 = float(close.max())
    low_52 = float(close.min())

    # 1. Desviación del promedio histórico
    deviation_pct = (current - mean_52) / mean_52 * 100

    # 2. Bandas de Bollinger
    sma, upper, lower = compute_bollinger(close)
    lower_band = float(lower.iloc[-1])
    upper_band = float(upper.iloc[-1])
    mid_band = float(sma.iloc[-1])
    band_width = upper_band - lower_band
    percent_b = (current - lower_band) / band_width if band_width else 0.5

    # 3. RSI
    rsi = float(compute_rsi(close).iloc[-1])

    # 5. Posición en el rango de 52 semanas (0 = mínimo, 100 = máximo)
    range_span = high_52 - low_52
    range_position = (current - low_52) / range_span * 100 if range_span else 50

    # 4. Score de Oportunidad
    s_dev = _deviation_score(deviation_pct)
    s_rsi = _rsi_score(rsi)
    s_boll = _bollinger_score(percent_b)
    score = int(round(
        np.clip(s_dev * W_DEVIATION + s_rsi * W_RSI + s_boll * W_BOLLINGER, 1, 100)
    ))

    result = {
        "symbol": symbol,
        "name": SYMBOL_TO_NAME.get(symbol, symbol),
        "sector": SYMBOL_TO_SECTOR.get(symbol, "—"),
        "price": round(current, 2),
        "mean_52w": round(mean_52, 2),
        "high_52w": round(high_52, 2),
        "low_52w": round(low_52, 2),
        "deviation_pct": round(deviation_pct, 2),
        "range_position": round(range_position, 1),
        "rsi": round(rsi, 1),
        "bollinger": {
            "lower": round(lower_band, 2),
            "mid": round(mid_band, 2),
            "upper": round(upper_band, 2),
            "percent_b": round(percent_b * 100, 1),
            "below_lower": current < lower_band,
        },
        "score": score,
        "subscores": {
            "deviation": round(s_dev, 1),
            "rsi": round(s_rsi, 1),
            "bollinger": round(s_boll, 1),
        },
        "alerts": {
            "deviation": deviation_pct <= DEVIATION_ALERT,
            "rsi_oversold": rsi < RSI_OVERSOLD,
            "below_lower_band": current < lower_band,
        },
    }
    cache.set(key, result)
    return result


def get_candles(symbol):
    """Devuelve velas OHLC del último año para Chart.js + serie de Bollinger."""
    symbol = symbol.upper().strip()
    df = get_history(symbol)
    close = pd.Series(df["Close"], dtype="float64")
    sma, upper, lower = compute_bollinger(close)

    candles = []
    for i in range(len(df)):
        candles.append({
            "t": df["Date"][i],
            "o": round(float(df["Open"][i]), 2),
            "h": round(float(df["High"][i]), 2),
            "l": round(float(df["Low"][i]), 2),
            "c": round(float(df["Close"][i]), 2),
        })
    bollinger = {
        "mid": [None if pd.isna(v) else round(float(v), 2) for v in sma],
        "upper": [None if pd.isna(v) else round(float(v), 2) for v in upper],
        "lower": [None if pd.isna(v) else round(float(v), 2) for v in lower],
    }
    return {"candles": candles, "bollinger": bollinger}


# --------------------------------------------------------------------------- #
# Escaneo masivo (paralelo) para landing y screener
# --------------------------------------------------------------------------- #
def _safe_analyze(symbol):
    try:
        return analyze(symbol)
    except Exception:  # noqa: BLE001
        return None


def scan(symbols):
    """Analiza una lista de símbolos en paralelo. Ignora los que fallan."""
    results = []
    with ThreadPoolExecutor(max_workers=Config.MAX_WORKERS) as pool:
        for res in pool.map(_safe_analyze, symbols):
            if res is not None:
                results.append(res)
    return results
