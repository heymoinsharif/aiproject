/**
 * SentinelMail AI — Landing Page Motion & Live Telemetry Controller
 * Combines:
 *  - GSAP 3 + ScrollTrigger + ScrollSmoother (smooth scroll + data-speed parallax)
 *  - Scrubbed Storytelling Timeline (.scroll-trigger-ready__worm-wrap)
 *  - Pinned Scrubbed Windmill (#pin-windmill-wrap / #pin-windmill / #pin-windmill-svg rotateZ: 900)
 *  - Anime.js v4:
 *      1) Blended Kinetic Shapes (animate + random + composition: 'blend')
 *      2) 13x13 Neural Matrix Radial Stagger (createTimeline + stagger + grid: [13, 13], from: 'center')
 *      3) Orientation-Aware Scope Wave (createScope + mediaQueries portrait)
 *  - Live REST API integration (/api/stats, /api/samples, /api/analyze)
 */

let smoother = null;
let markersEnabled = false;
let wormTimeline = null;
let windmillTimeline = null;
let cachedSamples = [];

// ============================================================================
// 1. GSAP + ScrollTrigger + ScrollSmoother + Parallax (data-speed)
// ============================================================================

function initGSAP(showMarkers = false) {
  const gsap = window.gsap;
  const ScrollTrigger = window.ScrollTrigger;
  const ScrollSmoother = window.ScrollSmoother;

  if (!gsap || !ScrollTrigger) {
    console.warn('GSAP or ScrollTrigger not loaded; running in static fallback mode.');
    document.querySelectorAll('.worm-step').forEach((el) => {
      el.style.opacity = '1';
      el.style.transform = 'none';
    });
    return;
  }

  gsap.registerPlugin(ScrollTrigger);
  if (ScrollSmoother) {
    gsap.registerPlugin(ScrollSmoother);
  }

  // Clean up previous timelines if re-initializing (e.g., when toggling debug markers)
  if (wormTimeline) {
    wormTimeline.scrollTrigger?.kill();
    wormTimeline.kill();
    wormTimeline = null;
  }
  if (windmillTimeline) {
    windmillTimeline.scrollTrigger?.kill();
    windmillTimeline.kill();
    windmillTimeline = null;
  }
  ScrollTrigger.getAll().forEach((st) => st.kill());

  // Smooth Scroll + native data-speed="0.8" / "2.0" / "1.2" parallax effects
  if (ScrollSmoother && !smoother) {
    smoother = ScrollSmoother.create({
      wrapper: '#smooth-wrapper',
      content: '#smooth-content',
      smooth: 1.35,
      effects: true,
      smoothTouch: 0.12,
    });
  } else if (!ScrollSmoother) {
    // Graceful data-speed parallax fallback via ScrollTrigger if ScrollSmoother unavailable
    document.querySelectorAll('[data-speed]').forEach((el) => {
      const speed = parseFloat(el.getAttribute('data-speed') || '1');
      const delta = (1 - speed) * 85;
      gsap.to(el, {
        y: delta,
        ease: 'none',
        scrollTrigger: {
          trigger: el.parentElement || el,
          start: 'top bottom',
          end: 'bottom top',
          scrub: true,
        },
      });
    });
  }

  // Hero entrance stagger
  gsap.fromTo(
    '.hero-copy > *',
    { y: 24, opacity: 0 },
    { y: 0, opacity: 1, duration: 0.75, stagger: 0.09, ease: 'power3.out', clearProps: 'transform' }
  );

  // --------------------------------------------------------------------------
  // Scrubbed Storytelling Timeline (.scroll-trigger-ready__worm-wrap)
  // --------------------------------------------------------------------------
  const wormPath = document.getElementById('wormPathActive');
  if (wormPath) {
    const pathLen = wormPath.getTotalLength();
    gsap.set(wormPath, {
      strokeDasharray: pathLen,
      strokeDashoffset: pathLen,
    });
  }

  wormTimeline = gsap.timeline({
    scrollTrigger: {
      scrub: 1,
      trigger: '.scroll-trigger-ready__worm-wrap',
      start: 'top 90%',
      end: 'bottom 30%',
      markers: showMarkers,
    },
  });

  if (wormPath) {
    wormTimeline.to(wormPath, { strokeDashoffset: 0, ease: 'none', duration: 1 }, 0);
  }

  wormTimeline.to(
    '.worm-step',
    {
      opacity: 1,
      y: 0,
      borderColor: 'rgba(0, 210, 255, 0.38)',
      stagger: 0.22,
      ease: 'power2.out',
      duration: 0.35,
    },
    0.05
  );

  // --------------------------------------------------------------------------
  // Pinned Scrubbed Windmill (#pin-windmill-wrap / #pin-windmill / #pin-windmill-svg)
  // --------------------------------------------------------------------------
  const degLabel = document.getElementById('windmillDeg');
  const layerItems = Array.from(document.querySelectorAll('#windmillLayers .windmill-layer-item'));

  windmillTimeline = gsap.timeline({
    scrollTrigger: {
      scrub: 1,
      pin: true,
      trigger: '#pin-windmill',
      start: '50% 50%',
      endTrigger: '#pin-windmill-wrap',
      end: 'bottom 50%',
      markers: showMarkers,
      onUpdate: (self) => {
        const deg = Math.round(self.progress * 900);
        if (degLabel) degLabel.textContent = `${deg}°`;
        const activeIdx = Math.min(layerItems.length - 1, Math.floor(self.progress * layerItems.length));
        layerItems.forEach((item, idx) => {
          item.classList.toggle('is-active', idx === activeIdx);
        });
      },
    },
  });

  windmillTimeline.to('#pin-windmill-svg', {
    rotateZ: 900,
    ease: 'none',
  });

  // Navbar scrolled state
  ScrollTrigger.create({
    start: 'top -40',
    onUpdate: (self) => {
      const nav = document.getElementById('siteNav');
      if (nav) nav.classList.toggle('scrolled', self.scroll() > 40);
    },
  });

  ScrollTrigger.refresh();
}

