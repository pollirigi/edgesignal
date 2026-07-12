"""
EdgeSignal — Plataforma de inteligencia de mercado para el S&P 500.

Ejecutar localmente:
    python app.py

Luego abrir http://127.0.0.1:5000
"""
import csv
import io
import re

from flask import (
    Flask, Response, jsonify, redirect, render_template, request, url_for, flash,
)
from flask_login import (
    LoginManager, current_user, login_required, login_user, logout_user,
)

import analysis
import cache
from config import Config
from models import User, WatchlistItem, db
from sp500 import SECTORS, SP500, search

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Iniciá sesión para acceder a esa sección."
login_manager.login_message_category = "warning"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# --------------------------------------------------------------------------- #
# Escaneo del universo (cacheado)
# --------------------------------------------------------------------------- #
def scan_universe():
    """Analiza el universo del S&P 500 (limitado por config) y cachea el resultado."""
    cached = cache.get("scan:universe")
    if cached is not None:
        return cached
    symbols = [s for s, _, _ in SP500][: Config.SCAN_UNIVERSE_LIMIT]
    results = analysis.scan(symbols)
    results.sort(key=lambda r: r["score"], reverse=True)
    cache.set("scan:universe", results)
    return results


# --------------------------------------------------------------------------- #
# Páginas
# --------------------------------------------------------------------------- #
@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/screener")
@login_required
def screener():
    return render_template("screener.html", sectors=SECTORS)


@app.route("/stock/<symbol>")
@login_required
def stock_detail(symbol):
    return render_template("stock.html", symbol=symbol.upper())


@app.route("/profile")
@login_required
def profile():
    count = current_user.watchlist.count()
    return render_template("profile.html", watch_count=count)


# --------------------------------------------------------------------------- #
# Autenticación
# --------------------------------------------------------------------------- #
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        if not EMAIL_RE.match(email):
            flash("Ingresá un email válido.", "error")
        elif len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "error")
        elif User.query.filter_by(email=email).first():
            flash("Ya existe una cuenta con ese email.", "error")
        else:
            user = User(email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            return redirect(url_for("dashboard"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_url = request.args.get("next")
            return redirect(next_url or url_for("dashboard"))
        flash("Email o contraseña incorrectos.", "error")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("landing"))


# --------------------------------------------------------------------------- #
# API: análisis y datos de mercado
# --------------------------------------------------------------------------- #
@app.route("/api/top")
def api_top():
    """Top 10 acciones con mayor Score de Oportunidad (landing pública)."""
    results = scan_universe()
    return jsonify(results[:10])


@app.route("/api/search")
def api_search():
    return jsonify(search(request.args.get("q", "")))


@app.route("/api/analyze/<symbol>")
def api_analyze(symbol):
    try:
        return jsonify(analysis.analyze(symbol))
    except analysis.SymbolError as exc:
        return jsonify({"error": str(exc)}), 404


@app.route("/api/candles/<symbol>")
def api_candles(symbol):
    try:
        return jsonify(analysis.get_candles(symbol))
    except analysis.SymbolError as exc:
        return jsonify({"error": str(exc)}), 404


@app.route("/api/screener")
@login_required
def api_screener():
    """Filtra el universo del S&P 500 según los parámetros del screener."""
    def to_float(name, default):
        try:
            v = request.args.get(name)
            return float(v) if v not in (None, "") else default
        except ValueError:
            return default

    score_min = to_float("score_min", 0)
    rsi_max = to_float("rsi_max", 100)
    deviation_min = to_float("deviation_min", 0)  # caída mínima (%) respecto al promedio
    sector = request.args.get("sector") or ""

    results = scan_universe()
    filtered = []
    for r in results:
        if r["score"] < score_min:
            continue
        if r["rsi"] > rsi_max:
            continue
        # deviation_pct negativo = por debajo del promedio. "caída mínima del X%"
        if r["deviation_pct"] > -deviation_min:
            continue
        if sector and r["sector"] != sector:
            continue
        filtered.append(r)
    return jsonify(filtered)


# --------------------------------------------------------------------------- #
# API: watchlist (privada)
# --------------------------------------------------------------------------- #
@app.route("/api/watchlist", methods=["GET"])
@login_required
def api_watchlist():
    items = current_user.watchlist.order_by(WatchlistItem.added_at).all()
    out = []
    for item in items:
        try:
            out.append(analysis.analyze(item.symbol))
        except analysis.SymbolError:
            out.append({"symbol": item.symbol, "error": "Datos no disponibles"})
    out.sort(key=lambda r: r.get("score", -1), reverse=True)
    return jsonify(out)


@app.route("/api/watchlist", methods=["POST"])
@login_required
def api_watchlist_add():
    data = request.get_json(silent=True) or {}
    symbol = (data.get("symbol") or "").upper().strip()
    if not symbol:
        return jsonify({"error": "Símbolo requerido."}), 400
    # Validamos que exista antes de guardarlo.
    try:
        analysis.analyze(symbol)
    except analysis.SymbolError as exc:
        return jsonify({"error": str(exc)}), 404

    exists = current_user.watchlist.filter_by(symbol=symbol).first()
    if exists:
        return jsonify({"ok": True, "message": "Ya estaba en tu watchlist."})
    db.session.add(WatchlistItem(user_id=current_user.id, symbol=symbol))
    db.session.commit()
    return jsonify({"ok": True})


@app.route("/api/watchlist/<symbol>", methods=["DELETE"])
@login_required
def api_watchlist_remove(symbol):
    symbol = symbol.upper().strip()
    item = current_user.watchlist.filter_by(symbol=symbol).first()
    if item:
        db.session.delete(item)
        db.session.commit()
    return jsonify({"ok": True})


@app.route("/api/watchlist/export.csv")
@login_required
def api_watchlist_export():
    items = current_user.watchlist.order_by(WatchlistItem.added_at).all()
    rows = []
    for item in items:
        try:
            rows.append(analysis.analyze(item.symbol))
        except analysis.SymbolError:
            continue
    rows.sort(key=lambda r: r["score"], reverse=True)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "Simbolo", "Empresa", "Sector", "Precio", "Score",
        "Desviacion_%", "RSI", "Bollinger_%b", "Min_52s", "Max_52s", "Posicion_rango_%",
    ])
    for r in rows:
        writer.writerow([
            r["symbol"], r["name"], r["sector"], r["price"], r["score"],
            r["deviation_pct"], r["rsi"], r["bollinger"]["percent_b"],
            r["low_52w"], r["high_52w"], r["range_position"],
        ])
    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=edgesignal_watchlist.csv"},
    )


# --------------------------------------------------------------------------- #
# Errores
# --------------------------------------------------------------------------- #
@app.errorhandler(404)
def not_found(_e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "No encontrado"}), 404
    return render_template("404.html"), 404


def init_db():
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
