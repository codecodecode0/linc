// Built-in sample data. Used as a fallback when the /api backend isn't
// available — e.g. when this UI is served statically on GitHub Pages.
const SAMPLE = {
  stats: {
    creatorsCertified: 9000,
    brandsActive: 1200,
    agenciesActive: 180,
    aiAdsGenerated: 184000,
    paidToCreators: 240000000,
    avgRoas: 5.3,
  },
  creators: [
    { id: '1', name: 'Maya Chen', handle: '@mayacreates', niche: 'Beauty & Skincare', location: 'Mumbai', followers: '480K', engagement: '4.8%', matchScore: 96, avatar: 'MC', certified: true, rate: 85000 },
    { id: '2', name: 'Rohan Mehta', handle: '@rohaneats', niche: 'Food & Drinks', location: 'Delhi', followers: '320K', engagement: '3.2%', matchScore: 91, avatar: 'RM', certified: true, rate: 60000 },
    { id: '3', name: 'Priya Sharma', handle: '@priyafit', niche: 'Health & Fitness', location: 'Bengaluru', followers: '610K', engagement: '5.1%', matchScore: 88, avatar: 'PS', certified: false, rate: 95000 },
    { id: '4', name: 'Arjun Nair', handle: '@arjuntech', niche: 'Phones & Gadgets', location: 'Hyderabad', followers: '270K', engagement: '2.9%', matchScore: 84, avatar: 'AN', certified: true, rate: 70000 },
  ],
  deals: [
    { id: 'd1', title: 'Glow Face Serum — Video Ad', brand: 'Glow Labs', creator: 'Maya Chen', status: 'review', budget: 85000, path: 'video' },
    { id: 'd2', title: 'Protein Bar — AI Photo Ads', brand: 'Fuel Co', creator: 'Rohan Mehta', status: 'paid', budget: 55000, path: 'ai-static' },
    { id: 'd3', title: 'Smart Watch — AI Video Ads', brand: 'Pulse Gear', creator: 'Arjun Nair', status: 'filming', budget: 160000, path: 'ai-video' },
    { id: 'd4', title: 'Yoga Mat — New Deal', brand: 'ZenFlow', creator: 'Priya Sharma', status: 'contract', budget: 70000, path: 'video' },
  ],
  campaigns: [
    { id: 'c1', name: 'Glow Serum — Festive Push', brand: 'Glow Labs', creator: 'Maya Chen', status: 'live', spend: 420000, roas: 6.4, ctr: 2.8, reach: 1840000 },
    { id: 'c2', name: 'Protein Bar — Always On', brand: 'Fuel Co', creator: 'Rohan Mehta', status: 'live', spend: 280000, roas: 4.9, ctr: 2.1, reach: 1120000 },
    { id: 'c3', name: 'Smart Watch — Launch', brand: 'Pulse Gear', creator: 'Arjun Nair', status: 'live', spend: 650000, roas: 5.7, ctr: 3.2, reach: 2350000 },
    { id: 'c4', name: 'Yoga Mat — Test Batch', brand: 'ZenFlow', creator: 'Priya Sharma', status: 'draft', spend: 0, roas: 0, ctr: 0, reach: 0 },
  ],
  activity: [
    { id: 'a1', type: 'earning', text: 'Maya Chen earned ₹900', meta: 'Glow Labs used her look in an AI ad', time: 'just now' },
    { id: 'a2', type: 'campaign', text: 'Smart Watch campaign hit 5.7x return', meta: 'Pulse Gear · live now', time: '2 min ago' },
    { id: 'a3', type: 'match', text: 'Fuel Co matched with Rohan Mehta', meta: '91% fit · suggested by linc', time: '6 min ago' },
    { id: 'a4', type: 'delivery', text: 'Glow Face Serum video delivered', meta: 'Waiting for brand to check', time: '14 min ago' },
    { id: 'a5', type: 'earning', text: 'Arjun Nair earned ₹1,200', meta: 'Pulse Gear used his look in an AI ad', time: '21 min ago' },
  ],
};

// Tracks whether we're showing live API data or the built-in sample data.
let usingLiveApi = false;

// Fetch JSON from the backend, falling back to bundled sample data.
async function getData(path, key) {
  try {
    const res = await fetch(path);
    if (!res.ok) throw new Error('bad response');
    usingLiveApi = true;
    return await res.json();
  } catch {
    return SAMPLE[key];
  }
}

const views = {
  landing: document.getElementById('landing'),
  brand: document.getElementById('brand'),
  creator: document.getElementById('creator'),
  agency: document.getElementById('agency'),
};

const statusLabels = {
  brief: 'New',
  contract: 'Signing',
  filming: 'Filming',
  review: 'Being checked',
  paid: 'Paid',
};

const pathLabels = {
  video: 'Video',
  'ai-static': 'AI photo',
  'ai-video': 'AI video',
};

const campaignStatusLabels = {
  live: 'Live',
  draft: 'Draft',
  ended: 'Ended',
};

const activityIcons = {
  earning: '₹',
  match: '↔',
  delivery: '✓',
  campaign: '↗',
};