// ============================================================================
// 2. ANIME.JS v4 — Blended Shapes, 13x13 Stagger Grid & Responsive Scope Wave
// ============================================================================

function buildDotGrid() {
  const grid = document.getElementById('dotGrid');
  if (!grid || grid.children.length > 0) return;
  const frag = document.createDocumentFragment();
  for (let i = 0; i < 169; i++) {
    const dot = document.createElement('div');
    dot.className = 'dot';
    dot.dataset.index = String(i);
    frag.appendChild(dot);
  }
  grid.appendChild(frag);
}

async function initAnimeJS() {
  buildDotGrid();

  let animeModule = null;
  try {
    animeModule = await import('https://cdn.jsdelivr.net/npm/animejs@4.0.2/+esm');
  } catch (err) {
    console.warn('Anime.js v4 CDN unavailable (offline mode):', err);
    return;
  }

  const { animate, createTimeline, stagger, random, createScope } = animeModule;

  // --------------------------------------------------------------------------
  // A) Blended Kinetic Shapes: animate('.shape', { x, y, rotate, duration, composition: 'blend' })
  // --------------------------------------------------------------------------
  function scatterShapes() {
    animate('.shape', {
      x: () => random(-100, 100),
      y: () => random(-100, 100),
      rotate: () => random(-180, 180),
      duration: () => random(500, 1000),
      composition: 'blend',
      ease: 'outQuad',
    });
  }

  scatterShapes();
  const shapeInterval = setInterval(scatterShapes, 1800);

  const arena = document.getElementById('kineticArena');
  const pulseBtn = document.getElementById('pulseShapesBtn');
  if (arena) arena.addEventListener('click', scatterShapes);
  if (pulseBtn) pulseBtn.addEventListener('click', scatterShapes);

  // --------------------------------------------------------------------------
  // B) 13x13 Neural Matrix Radial Stagger Timeline
  // --------------------------------------------------------------------------
  const options = {
    grid: [13, 13],
    from: 'center',
  };

  let matrixTl = createTimeline({
    loop: true,
    alternate: true,
  }).add(
    '.dot',
    {
      scale: stagger([1.1, 0.75], options),
      opacity: stagger([1, 0.35], options),
      ease: 'inOutQuad',
    },
    stagger(200, options)
  );

  // Interactive click-to-ripple from any clicked cell in the 13x13 grid
  const dotGrid = document.getElementById('dotGrid');
  if (dotGrid) {
    dotGrid.addEventListener('click', (ev) => {
      const target = ev.target;
      if (!target || !target.classList.contains('dot')) return;
      const fromIndex = Number(target.dataset.index || 84);
      const clickOptions = { grid: [13, 13], from: fromIndex };

      if (matrixTl && typeof matrixTl.pause === 'function') {
        matrixTl.pause();
      }
      matrixTl = createTimeline({
        loop: true,
        alternate: true,
      }).add(
        '.dot',
        {
          scale: stagger([1.22, 0.58], clickOptions),
          opacity: stagger([1, 0.32], clickOptions),
          ease: 'inOutQuad',
        },
        stagger(160, clickOptions)
      );
    });
  }

  const resetMatrixBtn = document.getElementById('resetMatrixBtn');
  if (resetMatrixBtn) {
    resetMatrixBtn.addEventListener('click', () => {
      if (matrixTl && typeof matrixTl.pause === 'function') {
        matrixTl.pause();
      }
      matrixTl = createTimeline({
        loop: true,
        alternate: true,
      }).add(
        '.dot',
        {
          scale: stagger([1.1, 0.75], options),
          opacity: stagger([1, 0.35], options),
          ease: 'inOutQuad',
        },
        stagger(200, options)
      );
    });
  }

  // --------------------------------------------------------------------------
  // C) Orientation-Aware Responsive Scope Wave (createScope + mediaQueries)
  // --------------------------------------------------------------------------
  const orientationBadge = document.getElementById('orientationBadge');

  createScope({
    mediaQueries: {
      portrait: '(orientation: portrait)',
    },
  }).add(({ matches }) => {
    const isPortrait = matches.portrait;
    if (orientationBadge) {
      orientationBadge.textContent = isPortrait ? 'PORTRAIT (X-WAVE)' : 'LANDSCAPE (Y-WAVE)';
    }

    createTimeline({ loop: true }).add(
      '.circle',
      {
        y: isPortrait ? 0 : [-50, 50, -50],
        x: isPortrait ? [-50, 50, -50] : 0,
        duration: 1800,
        ease: 'inOutSine',
      },
      stagger(100)
    );
  });

  window.addEventListener('beforeunload', () => clearInterval(shapeInterval));
}

