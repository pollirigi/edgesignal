# ◢ EdgeSignal

**Plataforma de inteligencia de mercado para el S&P 500.** Detecta acciones estadísticamente
"baratas" combinando desviación del promedio histórico, Bandas de Bollinger y RSI en un único
**Score de Oportunidad** del 1 al 100.

> ⚠️ **Aviso:** EdgeSignal es una herramienta **educativa** de análisis estadístico. No es
> asesoramiento financiero. El rendimiento pasado no garantiza resultados futuros.

---

## ✨ Características

- **Landing pública** con el Top 10 de oportunidades del S&P 500 en tiempo real.
- **Dashboard privado** con buscador, watchlist personal, gráficos de velas japonesas,
  gauge circular animado del Score y explicaciones simples de cada indicador.
- **Screener de mercado** con filtros por Score, sector, RSI y caída vs. promedio.
- **Exportación a CSV** de tu watchlist.
- **Autenticación** con email/contraseña (Flask-Login) y watchlist guardada por usuario en SQLite.
- **Tema oscuro premium** estilo Bloomberg Terminal, responsive, con glassmorphism y skeletons.
- **Caché de 15 minutos** de los datos de Yahoo Finance para no sobrecargar la API.

## 📊 Indicadores

| Indicador | Qué mide | Alerta |
|-----------|----------|--------|
| Desviación 52s | Precio actual vs. promedio de 52 semanas | Caída > 10% |
| Bandas de Bollinger | Precio vs. rango de volatilidad (20d, 2σ) | Bajo la banda inferior |
| RSI (14) | Momentum / sobreventa | RSI < 30 |
| Score de Oportunidad | Combinación ponderada de los 3 anteriores (1-100) | — |
| Rango 52 semanas | Posición entre mínimo y máximo anual | — |

El Score se calcula como:
`0.35 × desviación + 0.35 × RSI + 0.30 × Bollinger`, cada sub-score normalizado a 0-100.

---

## 🛠️ Stack

- **Backend:** Python + Flask, Flask-Login, Flask-SQLAlchemy
- **Datos:** yfinance + pandas + numpy
- **Base de datos:** SQLite
- **Frontend:** HTML, CSS y JavaScript vanilla + Chart.js (velas con `chartjs-chart-financial`)

---

## 🚀 Instalación paso a paso

Requiere **Python 3.10+**.

### 1. Posicionate en la carpeta del proyecto

```bash
cd EdgeSignal
```

### 2. Creá y activá un entorno virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
> Si PowerShell bloquea el script, ejecutá una vez:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalá las dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutá la app

```bash
python app.py
```

La base de datos `edgesignal.db` se crea automáticamente en el primer arranque.

### 5. Abrí el navegador

```
http://127.0.0.1:5000
```

Creá una cuenta, agregá acciones a tu watchlist y explorá el screener. 🎉

---

## ⚙️ Configuración (opcional)

Podés ajustar el comportamiento con variables de entorno antes de ejecutar:

| Variable | Por defecto | Descripción |
|----------|-------------|-------------|
| `EDGESIGNAL_SECRET` | `dev-secret-change-me-in-prod` | Clave secreta de sesión (cambiala en producción) |
| `EDGESIGNAL_CACHE_TTL` | `900` | Segundos de caché de datos (15 min) |
| `EDGESIGNAL_SCAN_LIMIT` | `120` | Máx. de tickers a escanear en landing/screener |
| `EDGESIGNAL_WORKERS` | `8` | Hilos concurrentes para descargar datos |

Ejemplo (PowerShell):
```powershell
$env:EDGESIGNAL_SCAN_LIMIT = "60"; python app.py
```

---

## 📁 Estructura del proyecto

```
EdgeSignal/
├── app.py              # App Flask: rutas, API, autenticación
├── analysis.py         # Motor de indicadores y Score de Oportunidad
├── models.py           # Modelos SQLAlchemy (User, WatchlistItem)
├── cache.py            # Caché en memoria con TTL
├── config.py           # Configuración
├── sp500.py            # Universo del S&P 500 (símbolo, nombre, sector)
├── requirements.txt
├── README.md
├── edgesignal.db       # SQLite (se crea solo)
├── templates/          # Jinja2: landing, dashboard, screener, stock, auth, perfil
└── static/
    ├── css/style.css   # Tema oscuro premium
    ├── js/             # common, charts, landing, dashboard, screener, detail
    └── favicon.svg
```

---

## ❓ Notas y solución de problemas

- **La primera carga del Top 10 / screener tarda unos segundos** porque descarga datos de
  ~120 acciones. Las siguientes son instantáneas gracias al caché de 15 minutos.
- **Yahoo Finance puede limitar las peticiones (rate limiting / HTTP 429).** EdgeSignal usa
  una sesión con fingerprint de navegador (`curl_cffi`) y reintenta con _backoff_ exponencial
  para mitigarlo. Aun así, si ves pocos resultados, bajá `EDGESIGNAL_SCAN_LIMIT` o esperá unos
  minutos.
- **Mantené `yfinance` actualizado.** Yahoo cambia su API con frecuencia y las versiones
  viejas dejan de traer datos (error típico: `Expecting value: line 1 column 1`). Si el Top 10
  aparece vacío, ejecutá `pip install --upgrade yfinance curl_cffi`.
- **Las velas japonesas** usan el plugin `chartjs-chart-financial` vía CDN. Si no carga
  (sin internet), el gráfico cae automáticamente a una línea de cierre.
- El universo del S&P 500 en `sp500.py` es un subconjunto curado de ~115 componentes
  principales; podés ampliarlo agregando tuplas `(símbolo, nombre, sector)`.

---

## 📄 Licencia

Proyecto educativo. Usalo y modificalo libremente.
```

🤖 Generado con [Claude Code](https://claude.com/claude-code)
