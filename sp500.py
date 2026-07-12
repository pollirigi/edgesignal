"""
Universo de acciones del S&P 500 con su sector.

Es un subconjunto curado de los componentes más relevantes del índice,
organizado por sector para alimentar el screener y la landing.
Podés ampliarlo libremente agregando más tuplas (símbolo, nombre, sector).

Sectores usados (en español, para los filtros de la UI):
  Tecnología, Salud, Finanzas, Consumo Discrecional, Consumo Básico,
  Energía, Industrial, Comunicaciones, Servicios Públicos, Materiales, Inmobiliario
"""

# (símbolo, nombre de empresa, sector)
SP500 = [
    # --- Tecnología ---
    ("AAPL", "Apple Inc.", "Tecnología"),
    ("MSFT", "Microsoft Corporation", "Tecnología"),
    ("NVDA", "NVIDIA Corporation", "Tecnología"),
    ("AVGO", "Broadcom Inc.", "Tecnología"),
    ("ORCL", "Oracle Corporation", "Tecnología"),
    ("CRM", "Salesforce Inc.", "Tecnología"),
    ("ADBE", "Adobe Inc.", "Tecnología"),
    ("AMD", "Advanced Micro Devices", "Tecnología"),
    ("ACN", "Accenture plc", "Tecnología"),
    ("CSCO", "Cisco Systems Inc.", "Tecnología"),
    ("INTC", "Intel Corporation", "Tecnología"),
    ("IBM", "IBM Corporation", "Tecnología"),
    ("QCOM", "Qualcomm Inc.", "Tecnología"),
    ("TXN", "Texas Instruments", "Tecnología"),
    ("NOW", "ServiceNow Inc.", "Tecnología"),
    ("INTU", "Intuit Inc.", "Tecnología"),
    ("AMAT", "Applied Materials", "Tecnología"),
    ("MU", "Micron Technology", "Tecnología"),
    ("LRCX", "Lam Research", "Tecnología"),
    ("KLAC", "KLA Corporation", "Tecnología"),
    ("PANW", "Palo Alto Networks", "Tecnología"),

    # --- Comunicaciones ---
    ("GOOGL", "Alphabet Inc. Class A", "Comunicaciones"),
    ("META", "Meta Platforms Inc.", "Comunicaciones"),
    ("NFLX", "Netflix Inc.", "Comunicaciones"),
    ("DIS", "Walt Disney Company", "Comunicaciones"),
    ("CMCSA", "Comcast Corporation", "Comunicaciones"),
    ("T", "AT&T Inc.", "Comunicaciones"),
    ("VZ", "Verizon Communications", "Comunicaciones"),
    ("TMUS", "T-Mobile US Inc.", "Comunicaciones"),
    ("CHTR", "Charter Communications", "Comunicaciones"),
    ("EA", "Electronic Arts", "Comunicaciones"),

    # --- Consumo Discrecional ---
    ("AMZN", "Amazon.com Inc.", "Consumo Discrecional"),
    ("TSLA", "Tesla Inc.", "Consumo Discrecional"),
    ("HD", "Home Depot Inc.", "Consumo Discrecional"),
    ("MCD", "McDonald's Corporation", "Consumo Discrecional"),
    ("NKE", "Nike Inc.", "Consumo Discrecional"),
    ("LOW", "Lowe's Companies", "Consumo Discrecional"),
    ("SBUX", "Starbucks Corporation", "Consumo Discrecional"),
    ("BKNG", "Booking Holdings", "Consumo Discrecional"),
    ("TJX", "TJX Companies", "Consumo Discrecional"),
    ("GM", "General Motors", "Consumo Discrecional"),
    ("F", "Ford Motor Company", "Consumo Discrecional"),
    ("MAR", "Marriott International", "Consumo Discrecional"),

    # --- Consumo Básico ---
    ("WMT", "Walmart Inc.", "Consumo Básico"),
    ("PG", "Procter & Gamble", "Consumo Básico"),
    ("KO", "Coca-Cola Company", "Consumo Básico"),
    ("PEP", "PepsiCo Inc.", "Consumo Básico"),
    ("COST", "Costco Wholesale", "Consumo Básico"),
    ("MDLZ", "Mondelez International", "Consumo Básico"),
    ("PM", "Philip Morris International", "Consumo Básico"),
    ("CL", "Colgate-Palmolive", "Consumo Básico"),
    ("TGT", "Target Corporation", "Consumo Básico"),
    ("KHC", "Kraft Heinz Company", "Consumo Básico"),

    # --- Salud ---
    ("UNH", "UnitedHealth Group", "Salud"),
    ("JNJ", "Johnson & Johnson", "Salud"),
    ("LLY", "Eli Lilly and Company", "Salud"),
    ("ABBV", "AbbVie Inc.", "Salud"),
    ("MRK", "Merck & Co.", "Salud"),
    ("PFE", "Pfizer Inc.", "Salud"),
    ("TMO", "Thermo Fisher Scientific", "Salud"),
    ("ABT", "Abbott Laboratories", "Salud"),
    ("DHR", "Danaher Corporation", "Salud"),
    ("BMY", "Bristol-Myers Squibb", "Salud"),
    ("AMGN", "Amgen Inc.", "Salud"),
    ("GILD", "Gilead Sciences", "Salud"),
    ("CVS", "CVS Health", "Salud"),
    ("MDT", "Medtronic plc", "Salud"),
    ("ISRG", "Intuitive Surgical", "Salud"),

    # --- Finanzas ---
    ("BRK-B", "Berkshire Hathaway B", "Finanzas"),
    ("JPM", "JPMorgan Chase & Co.", "Finanzas"),
    ("V", "Visa Inc.", "Finanzas"),
    ("MA", "Mastercard Inc.", "Finanzas"),
    ("BAC", "Bank of America", "Finanzas"),
    ("WFC", "Wells Fargo & Company", "Finanzas"),
    ("GS", "Goldman Sachs Group", "Finanzas"),
    ("MS", "Morgan Stanley", "Finanzas"),
    ("AXP", "American Express", "Finanzas"),
    ("BLK", "BlackRock Inc.", "Finanzas"),
    ("C", "Citigroup Inc.", "Finanzas"),
    ("SCHW", "Charles Schwab", "Finanzas"),
    ("SPGI", "S&P Global Inc.", "Finanzas"),
    ("PYPL", "PayPal Holdings", "Finanzas"),

    # --- Energía ---
    ("XOM", "Exxon Mobil Corporation", "Energía"),
    ("CVX", "Chevron Corporation", "Energía"),
    ("COP", "ConocoPhillips", "Energía"),
    ("SLB", "Schlumberger Limited", "Energía"),
    ("EOG", "EOG Resources", "Energía"),
    ("MPC", "Marathon Petroleum", "Energía"),
    ("PSX", "Phillips 66", "Energía"),
    ("OXY", "Occidental Petroleum", "Energía"),
    ("VLO", "Valero Energy", "Energía"),

    # --- Industrial ---
    ("CAT", "Caterpillar Inc.", "Industrial"),
    ("BA", "Boeing Company", "Industrial"),
    ("HON", "Honeywell International", "Industrial"),
    ("GE", "General Electric", "Industrial"),
    ("UPS", "United Parcel Service", "Industrial"),
    ("RTX", "RTX Corporation", "Industrial"),
    ("DE", "Deere & Company", "Industrial"),
    ("LMT", "Lockheed Martin", "Industrial"),
    ("UNP", "Union Pacific", "Industrial"),
    ("MMM", "3M Company", "Industrial"),
    ("FDX", "FedEx Corporation", "Industrial"),

    # --- Servicios Públicos ---
    ("NEE", "NextEra Energy", "Servicios Públicos"),
    ("DUK", "Duke Energy", "Servicios Públicos"),
    ("SO", "Southern Company", "Servicios Públicos"),
    ("D", "Dominion Energy", "Servicios Públicos"),
    ("AEP", "American Electric Power", "Servicios Públicos"),

    # --- Materiales ---
    ("LIN", "Linde plc", "Materiales"),
    ("SHW", "Sherwin-Williams", "Materiales"),
    ("FCX", "Freeport-McMoRan", "Materiales"),
    ("NEM", "Newmont Corporation", "Materiales"),
    ("APD", "Air Products and Chemicals", "Materiales"),
    ("DOW", "Dow Inc.", "Materiales"),

    # --- Inmobiliario ---
    ("PLD", "Prologis Inc.", "Inmobiliario"),
    ("AMT", "American Tower", "Inmobiliario"),
    ("EQIX", "Equinix Inc.", "Inmobiliario"),
    ("PSA", "Public Storage", "Inmobiliario"),
    ("SPG", "Simon Property Group", "Inmobiliario"),
]

# Diccionarios auxiliares de búsqueda rápida.
SYMBOL_TO_NAME = {s: n for s, n, _ in SP500}
SYMBOL_TO_SECTOR = {s: sec for s, _, sec in SP500}
SECTORS = sorted({sec for _, _, sec in SP500})


def search(query):
    """Devuelve coincidencias por símbolo o nombre de empresa (case-insensitive)."""
    q = (query or "").strip().lower()
    if not q:
        return []
    out = []
    for sym, name, sector in SP500:
        if q in sym.lower() or q in name.lower():
            out.append({"symbol": sym, "name": name, "sector": sector})
    return out