// ============================================================================
// 3. LIVE API TELEMETRY & INSTANT SANDBOX
// ============================================================================

function escapeHtml(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

async function loadLandingStats() {
  try {
    const res = await fetch('/api/stats');
    if (!res.ok) return;
    const data = await res.json();
    const f1El = document.getElementById('heroF1');
    const aucEl = document.getElementById('heroAuc');
    const scannedEl = document.getElementById('heroScanned');

    if (f1El && data.best_metrics?.f1) {
      f1El.textContent = `${(data.best_metrics.f1 * 100).toFixed(2)}%`;
    }
    if (aucEl && data.best_metrics?.roc_auc) {
      aucEl.textContent = `${(data.best_metrics.roc_auc * 100).toFixed(2)}%`;
    }
    if (scannedEl && data.db_stats) {
      scannedEl.textContent = String(data.db_stats.total_scanned ?? 0);
    }
  } catch (err) {
    console.warn('Could not load live stats:', err);
  }
}

async function loadLandingSamples() {
  const row = document.getElementById('landingSampleButtons');
  if (!row) return;

  try {
    const res = await fetch('/api/samples');
    if (!res.ok) return;
    const data = await res.json();
    cachedSamples = data.samples || [];

    cachedSamples.slice(0, 3).forEach((sample, idx) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'btn btn-ghost btn-sm';
      const shortLabel =
        idx === 0 ? 'Phishing Alert' : idx === 1 ? 'University Notice' : 'Suspicious Invoice';
      btn.textContent = shortLabel;
      btn.addEventListener('click', () => {
        document.getElementById('landingSubject').value = sample.subject || '';
        document.getElementById('landingSender').value = sample.sender || '';
        document.getElementById('landingBody').value = sample.body || '';
      });
      row.appendChild(btn);
    });

    // Pre-populate the first sample for effortless 1-click live testing
    if (cachedSamples[0]) {
      document.getElementById('landingSubject').value = cachedSamples[0].subject || '';
      document.getElementById('landingSender').value = cachedSamples[0].sender || '';
      document.getElementById('landingBody').value = cachedSamples[0].body || '';
    }
  } catch (err) {
    console.warn('Could not load samples:', err);
  }
}

