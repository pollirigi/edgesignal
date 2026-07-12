/* Gráficos de EdgeSignal: velas japonesas + gauge circular */

Chart.defaults.color = '#8b8b9a';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';

// Devuelve el controlador si está registrado, o null (sin lanzar excepción).
function safeGet(key) {
  try { return Chart.registry.getController(key); } catch (_) { return null; }
}

// Renderiza velas japonesas del último año + Bandas de Bollinger superpuestas.
function renderCandles(canvas, data) {
  const candles = data.candles.map((c) => ({
    x: luxon.DateTime.fromISO(c.t).toMillis(),
    o: c.o, h: c.h, l: c.l, c: c.c,
  }));
  const x = candles.map((c) => c.x);
  const bands = (arr) => arr.map((v, i) => (v === null ? null : { x: x[i], y: v }));

  const useCandles = safeGet('candlestick') !== null;

  const datasets = [
    {
      label: 'Banda superior', type: 'line', data: bands(data.bollinger.upper),
      borderColor: 'rgba(0,255,136,0.25)', borderWidth: 1, pointRadius: 0,
      borderDash: [4, 4], fill: false, tension: 0.2,
    },
    {
      label: 'Banda inferior', type: 'line', data: bands(data.bollinger.lower),
      borderColor: 'rgba(255,68,68,0.3)', borderWidth: 1, pointRadius: 0,
      borderDash: [4, 4], fill: false, tension: 0.2,
    },
    {
      label: 'Media (20)', type: 'line', data: bands(data.bollinger.mid),
      borderColor: 'rgba(255,255,255,0.25)', borderWidth: 1, pointRadius: 0,
      fill: false, tension: 0.2,
    },
  ];

  if (useCandles) {
    datasets.unshift({
      label: 'Precio', type: 'candlestick', data: candles,
      color: { up: '#00ff88', down: '#ff4444', unchanged: '#8b8b9a' },
      borderColor: { up: '#00ff88', down: '#ff4444', unchanged: '#8b8b9a' },
    });
  } else {
    // Fallback: línea de cierre coloreada si el plugin de velas no cargó.
    datasets.unshift({
      label: 'Cierre', type: 'line', data: candles.map((c) => ({ x: c.x, y: c.c })),
      borderColor: '#00ff88', borderWidth: 1.5, pointRadius: 0, fill: false, tension: 0.15,
    });
  }

  return new Chart(canvas, {
    type: useCandles ? 'candlestick' : 'line',
    data: { datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      animation: { duration: 900, easing: 'easeOutQuart' },
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1c1c26', borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1,
          padding: 10, displayColors: false,
        },
      },
      scales: {
        x: { type: 'time', time: { unit: 'month' }, grid: { display: false }, ticks: { maxRotation: 0 } },
        y: { position: 'right', grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { callback: (v) => '$' + v } },
      },
    },
  });
}

// Gauge circular animado del Score de Oportunidad (0-100).
function renderGauge(canvas, score) {
  const color = scoreColor(score);
  return new Chart(canvas, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [score, 100 - score],
        backgroundColor: [color, 'rgba(255,255,255,0.06)'],
        borderWidth: 0,
        circumference: 270,
        rotation: 225,
      }],
    },
    options: {
      responsive: false,
      cutout: '78%',
      animation: { animateRotate: true, duration: 1200, easing: 'easeOutCubic' },
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
    },
  });
}