function showView(name) {
  Object.values(views).forEach((el) => el && el.classList.remove('active'));
  views[name]?.classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

document.querySelectorAll('[data-view]').forEach((btn) => {
  btn.addEventListener('click', (e) => {
    e.preventDefault();
    showView(btn.dataset.view);
  });
});

// Plain counts, grouped the Indian way (e.g. 1,84,000)
function formatNumber(n) {
  return Math.round(n).toLocaleString('en-IN');
}

// Rupee amounts. Big numbers are shown short as lakh (L) / crore (Cr).
function formatCurrency(n) {
  if (n >= 10000000) return `₹${(n / 10000000).toFixed(1).replace(/\.0$/, '')}Cr`;
  if (n >= 100000) return `₹${(n / 100000).toFixed(1).replace(/\.0$/, '')}L`;
  return `₹${Math.round(n).toLocaleString('en-IN')}`;
}

function formatCompact(n) {
  if (n >= 10000000) return `${(n / 10000000).toFixed(1).replace(/\.0$/, '')}Cr`;
  if (n >= 100000) return `${(n / 100000).toFixed(1).replace(/\.0$/, '')}L`;
  if (n >= 1000) return `${(n / 1000).toFixed(0)}K`;
  return formatNumber(n);
}

// Count-up animation for a hero stat element
function animateValue(el, target, render) {
  const duration = 1100;
  const start = performance.now();
  function tick(now) {
    const p = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - p, 3);
    el.textContent = render(target * eased);
    if (p < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

async function loadStats() {
  const stats = await getData('/api/stats', 'stats');

  document.querySelectorAll('[data-stat]').forEach((el) => {
    const key = el.dataset.stat;
    const val = stats[key];
    if (val === undefined) return;
    const suffix = el.dataset.suffix || '';

    let render;
    if (key === 'paidToCreators') render = (v) => formatCurrency(v);
    else if (suffix === 'x') render = (v) => `${v.toFixed(1)}x`;
    else render = (v) => formatNumber(v);

    animateValue(el, val, (v) => render(v) + (suffix === 'x' ? '' : suffix));
  });
}

function setApiStatus() {
  const el = document.getElementById('api-status');
  if (!el) return;
  el.textContent = usingLiveApi ? 'Connected' : 'Live demo';
  el.classList.add('connected');
}

async function loadDeals() {
  const container = document.getElementById('deals-table');
  if (!container) return;

  const deals = await getData('/api/deals', 'deals');
  container.innerHTML = `
      <div class="deal-row header">
        <span>Deal</span>
        <span>Brand</span>
        <span>Type</span>
        <span>Stage</span>
        <span>Pay</span>
      </div>
      ${deals
        .map(
          (d) => `
        <div class="deal-row">
          <div>
            <div class="deal-title">${d.title}</div>
            <div class="deal-brand">${d.creator}</div>
          </div>
          <span class="deal-brand">${d.brand}</span>
          <span class="path-tag ${d.path}">${pathLabels[d.path]}</span>
          <span class="status-pill ${d.status}">${statusLabels[d.status]}</span>
          <span class="deal-budget">${formatCurrency(d.budget)}</span>
        </div>
      `,
        )
        .join('')}
    `;
}

async function loadCreators() {
  const container = document.getElementById('creators-grid');
  if (!container) return;

  const creators = await getData('/api/creators', 'creators');
  container.innerHTML = creators
    .map(
        (c) => `
      <div class="creator-card">
        <div class="creator-avatar">${c.avatar}</div>
        <div class="creator-info">
          <h4>${c.name} ${c.certified ? '<span class="license-badge">Certified</span>' : ''}</h4>
          <div class="handle">${c.handle} · ${c.location}</div>
          <div class="creator-meta">
            <span>${c.niche}</span>
            <span>${c.followers} followers</span>
            <span>from ${formatCurrency(c.rate)}</span>
          </div>
        </div>
        <div class="match-score">
          <strong>${c.matchScore}%</strong>
          <span>match</span>
        </div>
      </div>
    `,
    )
    .join('');
}

function renderCampaigns(container, campaigns) {
  container.innerHTML = `
    <div class="campaign-row header">
      <span>Campaign</span>
      <span>Spend</span>
      <span>Return</span>
      <span>Clicks</span>
      <span>Reach</span>
    </div>
    ${campaigns
      .map((c) => {
        const isDraft = c.status !== 'live';
        return `
      <div class="campaign-row">
        <div>
          <div class="deal-title">${c.name}</div>
          <div class="deal-brand">${c.brand} · ${c.creator}
            <span class="status-pill ${c.status === 'live' ? 'filming' : 'contract'}">${campaignStatusLabels[c.status]}</span>
          </div>
        </div>
        <span class="deal-budget">${isDraft ? '—' : formatCurrency(c.spend)}</span>
        <span class="metric ${!isDraft && c.roas >= 5 ? 'good' : ''}">${isDraft ? '—' : c.roas.toFixed(1) + 'x'}</span>
        <span>${isDraft ? '—' : c.ctr.toFixed(1) + '%'}</span>
        <span>${isDraft ? '—' : formatCompact(c.reach)}</span>
      </div>
    `;
      })
      .join('')}
  `;
}

async function loadCampaigns() {
  const targets = ['brand-campaigns', 'agency-campaigns']
    .map((id) => document.getElementById(id))
    .filter(Boolean);
  if (!targets.length) return;

  const campaigns = await getData('/api/campaigns', 'campaigns');
  targets.forEach((el) => renderCampaigns(el, campaigns));
}

function renderActivity(container, items) {
  container.innerHTML = items
    .map(
      (a) => `
    <li>
      <span class="activity-icon ${a.type}">${activityIcons[a.type] || '•'}</span>
      <div>
        <strong>${a.text}</strong>
        <span>${a.meta} · ${a.time}</span>
      </div>
    </li>
  `,
    )
    .join('');
}

async function loadActivity() {
  const targets = ['brand-activity', 'creator-activity', 'agency-activity']
    .map((id) => document.getElementById(id))
    .filter(Boolean);
  if (!targets.length) return;

  const items = await getData('/api/activity', 'activity');
  targets.forEach((el) => renderActivity(el, items));
}

// Load everything, then reflect whether we used the live API or sample data.
Promise.all([
  loadStats(),
  loadDeals(),
  loadCreators(),
  loadCampaigns(),
  loadActivity(),
]).then(setApiStatus);