function renderLandingResult(data) {
  const box = document.getElementById('landingResultBox');
  if (!box) return;

  const pillClass =
    data.verdict_code === 'phishing'
      ? 'pill-phishing'
      : data.verdict_code === 'suspicious'
      ? 'pill-suspicious'
      : 'pill-legitimate';

  const phishPct = Math.round((data.phishing_probability || 0) * 1000) / 10;
  const legitPct = Math.round((data.legitimate_probability || 0) * 1000) / 10;

  const phishTokens = (data.token_attributions?.phishing_tokens || []).slice(0, 5);
  const indicators = (data.observed_indicators || []).slice(0, 3);

  box.innerHTML = `
    <div>
      <div style="display:flex; justify-content:space-between; align-items:center; gap:0.75rem; flex-wrap:wrap;">
        <span class="pill ${pillClass}">${escapeHtml(data.classification)} &bull; ${escapeHtml(data.risk_level)}</span>
        <span class="mono" style="font-size:0.78rem; color:var(--text-muted);">${escapeHtml(data.model_used)}</span>
      </div>

      <div style="margin-top:1.15rem; display:flex; align-items:baseline; gap:0.7rem;">
        <div style="font-family:var(--font-display); font-size:2.4rem; font-weight:700; line-height:1;">
          ${Number(data.confidence_pct).toFixed(1)}%
        </div>
        <div class="mono" style="font-size:0.78rem; color:var(--text-muted);">CALIBRATED CONFIDENCE</div>
      </div>

      <div style="margin-top:1.15rem;">
        <div style="display:flex; justify-content:space-between; font-size:0.8rem;">
          <span style="color:#fca5a5;">P(Phishing)</span>
          <span class="mono">${phishPct.toFixed(1)}%</span>
        </div>
        <div class="prob-bar-track">
          <div class="prob-bar-fill" style="width:${phishPct}%; background:linear-gradient(90deg, #f59e0b, #ef4444);"></div>
        </div>

        <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-top:0.75rem;">
          <span style="color:#6ee7b7;">P(Legitimate)</span>
          <span class="mono">${legitPct.toFixed(1)}%</span>
        </div>
        <div class="prob-bar-track">
          <div class="prob-bar-fill" style="width:${legitPct}%; background:linear-gradient(90deg, #00d2ff, #10b981);"></div>
        </div>
      </div>

      ${
        phishTokens.length
          ? `<div style="margin-top:1.15rem;">
              <div class="mono" style="font-size:0.72rem; color:var(--text-muted); text-transform:uppercase;">Top XAI Risk Tokens</div>
              <div class="token-chip-list">
                ${phishTokens
                  .map(
                    (t) =>
                      `<span class="pill pill-phishing">${escapeHtml(t.token)} (+${t.impact.toFixed(2)})</span>`
                  )
                  .join('')}
              </div>
            </div>`
          : ''
      }

      ${
        indicators.length
          ? `<div style="margin-top:1rem;">
              <div class="mono" style="font-size:0.72rem; color:var(--text-muted); text-transform:uppercase;">Observed Heuristics</div>
              <ul style="margin:0.45rem 0 0; padding-left:1.15rem; font-size:0.84rem; color:var(--text-secondary);">
                ${indicators.map((ind) => `<li><strong>${escapeHtml(ind.category)}:</strong> ${escapeHtml(ind.description)}</li>`).join('')}
              </ul>
            </div>`
          : ''
      }
    </div>

    <div style="margin-top:1.25rem; padding-top:0.9rem; border-top:1px solid var(--border-subtle); display:flex; justify-content:space-between; align-items:center; gap:0.75rem; flex-wrap:wrap;">
      <span class="mono" style="font-size:0.74rem; color:var(--text-muted);">URLs Inspected: ${data.url_analysis?.total_urls_found ?? 0}</span>
      <a href="/app" class="btn btn-secondary btn-sm">Inspect Full XAI Report &rarr;</a>
    </div>
  `;

  if (data.db_stats) {
    const scannedEl = document.getElementById('heroScanned');
    if (scannedEl) scannedEl.textContent = String(data.db_stats.total_scanned ?? 0);
  }
}

