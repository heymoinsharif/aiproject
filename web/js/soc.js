/**
 * SentinelMail AI — Full-Stack SOC Web Application Controller (/app)
 * Connects directly to Starlette REST APIs:
 *   GET  /api/health
 *   GET  /api/stats
 *   GET  /api/samples
 *   POST /api/analyze
 *   GET  /api/benchmarks
 *   GET  /api/history
 *   DELETE /api/history
 */

const state = {
  activeView: 'analyzer',
  samples: [],
  benchmarks: null,
  selectedCmModel: null,
  historyFilter: 'All',
};

const MODEL_COLORS = [
  '#00d2ff',
  '#10b981',
  '#f59e0b',
  '#a78bfa',
];

function escapeHtml(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ============================================================================
// VIEW ROUTING
// ============================================================================

function switchView(viewName, updateHash = false) {
  const valid = ['analyzer', 'benchmarks', 'dataset', 'history', 'about'];
  const target = valid.includes(viewName) ? viewName : 'analyzer';
  state.activeView = target;

  document.querySelectorAll('.soc-view').forEach((sec) => {
    sec.classList.toggle('active', sec.id === `view-${target}`);
  });

  document.querySelectorAll('[data-view]').forEach((el) => {
    el.classList.toggle('active', el.getAttribute('data-view') === target);
  });

  if (target === 'benchmarks' || target === 'dataset') {
    ensureBenchmarksLoaded();
  }
  if (target === 'history') {
    loadHistory();
  }
}

function wireNavigation() {
  document.querySelectorAll('[data-view]').forEach((el) => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      switchView(el.getAttribute('data-view'));
    });
  });

  document.querySelectorAll('[data-soc-tab]').forEach((el) => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      const tab = el.getAttribute('data-soc-tab');
      switchView(tab);
      const ws = document.getElementById('soc-workspace');
      if (ws) ws.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  const initialHash = window.location.hash.replace('#', '');
  if (['analyzer', 'benchmarks', 'dataset', 'history', 'about'].includes(initialHash)) {
    switchView(initialHash, false);
  }
}

// ============================================================================
// HEALTH, STATS & SAMPLES
// ============================================================================

async function loadHealthAndModels() {
  try {
    const res = await fetch('/api/health');
    if (!res.ok) return;
    const data = await res.json();

    const statusEl = document.getElementById('sidebarStatusText');
    const modelEl = document.getElementById('sidebarModelText');
    const selectEl = document.getElementById('socModelSelect');

    if (statusEl) {
      statusEl.textContent = data.model_ready ? 'Operational & Local' : 'Models Missing';
    }
    if (modelEl) {
      modelEl.textContent = `Primary: ${data.best_model_name}`;
    }
    if (selectEl) {
      const models = data.available_models || [data.best_model_name];
      selectEl.innerHTML = models
        .map(
          (m) =>
            `<option value="${escapeHtml(m)}" ${m === data.best_model_name ? 'selected' : ''}>${escapeHtml(m)}</option>`
        )
        .join('');
    }
  } catch (err) {
    console.error('Failed to load /api/health:', err);
  }
}

function updateStatsKPIs(dbStats, bestMetrics) {
  if (dbStats) {
    const totalEl = document.getElementById('kpiTotal');
    const phishEl = document.getElementById('kpiPhishing');
    const suspEl = document.getElementById('kpiSuspicious');
    if (totalEl) totalEl.textContent = String(dbStats.total_scanned ?? 0);
    if (phishEl) phishEl.textContent = String(dbStats.phishing_count ?? 0);
    if (suspEl) suspEl.textContent = String(dbStats.suspicious_count ?? 0);
  }
  if (bestMetrics?.f1) {
    const f1El = document.getElementById('kpiTopF1');
    if (f1El) f1El.textContent = `${(bestMetrics.f1 * 100).toFixed(2)}%`;
  }
}

async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    if (!res.ok) return;
    const data = await res.json();
    updateStatsKPIs(data.db_stats, data.best_metrics);
  } catch (err) {
    console.error('Failed to load /api/stats:', err);
  }
}

