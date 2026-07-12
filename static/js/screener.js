/* Screener: filtros + tabla ordenable + filas clickeables */
(function () {
  const body = document.getElementById('screener-body');
  const countEl = document.getElementById('result-count');
  let rows = [];
  let sortKey = 'score';
  let sortDir = -1; // -1 desc, 1 asc

  // Sliders en vivo
  const sliders = [['f-score', 'f-score-out'], ['f-rsi', 'f-rsi-out'], ['f-dev', 'f-dev-out']];
  sliders.forEach(([inp, out]) => {
    const el = document.getElementById(inp);
    const o = document.getElementById(out);
    el.addEventListener('input', () => { o.textContent = el.value; });
  });

  async function apply() {
    const params = new URLSearchParams({
      score_min: document.getElementById('f-score').value,
      rsi_max: document.getElementById('f-rsi').value,
      deviation_min: document.getElementById('f-dev').value,
      sector: document.getElementById('f-sector').value,
    });
    body.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:2rem;"><span class="spin"></span> Escaneando el S&P 500…</td></tr>';
    try {
      rows = await fetchJSON('/api/screener?' + params.toString());
      render();
    } catch (e) {
      body.innerHTML = `<tr><td colspan="8" class="empty-state">Error: ${e.message}</td></tr>`;
    }
  }

  function render() {
    countEl.textContent = `${rows.length} acción${rows.length === 1 ? '' : 'es'} coinciden con tus filtros.`;
    const sorted = [...rows].sort((a, b) => {
      const av = a[sortKey], bv = b[sortKey];
      if (typeof av === 'string') return av.localeCompare(bv) * sortDir;
      return (av - bv) * sortDir;
    });
    if (!sorted.length) {
      body.innerHTML = '<tr><td colspan="8" class="empty-state">Ninguna acción cumple esos criterios. Probá relajar los filtros.</td></tr>';
      return;
    }
    body.innerHTML = sorted.map((r) => `
      <tr class="clickable" onclick="location.href='/stock/${r.symbol}'">
        <td class="mono"><strong>${r.symbol}</strong></td>
        <td>${r.name}</td>
        <td class="muted">${r.sector}</td>
        <td class="num">${fmt.money(r.price)}</td>
        <td class="num ${r.deviation_pct < 0 ? 'neg' : 'pos'}">${fmt.pct(r.deviation_pct)}</td>
        <td class="num">${fmt.num(r.rsi)}</td>
        <td class="num">${fmt.num(r.range_position)}%</td>
        <td class="num"><span class="score-badge" style="color:${scoreColor(r.score)}">${r.score}</span></td>
      </tr>`).join('');
  }

  // Ordenamiento por columna
  document.querySelectorAll('#screener-table thead th[data-key]').forEach((th) => {
    th.addEventListener('click', () => {
      const key = th.dataset.key;
      if (sortKey === key) sortDir *= -1; else { sortKey = key; sortDir = (key === 'score') ? -1 : 1; }
      document.querySelectorAll('#screener-table thead th').forEach((h) => {
        h.textContent = h.textContent.replace(/ [▲▼]$/, '');
      });
      th.textContent += sortDir === -1 ? ' ▼' : ' ▲';
      render();
    });
  });

  document.getElementById('apply-btn').addEventListener('click', apply);
  apply(); // carga inicial
})();