function wireSandboxControls() {
  const analyzeBtn = document.getElementById('landingAnalyzeBtn');
  const clearBtn = document.getElementById('landingClearBtn');

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      document.getElementById('landingSubject').value = '';
      document.getElementById('landingSender').value = '';
      document.getElementById('landingBody').value = '';
    });
  }

  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', async () => {
      const subject = document.getElementById('landingSubject').value.trim();
      const sender = document.getElementById('landingSender').value.trim();
      const body = document.getElementById('landingBody').value.trim();
      const box = document.getElementById('landingResultBox');

      if (!subject && !body) {
        box.innerHTML = `<p style="color:#fca5a5; margin:auto;">Please enter an email subject or body first.</p>`;
        return;
      }

      analyzeBtn.disabled = true;
      analyzeBtn.textContent = 'Analyzing...';

      try {
        const res = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ subject, sender, body, save_to_history: true }),
        });
        const data = await res.json();
        if (!res.ok) {
          box.innerHTML = `<p style="color:#fca5a5; margin:auto;">${escapeHtml(data.error || 'Analysis failed.')}</p>`;
        } else {
          renderLandingResult(data);
        }
      } catch (err) {
        box.innerHTML = `<p style="color:#fca5a5; margin:auto;">Network error contacting /api/analyze.</p>`;
      } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<span>Run Live Threat Scan</span>';
      }
    });
  }
}

// ============================================================================
// 4. SMOOTH ANCHOR LINKS & MARKERS TOGGLE
// ============================================================================

function wireNavigationAndDebug() {
  document.querySelectorAll('[data-scroll-to]').forEach((link) => {
    link.addEventListener('click', (e) => {
      const target = link.getAttribute('data-scroll-to');
      if (!target) return;
      const el = document.querySelector(target);
      if (!el) return;
      e.preventDefault();
      if (smoother) {
        smoother.scrollTo(el, true, 'top 76px');
      } else {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  const toggleBtn = document.getElementById('toggleMarkersBtn');
  const statusEl = document.getElementById('markerStatus');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      markersEnabled = !markersEnabled;
      toggleBtn.classList.toggle('active', markersEnabled);
      if (statusEl) statusEl.textContent = markersEnabled ? 'ON' : 'OFF';
      initGSAP(markersEnabled);
    });
  }
}

// ============================================================================
// BOOTSTRAP
// ============================================================================

window.addEventListener('DOMContentLoaded', () => {
  initGSAP(false);
  initAnimeJS();
  loadLandingStats();
  loadLandingSamples();
  wireSandboxControls();
  wireNavigationAndDebug();
});