async function loadSamples() {
  const grid = document.getElementById('socSamplesGrid');
  if (!grid) return;
  try {
    const res = await fetch('/api/samples');
    if (!res.ok) return;
    const data = await res.json();
    state.samples = data.samples || [];

    grid.innerHTML = state.samples
      .map(
        (s, idx) => `
        <button type="button" class="sample-btn" data-sample-idx="${idx}" title="${escapeHtml(s.description)}">
          <div class="sample-btn-title">${escapeHtml(s.key)}</div>
          <div class="sample-btn-cat">${escapeHtml(s.category)}</div>
        </button>
      `
      )
      .join('');

    grid.querySelectorAll('.sample-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const s = state.samples[Number(btn.dataset.sampleIdx)];
        if (!s) return;
        document.getElementById('socSubject').value = s.subject || '';
        document.getElementById('socSender').value = s.sender || '';
        document.getElementById('socBody').value = s.body || '';
        document.getElementById('socUrls').value = s.urls || '';
      });
    });
  } catch (err) {
    console.error('Failed to load /api/samples:', err);
  }
}

// ============================================================================
// EMAIL ANALYZER & XAI RENDERER
// ============================================================================

function renderTokenBars(tokens, isPhishing) {
  if (!tokens || tokens.length === 0) {
    return `<div style="font-size:0.82rem; color:var(--text-dim);">No significant ${isPhishing ? 'phishing' : 'legitimate'} tokens matched.</div>`;
  }
  const maxAbs = Math.max(...tokens.map((t) => Math.abs(t.impact)), 0.001);
  const grad = isPhishing
    ? 'linear-gradient(90deg, #f59e0b, #ef4444)'
    : 'linear-gradient(90deg, #00d2ff, #10b981)';
  const sign = isPhishing ? '+' : '';

  return tokens
    .map((t) => {
      const pct = Math.max(8, Math.round((Math.abs(t.impact) / maxAbs) * 100));
      return `
        <div class="xai-bar-row">
          <div class="xai-bar-meta">
            <span style="color:var(--text-primary);">${escapeHtml(t.token)}</span>
            <span style="color:${isPhishing ? '#fca5a5' : '#6ee7b7'};">${sign}${t.impact.toFixed(3)}</span>
          </div>
          <div class="xai-bar-track">
            <div class="xai-bar-fill" style="width:${pct}%; background:${grad};"></div>
          </div>
        </div>
      `;
    })
    .join('');
}

