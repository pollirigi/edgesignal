/* Dashboard: búsqueda, watchlist, cards detalladas y comparativa */
(function () {
  const charts = {}; // symbol -> { candle, gauge }

  // ---------- Búsqueda con debounce ----------
  const searchInput = document.getElementById('search');
  const resultsBox = document.getElementById('search-results');
  let debounce;

  searchInput.addEventListener('input', () => {
    clearTimeout(debounce);
    const q = searchInput.value.trim();
    if (q.length < 1) { resultsBox.classList.remove('open'); return; }
    debounce = setTimeout(async () => {
      try {
        const items = await fetchJSON('/api/search?q=' + encodeURIComponent(q));
        if (!items.length) {
          resultsBox.innerHTML = '<div class="search-item muted">Sin resultados</div>';
        } else {
          resultsBox.innerHTML = items.slice(0, 8).map((it) => `
            <div class="search-item" data-symbol="${it.symbol}">
              <span><span class="sym">${it.symbol}</span> · ${it.name}</span>
              <span class="sec">${it.sector}</span>
            </div>`).join('');
        }
        resultsBox.classList.add('open');
      } catch (_) { /* ignore */ }
    }, 200);
  });

  resultsBox.addEventListener('click', (e) => {
    const item = e.target.closest('.search-item[data-symbol]');
    if (!item) return;
    addToWatchlist(item.dataset.symbol);
    searchInput.value = '';
    resultsBox.classList.remove('open');
  });

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-input')) resultsBox.classList.remove('open');
  });

  // ---------- Watchlist ----------
  async function addToWatchlist(symbol) {
    try {
      await fetchJSON('/api/watchlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol }),
      });
      await loadWatchlist();
    } catch (e) {
      alert('No se pudo agregar ' + symbol + ': ' + e.message);
    }
  }

  async function removeFromWatchlist(symbol) {
    await fetchJSON('/api/watchlist/' + encodeURIComponent(symbol), { method: 'DELETE' });
    if (charts[symbol]) {
      charts[symbol].candle && charts[symbol].candle.destroy();
      charts[symbol].gauge && charts[symbol].gauge.destroy();
      delete charts[symbol];
    }
    await loadWatchlist();
  }

  const cardsEl = document.getElementById('cards');
  const compareBody = document.getElementById('compare-body');
  const compareEmpty = document.getElementById('compare-empty');

  function showSkeletons() {
    cardsEl.innerHTML = '';
    for (let i = 0; i < 2; i++) {
      const sk = document.createElement('div');
      sk.className = 'card glass';
      sk.innerHTML = '<div class="skeleton" style="height:300px;"></div>';
      cardsEl.appendChild(sk);
    }
  }

  async function loadWatchlist() {
    showSkeletons();
    let data;
    try {
      data = await fetchJSON('/api/watchlist');
    } catch (e) {
      cardsEl.innerHTML = `<p class="empty-state">Error: ${e.message}</p>`;
      return;
    }

    // Tabla comparativa
    const valid = data.filter((d) => !d.error);
    if (!valid.length) {
      compareBody.innerHTML = '';
      compareEmpty.hidden = false;
    } else {
      compareEmpty.hidden = true;
      compareBody.innerHTML = valid.map((d) => `
        <tr class="clickable" data-symbol="${d.symbol}">
          <td class="mono"><strong>${d.symbol}</strong></td>
          <td>${d.name}</td>
          <td class="num">${fmt.money(d.price)}</td>
          <td class="num ${d.deviation_pct < 0 ? 'neg' : 'pos'}">${fmt.pct(d.deviation_pct)}</td>
          <td class="num">${fmt.num(d.rsi)}</td>
          <td class="num">${fmt.num(d.bollinger.percent_b)}</td>
          <td class="num"><span class="score-badge" style="color:${scoreColor(d.score)}">${d.score}</span></td>
          <td class="num"><button class="btn-remove" data-remove="${d.symbol}">✕</button></td>
        </tr>`).join('');
    }

    // Cards detalladas
    cardsEl.innerHTML = '';
    if (!valid.length) {
      cardsEl.innerHTML = '<p class="empty-state">Agregá acciones a tu watchlist para ver el detalle completo.</p>';
      return;
    }
    data.forEach((d) => renderCard(d));
  }

  function renderCard(d) {
    const tpl = document.getElementById('stock-card-template');
    const node = tpl.content.cloneNode(true);
    const root = node.querySelector('.stock-card');
    root.dataset.symbol = d.symbol;
    node.querySelector('.sym').textContent = d.symbol;

    if (d.error) {
      node.querySelector('.cname').textContent = 'Datos no disponibles para este símbolo';
      node.querySelector('.stock-card-body').innerHTML = '';
      node.querySelector('.indicators').innerHTML = '';
    } else {
      node.querySelector('.cname').textContent = d.name + ' · ' + d.sector;
      const verdict = scoreVerdict(d.score);
      node.querySelector('.gauge-value').textContent = d.score;
      node.querySelector('.gauge-value').style.color = scoreColor(d.score);
      const v = node.querySelector('.gauge-verdict');
      v.textContent = verdict.text; v.style.color = verdict.color;
      node.querySelector('.indicators').innerHTML = buildIndicators(d);
    }

    node.querySelector('.btn-remove').addEventListener('click', () => removeFromWatchlist(d.symbol));
    cardsEl.appendChild(node);

    if (d.error) return;

    // Gauge inmediato
    charts[d.symbol] = charts[d.symbol] || {};
    charts[d.symbol].gauge = renderGauge(root.querySelector('.gauge-chart'), d.score);

    // Velas (carga async)
    fetchJSON('/api/candles/' + encodeURIComponent(d.symbol))
      .then((cd) => {
        charts[d.symbol].candle = renderCandles(root.querySelector('.candle-chart'), cd);
      })
      .catch(() => { root.querySelector('.chart-col').innerHTML = '<p class="muted">Gráfico no disponible.</p>'; });
  }

  // Click en fila de comparativa -> scroll a la card
  compareBody.addEventListener('click', (e) => {
    const removeBtn = e.target.closest('[data-remove]');
    if (removeBtn) { e.stopPropagation(); removeFromWatchlist(removeBtn.dataset.remove); return; }
    const row = e.target.closest('tr[data-symbol]');
    if (!row) return;
    const card = cardsEl.querySelector(`.stock-card[data-symbol="${row.dataset.symbol}"]`);
    if (card) card.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });

  // Export CSV
  document.getElementById('export-btn').addEventListener('click', () => {
    window.location = '/api/watchlist/export.csv';
  });

  // Init
  loadWatchlist();
})();
