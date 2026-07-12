/* Página de detalle de una acción */
(async function () {
  const root = document.getElementById('detail-root');
  const symbol = root.dataset.symbol;
  const errorEl = document.getElementById('detail-error');
  const skeleton = document.getElementById('detail-skeleton');
  const card = document.getElementById('detail-card');

  function fail(msg) {
    skeleton.hidden = true;
    errorEl.hidden = false;
    errorEl.textContent = '⚠️ ' + msg;
  }

  let d;
  try {
    d = await fetchJSON('/api/analyze/' + encodeURIComponent(symbol));
  } catch (e) {
    return fail('No se pudo analizar ' + symbol + ': ' + e.message);
  }

  document.getElementById('d-name').textContent = d.name + ' · ' + d.sector;
  document.getElementById('d-score').textContent = d.score;
  document.getElementById('d-score').style.color = scoreColor(d.score);
  const verdict = scoreVerdict(d.score);
  const vEl = document.getElementById('d-verdict');
  vEl.textContent = verdict.text; vEl.style.color = verdict.color;
  document.getElementById('d-indicators').innerHTML = buildIndicators(d);

  skeleton.hidden = true;
  card.hidden = false;

  renderGauge(document.getElementById('d-gauge'), d.score);

  // Botón agregar a watchlist
  document.getElementById('d-add').addEventListener('click', async (e) => {
    const btn = e.currentTarget;
    btn.disabled = true;
    try {
      await fetchJSON('/api/watchlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol }),
      });
      btn.textContent = '✓ En tu watchlist';
    } catch (err) {
      btn.textContent = 'Error';
      btn.disabled = false;
    }
  });

  // Velas
  try {
    const cd = await fetchJSON('/api/candles/' + encodeURIComponent(symbol));
    renderCandles(document.getElementById('d-chart'), cd);
  } catch (_) {
    document.getElementById('d-chart').closest('.chart-col').innerHTML = '<p class="muted">Gráfico no disponible.</p>';
  }
})();