function renderAnalysisResult(res) {
  const container = document.getElementById('socResultContainer');
  if (!container) return;

  const code = res.verdict_code || 'legitimate';
  const color = code === 'phishing' ? '#ef4444' : code === 'suspicious' ? '#f59e0b' : '#10b981';
  const pillClass = code === 'phishing' ? 'pill-phishing' : code === 'suspicious' ? 'pill-suspicious' : 'pill-legitimate';

  const conf = Number(res.confidence_pct || 0);
  const circumference = 2 * Math.PI * 38;
  const dashOffset = circumference * (1 - Math.min(100, Math.max(0, conf)) / 100);

  const phishPct = ((res.phishing_probability || 0) * 100).toFixed(2);
  const legitPct = ((res.legitimate_probability || 0) * 100).toFixed(2);

  const xai = res.token_attributions || {};
  const indicators = res.observed_indicators || [];
  const urls = res.url_analysis?.url_details || [];

  container.innerHTML = `
    <div class="verdict-banner ${code}">
      <div style="flex:1; min-width:210px;">
        <span class="pill ${pillClass}">${escapeHtml(res.classification)} &bull; ${escapeHtml(res.risk_level)}</span>
        <h2 style="font-family:var(--font-display); font-size:1.55rem; margin:0.6rem 0 0.25rem;">
          ${escapeHtml(res.classification)}
        </h2>
        <div class="mono" style="font-size:0.76rem; color:var(--text-muted);">
          Model: ${escapeHtml(res.model_used)} ${res.record_id ? `&bull; Audit #${res.record_id}` : ''}
        </div>
      </div>

      <div class="gauge-wrap" aria-label="Confidence ${conf.toFixed(1)}%">
        <svg width="96" height="96" viewBox="0 0 96 96">
          <circle cx="48" cy="48" r="38" fill="none" stroke="rgba(148,163,184,0.16)" stroke-width="8" />
          <circle cx="48" cy="48" r="38" fill="none" stroke="${color}" stroke-width="8"
            stroke-linecap="round"
            stroke-dasharray="${circumference.toFixed(2)}"
            stroke-dashoffset="${dashOffset.toFixed(2)}"
            transform="rotate(-90 48 48)" />
        </svg>
        <div class="gauge-label">
          <span style="color:${color};">${conf.toFixed(1)}%</span>
          <span class="mono" style="font-size:0.56rem; color:var(--text-muted);">CONF</span>
        </div>
      </div>
    </div>

    <!-- Calibrated Probabilities -->
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.85rem; margin-bottom:1.25rem;">
      <div class="xai-box">
        <div style="display:flex; justify-content:space-between; font-size:0.8rem;">
          <span style="color:#fca5a5;">P(Phishing)</span>
          <strong class="mono">${phishPct}%</strong>
        </div>
        <div class="xai-bar-track" style="margin-top:0.45rem; height:9px;">
          <div class="xai-bar-fill" style="width:${phishPct}%; background:linear-gradient(90deg, #f59e0b, #ef4444);"></div>
        </div>
      </div>
      <div class="xai-box">
        <div style="display:flex; justify-content:space-between; font-size:0.8rem;">
          <span style="color:#6ee7b7;">P(Legitimate)</span>
          <strong class="mono">${legitPct}%</strong>
        </div>
        <div class="xai-bar-track" style="margin-top:0.45rem; height:9px;">
          <div class="xai-bar-fill" style="width:${legitPct}%; background:linear-gradient(90deg, #00d2ff, #10b981);"></div>
        </div>
      </div>
    </div>

    <!-- Explainable AI (XAI) -->
    <div style="margin-bottom:1.25rem;">
      <div class="panel-title" style="margin-bottom:0.4rem;">
        <span>Explainable AI (XAI) Token Attribution</span>
        <span class="mono" style="font-size:0.7rem; color:var(--cyan);">TF-IDF &times; Coef</span>
      </div>
      ${
        xai.supported
          ? `<div class="xai-split">
              <div class="xai-box">
                <div class="mono" style="font-size:0.72rem; color:#fca5a5; margin-bottom:0.65rem;">PHISHING PUSH TOKENS (+)</div>
                ${renderTokenBars(xai.phishing_tokens, true)}
              </div>
              <div class="xai-box">
                <div class="mono" style="font-size:0.72rem; color:#6ee7b7; margin-bottom:0.65rem;">LEGITIMATE PUSH TOKENS (-)</div>
                ${renderTokenBars(xai.legitimate_tokens, false)}
              </div>
            </div>`
          : `<div class="xai-box" style="font-size:0.84rem; color:var(--text-muted);">${escapeHtml(xai.reason || 'Linear attribution unavailable for this tree classifier. Select SVM or Logistic Regression for token weights.')}</div>`
      }
    </div>

    <!-- Observed Security Heuristics -->
    <div style="margin-bottom:1.25rem;">
      <div class="panel-title" style="margin-bottom:0.65rem;">
        <span>Observed Cybersecurity Heuristics</span>
        <span class="mono" style="font-size:0.74rem; color:var(--text-muted);">${indicators.length} triggered</span>
      </div>
      ${
        indicators.length
          ? indicators
              .map((ind) => {
                const sev = (ind.severity || 'Low').toLowerCase();
                return `
                  <div class="indicator-item">
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:0.5rem; margin-bottom:0.3rem;">
                      <strong style="font-size:0.88rem;">${escapeHtml(ind.category)}</strong>
                      <span class="pill pill-${sev}">${escapeHtml(ind.severity)}</span>
                    </div>
                    <div style="font-size:0.84rem; color:var(--text-secondary);">${escapeHtml(ind.description)}</div>
                    <div class="mono" style="font-size:0.74rem; color:var(--text-muted); margin-top:0.35rem;">${escapeHtml(ind.evidence)}</div>
                  </div>
                `;
              })
              .join('')
          : `<div class="indicator-item" style="color:var(--emerald); font-size:0.86rem;">No suspicious deterministic text or URL heuristics triggered.</div>`
      }
    </div>

    <!-- Offline URL Scanner -->
    <div style="margin-bottom:1rem;">
      <div class="panel-title" style="margin-bottom:0.65rem;">
        <span>Offline URL Structural Scanner</span>
        <span class="mono" style="font-size:0.74rem; color:var(--text-muted);">${urls.length} URL(s) inspected</span>
      </div>
      ${
        urls.length
          ? urls
              .map(
                (u) => `
                <div class="url-item">
                  <div style="display:flex; justify-content:space-between; align-items:center; gap:0.5rem; flex-wrap:wrap;">
                    <code style="font-size:0.78rem; color:var(--cyan); word-break:break-all;">${escapeHtml(u.url)}</code>
                    <span class="pill ${u.risk_score >= 0.5 ? 'pill-phishing' : u.risk_score > 0.2 ? 'pill-suspicious' : 'pill-legitimate'}">
                      Risk: ${(u.risk_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div class="mono" style="font-size:0.72rem; color:var(--text-muted); margin-top:0.45rem;">
                    Host: ${escapeHtml(u.hostname || 'n/a')} &bull; TLD: .${escapeHtml(u.tld || 'n/a')} &bull; Len: ${u.length} &bull; Subdomains: ${u.subdomain_count}
                    ${u.has_ip_host ? ' &bull; [RAW IP]' : ''}
                    ${u.is_shortener ? ' &bull; [SHORTENER]' : ''}
                    ${u.has_punycode ? ' &bull; [PUNYCODE]' : ''}
                  </div>
                  ${
                    u.flags && u.flags.length
                      ? `<ul style="margin:0.45rem 0 0; padding-left:1.1rem; font-size:0.8rem; color:#fcd34d;">
                          ${u.flags.map((f) => `<li>${escapeHtml(f)}</li>`).join('')}
                        </ul>`
                      : ''
                  }
                </div>
              `
              )
              .join('')
          : `<div class="url-item" style="font-size:0.84rem; color:var(--text-muted);">No hyperlinks detected in email content.</div>`
      }
    </div>

    <!-- Statistical Disclaimer -->
    <div style="padding:0.85rem 1rem; border-radius:var(--radius-sm); background:rgba(148,163,184,0.06); border:1px solid var(--border-subtle); font-size:0.78rem; color:var(--text-muted); line-height:1.55;">
      ${escapeHtml(res.disclaimer)}
    </div>
  `;
}

function wireAnalyzerForm() {
  const analyzeBtn = document.getElementById('socAnalyzeBtn');
  const clearBtn = document.getElementById('socClearBtn');

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      document.getElementById('socSubject').value = '';
      document.getElementById('socSender').value = '';
      document.getElementById('socBody').value = '';
      document.getElementById('socUrls').value = '';
    });
  }

  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', async () => {
      const subject = document.getElementById('socSubject').value.trim();
      const sender = document.getElementById('socSender').value.trim();
      const body = document.getElementById('socBody').value.trim();
      const urls = document.getElementById('socUrls').value.trim();
      const selected_model = document.getElementById('socModelSelect').value;
      const save_to_history = document.getElementById('socSaveHistory').checked;
      const out = document.getElementById('socResultContainer');

      if (!subject && !body) {
        out.innerHTML = `<div style="padding:2rem; text-align:center; color:#fca5a5;">Please provide at least an email subject or body text before running analysis.</div>`;
        return;
      }

      analyzeBtn.disabled = true;
      analyzeBtn.textContent = 'Running ML Pipeline...';

      try {
        const res = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ subject, sender, body, urls, selected_model, save_to_history }),
        });
        const data = await res.json();
        if (!res.ok) {
          out.innerHTML = `<div style="padding:2rem; text-align:center; color:#fca5a5;">${escapeHtml(data.error || 'Inference error')}</div>`;
        } else {
          renderAnalysisResult(data);
          if (data.db_stats) updateStatsKPIs(data.db_stats, null);
        }
      } catch (err) {
        out.innerHTML = `<div style="padding:2rem; text-align:center; color:#fca5a5;">Network error reaching /api/analyze.</div>`;
      } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Analyze Email & Explain';
      }
    });
  }
}

// ============================================================================
// BENCHMARKS, CONFUSION MATRIX, SVG ROC/PR CURVES & DATASET HYGIENE
// ============================================================================

async function ensureBenchmarksLoaded() {
  if (state.benchmarks) {
    renderBenchmarks(state.benchmarks);
    renderDatasetView(state.benchmarks);
    return;
  }
  try {
    const res = await fetch('/api/benchmarks');
    if (!res.ok) return;
    state.benchmarks = await res.json();
    renderBenchmarks(state.benchmarks);
    renderDatasetView(state.benchmarks);
  } catch (err) {
    console.error('Failed to load /api/benchmarks:', err);
  }
}

function renderConfusionMatrix(modelName, models) {
  const info = models[modelName];
  if (!info) return;
  const tm = info.test_metrics;
  const cm = tm.confusion_matrix;

  const grid = document.getElementById('cmMatrixGrid');
  const rates = document.getElementById('cmRatesBox');
  const tradeoffs = document.getElementById('tradeoffsContainer');

  if (grid) {
    grid.innerHTML = `
      <div class="cm-cell cm-tn">
        <div class="cm-num" style="color:var(--emerald);">${cm.tn}</div>
        <div class="cm-tag">TRUE NEGATIVE (Legit Safe)</div>
      </div>
      <div class="cm-cell cm-fp">
        <div class="cm-num" style="color:var(--amber);">${cm.fp}</div>
        <div class="cm-tag">FALSE POSITIVE (False Alarm)</div>
      </div>
      <div class="cm-cell cm-fn">
        <div class="cm-num" style="color:var(--crimson);">${cm.fn}</div>
        <div class="cm-tag">FALSE NEGATIVE (Missed Threat)</div>
      </div>
      <div class="cm-cell cm-tp">
        <div class="cm-num" style="color:var(--cyan);">${cm.tp}</div>
        <div class="cm-tag">TRUE POSITIVE (Phish Caught)</div>
      </div>
    `;
  }

  if (rates) {
    rates.innerHTML = `
      <div style="display:flex; gap:1.5rem; flex-wrap:wrap;">
        <span>False Positive Rate: <strong style="color:var(--amber);">${(tm.false_positive_rate * 100).toFixed(2)}%</strong></span>
        <span>False Negative Rate: <strong style="color:var(--crimson);">${(tm.false_negative_rate * 100).toFixed(2)}%</strong></span>
      </div>
    `;
  }

  if (tradeoffs && info.tradeoffs) {
    tradeoffs.innerHTML = `
      <div class="indicator-item">
        <strong style="color:var(--amber);">False Positive Impact</strong>
        <p style="margin:0.35rem 0 0; color:var(--text-muted); font-size:0.84rem;">${escapeHtml(info.tradeoffs.false_positive_impact)}</p>
      </div>
      <div class="indicator-item">
        <strong style="color:var(--crimson);">False Negative Impact</strong>
        <p style="margin:0.35rem 0 0; color:var(--text-muted); font-size:0.84rem;">${escapeHtml(info.tradeoffs.false_negative_impact)}</p>
      </div>
      <div class="indicator-item" style="margin-bottom:0;">
        <strong style="color:var(--cyan);">The Accuracy Paradox</strong>
        <p style="margin:0.35rem 0 0; color:var(--text-muted); font-size:0.84rem;">${escapeHtml(info.tradeoffs.accuracy_paradox_explanation)}</p>
      </div>
    `;
  }
}

function buildCurveSVG(models, curveKey, xKey, yKey, xLabel, yLabel, diagonal = false) {
  const W = 520;
  const H = 290;
  const pad = { top: 18, right: 20, bottom: 42, left: 48 };
  const plotW = W - pad.left - pad.right;
  const plotH = H - pad.top - pad.bottom;

  const toX = (v) => pad.left + v * plotW;
  const toY = (v) => pad.top + (1 - v) * plotH;

  let gridLines = '';
  for (let i = 0; i <= 4; i++) {
    const val = i / 4;
    const x = toX(val).toFixed(1);
    const y = toY(val).toFixed(1);
    gridLines += `<line x1="${pad.left}" y1="${y}" x2="${W - pad.right}" y2="${y}" stroke="rgba(148,163,184,0.12)" stroke-width="1" />`;
    gridLines += `<line x1="${x}" y1="${pad.top}" x2="${x}" y2="${H - pad.bottom}" stroke="rgba(148,163,184,0.12)" stroke-width="1" />`;
    gridLines += `<text x="${pad.left - 8}" y="${Number(y) + 4}" text-anchor="end" fill="#94a3b8" font-size="10" font-family="JetBrains Mono">${val.toFixed(2)}</text>`;
    gridLines += `<text x="${x}" y="${H - pad.bottom + 16}" text-anchor="middle" fill="#94a3b8" font-size="10" font-family="JetBrains Mono">${val.toFixed(2)}</text>`;
  }

  const diagLine = diagonal
    ? `<line x1="${toX(0)}" y1="${toY(0)}" x2="${toX(1)}" y2="${toY(1)}" stroke="rgba(148,163,184,0.3)" stroke-dasharray="4 4" stroke-width="1.2" />`
    : '';

  const modelNames = Object.keys(models);
  let paths = '';
  let legendHtml = '';

  modelNames.forEach((name, idx) => {
    const color = MODEL_COLORS[idx % MODEL_COLORS.length];
    const c = models[name]?.curves?.[curveKey];
    if (!c || !c[xKey] || !c[yKey]) return;
    const xs = c[xKey];
    const ys = c[yKey];
    const d = xs
      .map((xv, i) => `${i === 0 ? 'M' : 'L'} ${toX(xv).toFixed(2)} ${toY(ys[i]).toFixed(2)}`)
      .join(' ');
    paths += `<path d="${d}" fill="none" stroke="${color}" stroke-width="2.2" stroke-linejoin="round" />`;
    const auc = models[name]?.test_metrics?.roc_auc;
    const suffix = curveKey === 'roc' && auc ? ` (${auc.toFixed(4)})` : '';
    legendHtml += `<span class="legend-item"><span class="legend-swatch" style="background:${color};"></span>${escapeHtml(name)}${suffix}</span>`;
  });

  return `
    <svg class="svg-chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${escapeHtml(yLabel)} vs ${escapeHtml(xLabel)}">
      ${gridLines}
      ${diagLine}
      ${paths}
      <text x="${pad.left + plotW / 2}" y="${H - 6}" text-anchor="middle" fill="#cbd5e1" font-size="11" font-family="Inter">${escapeHtml(xLabel)}</text>
      <text x="14" y="${pad.top + plotH / 2}" text-anchor="middle" fill="#cbd5e1" font-size="11" font-family="Inter" transform="rotate(-90 14 ${pad.top + plotH / 2})">${escapeHtml(yLabel)}</text>
    </svg>
    <div class="chart-legend">${legendHtml}</div>
  `;
}

function renderBenchmarks(evalData) {
  const models = evalData.models || {};
  const bestName = evalData.best_model_name || 'Support Vector Machine (SVM)';
  const pill = document.getElementById('bestModelPill');
  if (pill) pill.textContent = `Best: ${bestName}`;

  const tbody = document.querySelector('#benchmarkTable tbody');
  if (tbody) {
    tbody.innerHTML = Object.entries(models)
      .map(([name, info]) => {
        const tm = info.test_metrics;
        const cv = info.cross_validation || {};
        const isBest = name === bestName;
        return `
          <tr class="${isBest ? 'highlight-row' : ''}">
            <td>${escapeHtml(name)} ${isBest ? '<span class="pill pill-legitimate" style="margin-left:0.4rem;">TOP</span>' : ''}</td>
            <td class="mono">${(cv.cv_f1_mean ?? 0).toFixed(4)}</td>
            <td class="mono">${(tm.accuracy * 100).toFixed(2)}%</td>
            <td class="mono">${(tm.precision * 100).toFixed(2)}%</td>
            <td class="mono">${(tm.recall * 100).toFixed(2)}%</td>
            <td class="mono" style="color:var(--emerald); font-weight:700;">${(tm.f1 * 100).toFixed(2)}%</td>
            <td class="mono">${tm.roc_auc != null ? tm.roc_auc.toFixed(4) : 'N/A'}</td>
            <td class="mono">${info.train_time_seconds.toFixed(3)}</td>
            <td class="mono">${info.inference_time_ms_per_email.toFixed(3)}</td>
          </tr>
        `;
      })
      .join('');
  }

  // CM Tabs
  const cmTabs = document.getElementById('cmModelTabs');
  const names = Object.keys(models);
  if (!state.selectedCmModel || !models[state.selectedCmModel]) {
    state.selectedCmModel = models[bestName] ? bestName : names[0];
  }

  if (cmTabs) {
    cmTabs.innerHTML = names
      .map(
        (n) =>
          `<button type="button" class="filter-pill ${n === state.selectedCmModel ? 'active' : ''}" data-cm="${escapeHtml(n)}">${escapeHtml(n)}</button>`
      )
      .join('');

    cmTabs.querySelectorAll('[data-cm]').forEach((btn) => {
      btn.addEventListener('click', () => {
        state.selectedCmModel = btn.getAttribute('data-cm');
        cmTabs.querySelectorAll('[data-cm]').forEach((b) =>
          b.classList.toggle('active', b.getAttribute('data-cm') === state.selectedCmModel)
        );
        renderConfusionMatrix(state.selectedCmModel, models);
      });
    });
  }
  renderConfusionMatrix(state.selectedCmModel, models);

  // ROC & PR Curves
  const rocEl = document.getElementById('rocChartContainer');
  const prEl = document.getElementById('prChartContainer');
  if (rocEl) {
    rocEl.innerHTML = buildCurveSVG(models, 'roc', 'fpr', 'tpr', 'False Positive Rate', 'True Positive Rate', true);
  }
  if (prEl) {
    prEl.innerHTML = buildCurveSVG(models, 'pr', 'recall', 'precision', 'Recall', 'Precision', false);
  }

  // Research Questions RQ1-RQ4
  const rqGrid = document.getElementById('rqCardsGrid');
  const rqs = evalData.research_questions || {};
  if (rqGrid) {
    rqGrid.innerHTML = Object.entries(rqs)
      .map(([key, rq]) => {
        let extra = '';
        if (key === 'RQ3' && rq.comparison) {
          const textF1 = (rq.comparison.text_only_baseline.f1 * 100).toFixed(2);
          const hybF1 = (rq.comparison.hybrid_text_plus_structured.f1 * 100).toFixed(2);
          extra = `<div class="mono" style="margin-top:0.8rem; font-size:0.78rem; color:var(--cyan);">Text-Only F1: ${textF1}% &bull; Hybrid Structured F1: ${hybF1}%</div>`;
        }
        if (key === 'RQ4' && rq.stress_test_metrics) {
          extra = `<div class="mono" style="margin-top:0.8rem; font-size:0.78rem; color:var(--emerald);">Short-Email Stress Test (${rq.stress_test_sample_count} samples): F1 ${(rq.stress_test_metrics.f1 * 100).toFixed(2)}% &bull; Recall ${(rq.stress_test_metrics.recall * 100).toFixed(2)}%</div>`;
        }
        return `
          <article class="cyber-panel panel-pad">
            <span class="pill pill-info">${escapeHtml(key)}</span>
            <h3 style="font-family:var(--font-display); font-size:1.05rem; margin:0.75rem 0 0.5rem;">${escapeHtml(rq.question)}</h3>
            <p style="margin:0; font-size:0.88rem; color:var(--text-muted); line-height:1.65;">${escapeHtml(rq.conclusion)}</p>
            ${extra}
          </article>
        `;
      })
      .join('');
  }
}

function renderDatasetView(evalData) {
  const m = evalData.metadata || {};
  const total = m.dataset_size || 10000;
  const phish = m.phishing_count || 5577;
  const legit = m.legitimate_count || 4423;
  const phishPct = ((phish / total) * 100).toFixed(1);
  const legitPct = ((legit / total) * 100).toFixed(1);

  const kpiGrid = document.getElementById('datasetKpiGrid');
  if (kpiGrid) {
    kpiGrid.innerHTML = `
      <div class="kpi-card"><div class="kpi-val">${total.toLocaleString()}</div><div class="kpi-lbl">Curated Benchmark Emails</div></div>
      <div class="kpi-card"><div class="kpi-val" style="color:var(--crimson);">${phish.toLocaleString()}</div><div class="kpi-lbl">Phishing (${phishPct}%)</div></div>
      <div class="kpi-card"><div class="kpi-val" style="color:var(--emerald);">${legit.toLocaleString()}</div><div class="kpi-lbl">Legitimate (${legitPct}%)</div></div>
      <div class="kpi-card"><div class="kpi-val" style="color:var(--cyan);">0.00%</div><div class="kpi-lbl">Data Leakage Tolerance</div></div>
    `;
  }

  const donutEl = document.getElementById('datasetDonutContainer');
  if (donutEl) {
    const r = 68;
    const c = 2 * Math.PI * r;
    const phishDash = (phish / total) * c;
    const legitDash = (legit / total) * c;

    donutEl.innerHTML = `
      <svg width="190" height="190" viewBox="0 0 190 190" role="img" aria-label="Dataset Class Balance">
        <circle cx="95" cy="95" r="${r}" fill="none" stroke="rgba(148,163,184,0.12)" stroke-width="22" />
        <circle cx="95" cy="95" r="${r}" fill="none" stroke="#ef4444" stroke-width="22"
          stroke-dasharray="${phishDash.toFixed(1)} ${c.toFixed(1)}" transform="rotate(-90 95 95)" />
        <circle cx="95" cy="95" r="${r}" fill="none" stroke="#10b981" stroke-width="22"
          stroke-dasharray="${legitDash.toFixed(1)} ${c.toFixed(1)}"
          stroke-dashoffset="${(-phishDash).toFixed(1)}" transform="rotate(-90 95 95)" />
        <text x="95" y="92" text-anchor="middle" fill="#f1f5f9" font-size="20" font-weight="700" font-family="Space Grotesk">${total.toLocaleString()}</text>
        <text x="95" y="111" text-anchor="middle" fill="#94a3b8" font-size="10" font-family="JetBrains Mono">CEAS 2008</text>
      </svg>
      <div style="display:flex; flex-direction:column; gap:0.75rem; font-size:0.88rem;">
        <div class="legend-item"><span class="legend-swatch" style="background:#ef4444; height:10px; width:10px; border-radius:50%;"></span> Phishing Attacks: <strong>${phish.toLocaleString()} (${phishPct}%)</strong></div>
        <div class="legend-item"><span class="legend-swatch" style="background:#10b981; height:10px; width:10px; border-radius:50%;"></span> Legitimate / Ham: <strong>${legit.toLocaleString()} (${legitPct}%)</strong></div>
        <div class="mono" style="font-size:0.76rem; color:var(--text-muted); margin-top:0.4rem;">Train: ${(m.train_size || 8000).toLocaleString()} &bull; Test: ${(m.test_size || 2000).toLocaleString()} &bull; Vocab: ${(m.feature_count || 5000).toLocaleString()}</div>
      </div>
    `;
  }
}

// ============================================================================
// AUDIT HISTORY (SQLITE)
// ============================================================================

async function loadHistory() {
  const tbody = document.querySelector('#historyTable tbody');
  const kpiGrid = document.getElementById('historyKpiGrid');
  const countNote = document.getElementById('historyCountNote');

  try {
    const url = `/api/history?limit=150&classification=${encodeURIComponent(state.historyFilter)}`;
    const res = await fetch(url);
    if (!res.ok) return;
    const data = await res.json();
    const records = data.records || [];
    const stats = data.stats || {};

    updateStatsKPIs(stats, null);

    if (kpiGrid) {
      kpiGrid.innerHTML = `
        <div class="kpi-card"><div class="kpi-val">${stats.total_scanned ?? 0}</div><div class="kpi-lbl">Total Logged Scans</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:var(--crimson);">${stats.phishing_count ?? 0}</div><div class="kpi-lbl">Likely Phishing</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:var(--amber);">${stats.suspicious_count ?? 0}</div><div class="kpi-lbl">Suspicious</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:var(--emerald);">${stats.legitimate_count ?? 0}</div><div class="kpi-lbl">Likely Legitimate</div></div>
      `;
    }

    if (countNote) {
      countNote.textContent = `${records.length} record${records.length === 1 ? '' : 's'} shown`;
    }

    if (tbody) {
      if (records.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:2rem; color:var(--text-muted);">No audit records found for this filter. Analyze an email in the Analyzer tab to populate history.</td></tr>`;
      } else {
        tbody.innerHTML = records
          .map((r) => {
            const pClass = r.classification.includes('Phishing')
              ? 'pill-phishing'
              : r.classification.includes('Suspicious')
              ? 'pill-suspicious'
              : 'pill-legitimate';
            const inds = (r.indicators || []).slice(0, 2).join(', ') || 'None';
            return `
              <tr>
                <td class="mono" style="font-size:0.78rem; white-space:nowrap;">${escapeHtml(r.timestamp)}</td>
                <td style="color:var(--text-primary); font-weight:500;">${escapeHtml(r.subject_snippet)}</td>
                <td class="mono" style="font-size:0.78rem;">${escapeHtml(r.sender_domain)}</td>
                <td><span class="pill ${pClass}">${escapeHtml(r.classification)}</span></td>
                <td class="mono">${(Number(r.confidence || 0) * 100).toFixed(1)}%</td>
                <td class="mono">${r.urls_count ?? 0}</td>
                <td style="font-size:0.78rem; color:var(--text-muted);">${escapeHtml(inds)}</td>
              </tr>
            `;
          })
          .join('');
      }
    }
  } catch (err) {
    console.error('Failed to load /api/history:', err);
  }
}

function wireHistoryControls() {
  document.querySelectorAll('#historyFilterBar [data-filter]').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.historyFilter = btn.getAttribute('data-filter') || 'All';
      document.querySelectorAll('#historyFilterBar [data-filter]').forEach((b) =>
        b.classList.toggle('active', b.getAttribute('data-filter') === state.historyFilter)
      );
      loadHistory();
    });
  });

  const refreshBtn = document.getElementById('refreshHistoryBtn');
  if (refreshBtn) refreshBtn.addEventListener('click', loadHistory);

  const clearBtn = document.getElementById('clearHistoryBtn');
  if (clearBtn) {
    clearBtn.addEventListener('click', async () => {
      if (!window.confirm('Permanently purge all scan history records from local SQLite?')) return;
      try {
        await fetch('/api/history', { method: 'DELETE' });
        loadHistory();
      } catch (err) {
        console.error('Failed to clear history:', err);
      }
    });
  }
}

// ============================================================================
// BOOTSTRAP
// ============================================================================

window.addEventListener('DOMContentLoaded', () => {
  wireNavigation();
  wireAnalyzerForm();
  wireHistoryControls();
  loadHealthAndModels();
  loadStats();
  loadSamples();
});
