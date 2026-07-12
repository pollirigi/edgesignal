/* Landing: carga el Top 10 de oportunidades */
(async function () {
  const body = document.getElementById('top-body');
  try {
    const rows = await (await fetch('/api/top')).json();
    if (!rows.length) {
      body.innerHTML = '<tr><td colspan="8" class="empty-state">No hay datos disponibles en este momento.</td></tr>';
      return;
    }
    body.innerHTML = rows.map((r, i) => `
      <tr>
        <td class="mono muted">${i + 1}</td>
        <td class="mono"><strong>${r.symbol}</strong></td>
        <td>${r.name}</td>
        <td class="muted">${r.sector}</td>
        <td class="num">${'$' + r.price.toFixed(2)}</td>
        <td class="num ${r.deviation_pct < 0 ? 'neg' : 'pos'}">${(r.deviation_pct > 0 ? '+' : '') + r.deviation_pct.toFixed(1)}%</td>
        <td class="num">${r.rsi.toFixed(0)}</td>
        <td class="num"><span class="score-badge" style="color:${score10Color(r.score)}">${r.score}</span></td>
      </tr>
    `).join('');
  } catch (e) {
    body.innerHTML = `<tr><td colspan="8" class="empty-state">No se pudieron cargar los datos: ${e.message}</td></tr>`;
  }

  function score10Color(s) {
    if (s >= 70) return '#00ff88';
    if (s >= 45) return '#ffb84d';
    return '#ff4444';
  }
})();
