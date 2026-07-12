/* Utilidades compartidas de EdgeSignal */

async function fetchJSON(url, opts) {
  const res = await fetch(url, opts);
  let data = null;
  try { data = await res.json(); } catch (_) { /* sin cuerpo */ }
  if (!res.ok) {
    const msg = (data && data.error) || `Error ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

const fmt = {
  money: (v) => '$' + Number(v).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
  pct: (v) => (v > 0 ? '+' : '') + Number(v).toFixed(2) + '%',
  num: (v, d = 1) => Number(v).toFixed(d),
};

// Color del score según rango
function scoreColor(score) {
  if (score >= 70) return '#00ff88';
  if (score >= 45) return '#ffb84d';
  return '#ff4444';
}

function scoreVerdict(score) {
  if (score >= 80) return { text: '🔥 Oportunidad fuerte', color: '#00ff88' };
  if (score >= 65) return { text: '✅ Estadísticamente barata', color: '#00ff88' };
  if (score >= 45) return { text: '➖ En su rango normal', color: '#ffb84d' };
  if (score >= 30) return { text: '⬆️ Algo cara', color: '#ffb84d' };
  return { text: '❌ Cara vs su historia', color: '#ff4444' };
}

// Textos de tooltips para usuarios no técnicos
const TIPS = {
  deviation: 'Compara el precio de hoy con el precio promedio del último año. Un número negativo grande significa que la acción está mucho más barata de lo habitual.',
  bollinger: 'Las Bandas de Bollinger marcan el rango "normal" de precios según su volatilidad reciente. Si el precio cae por debajo de la banda inferior, suele estar en zona de sobreventa.',
  rsi: 'El RSI mide la fuerza del movimiento de precios de 0 a 100. Por debajo de 30 la acción se considera "sobrevendida" (posible rebote); por encima de 70, "sobrecomprada".',
  range: 'Muestra en qué punto del recorrido del último año está el precio: 0% = mínimo anual, 100% = máximo anual.',
  score: 'Nuestro puntaje propietario de 1 a 100 que combina las tres señales. Cuanto más alto, más barata está la acción frente a su propia historia.',
};

function tip(key, label) {
  return `<span class="tip">${label}<span class="tip-box">${TIPS[key]}</span></span>`;
}

// Construye el bloque de 5 indicadores para una acción
function buildIndicators(d) {
  const b = d.bollinger;
  const a = d.alerts;
  return `
    <div class="indicator ${a.deviation ? 'alert' : ''}">
      <div class="ind-label">${tip('deviation', 'Desv. del promedio')}
        ${a.deviation ? '<span class="ind-tag tag-buy">OPORTUNIDAD</span>' : ''}</div>
      <div class="ind-value ${d.deviation_pct < 0 ? 'neg' : 'pos'}">${fmt.pct(d.deviation_pct)}</div>
      <div class="ind-sub">Promedio 52s: ${fmt.money(d.mean_52w)}</div>
    </div>

    <div class="indicator ${a.below_lower_band ? 'alert' : ''}">
      <div class="ind-label">${tip('bollinger', 'Bollinger')}
        ${a.below_lower_band ? '<span class="ind-tag tag-buy">SOBREVENTA</span>' : ''}</div>
      <div class="ind-value">${fmt.num(b.percent_b)}<span class="ind-sub">%b</span></div>
      <div class="ind-sub">Inf ${fmt.money(b.lower)} · Sup ${fmt.money(b.upper)}</div>
    </div>

    <div class="indicator ${a.rsi_oversold ? 'alert' : ''}">
      <div class="ind-label">${tip('rsi', 'RSI (14)')}
        ${a.rsi_oversold ? '<span class="ind-tag tag-buy">SOBREVENDIDA</span>' : ''}</div>
      <div class="ind-value">${fmt.num(d.rsi)}</div>
      <div class="ind-sub">${d.rsi < 30 ? 'Sobrevendida' : d.rsi > 70 ? 'Sobrecomprada' : 'Neutral'}</div>
    </div>

    <div class="indicator">
      <div class="ind-label">${tip('range', 'Rango 52 semanas')}</div>
      <div class="ind-value">${fmt.num(d.range_position)}%</div>
      <div class="range-bar"><span class="marker" style="left:${Math.min(100, Math.max(0, d.range_position))}%"></span></div>
      <div class="ind-sub">${fmt.money(d.low_52w)} – ${fmt.money(d.high_52w)}</div>
    </div>
  `;
}
