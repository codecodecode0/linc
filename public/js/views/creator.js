import { API } from '../services/api.js';
import { getSession, setSession } from '../services/session.js';
import {
  LICENSE_STATUS,
  MEDIA_SCOPE,
  PAYOUT_METHODS,
  RATE_MODEL,
} from '../shared/constants.js';
import { formData, root, toast } from '../shared/dom.js';
import { compactNumber, esc, inr, titleCase } from '../shared/format.js';
import { badge, quickCard, select, shell } from '../components/ui.js';
import { dealAction, dealDetail } from './deals.js';

export function routeCreator(parts) {
  const sub = parts[1] || '';
  if (sub === 'profile') return creatorProfile();
  if (sub === 'social') return creatorSocial();
  if (sub === 'licenses') return creatorLicenses();
  if (sub === 'payouts') return creatorPayouts();
  if (sub === 'deals' && parts[2]) return dealDetail(parts[2], 'creator');
  if (sub === 'deals') return creatorDeals();
  return creatorHome();
}

async function creatorHome() {
  const creator = getSession().account;
  const [board, licenses, deals, activity] = await Promise.all([
    socialBoardHtml(creator.id),
    API.get(`/api/creators/${creator.id}/licenses`).catch(() => []),
    API.get(`/api/creators/${creator.id}/deals`).catch(() => []),
    API.get('/api/activity').catch(() => []),
  ]);
  const booked = deals
    .filter((d) => ['accepted', 'approved', 'completed'].includes(d.status))
    .reduce((sum, d) => sum + Number(d.quoteAmount || 0), 0);
  const activeLicense = licenses.some((l) => l.status === 'active');
  const certBadge = creator.certified
    ? ` <span class="certified-badge inline"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M9 12l2 2 4-4 1.4 1.4L11 16.8 7.6 13.4z"/><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.6"/></svg> Certified Digi Creator</span>`
    : '';

  shell('', `
    <div class="dash-header">
      <div><h2>Creator home</h2><p class="dash-sub">${esc(creator.name)} · ${esc(creator.handle || '')}${certBadge}</p></div>
      <div class="earnings-pill"><span>Booked</span><strong>${inr(booked)}</strong><small>this month</small></div>
    </div>
    <div class="dash-grid">
      <div class="dash-main">
        <div class="panel social-panel">
          <div class="panel-head"><h3>Connected accounts</h3><span class="panel-meta">Show brands your real numbers</span></div>
          <div id="social-body">${board}</div>
        </div>
        <div class="panel">
          <div class="panel-head"><h3>Your deals</h3><span class="panel-meta">Latest offers</span></div>
          ${creatorDealsPanel(deals)}
        </div>
        <div class="panel">
          <div class="panel-head"><h3>Earn from your look</h3>${activeLicense ? '<span class="status-pill paid">On</span>' : ''}</div>
          ${licensePanel(licenses)}
        </div>
      </div>
      <aside class="dash-sidebar">
        <div class="panel">
          <div class="panel-head"><h3>Where your money comes from</h3></div>
          ${earningsChartPanel(deals)}
        </div>
        <div class="panel">
          <div class="panel-head"><h3>Recent activity</h3></div>
          <ul class="activity-list">${activityListItems(activity)}</ul>
        </div>
      </aside>
    </div>`);
  wireSocialBoard(creator.id);
}

async function creatorProfile() {
  const creator = getSession().account;
  shell('profile', `
    <div class="page-head"><h1>Profile</h1><p class="sub">This information helps brands understand your fit.</p></div>
    <section class="workspace-panel"><form id="pf" class="campaign-form">
      <div class="field"><label>Name</label><input name="name" value="${esc(creator.name)}" required /></div>
      <div class="field"><label>Niche</label><input name="niche" value="${esc(creator.niche || '')}" /></div>
      <div class="field"><label>City</label><input name="city" value="${esc(creator.city || '')}" /></div>
      <div class="field"><label>Starting rate (₹)</label><input name="rate" type="number" value="${creator.rate || 0}" /></div>
      <div class="field span-2"><label>Bio</label><textarea name="bio" rows="4">${esc(creator.bio || '')}</textarea></div>
      <button class="btn btn-primary" type="submit">Save profile</button>
    </form></section>`);
  document.getElementById('pf').onsubmit = async (event) => {
    event.preventDefault();
    const data = formData(event.target);
    data.rate = Number(data.rate) || 0;
    try {
      const updated = await API.patch(`/api/creators/${creator.id}`, data);
      setSession({ ...getSession(), account: updated });
      toast('Profile saved', 'success');
      creatorProfile();
    } catch (err) {
      toast(err.detail || 'Could not save profile', 'error');
    }
  };
}

async function creatorSocial() {
  const id = getSession().account.id;
  const platforms = [
    { key: 'instagram', label: 'Instagram' },
    { key: 'youtube', label: 'YouTube' },
  ];
  let connections = [];
  try { connections = await API.get(`/api/creators/${id}/connections`); } catch {}
  const cards = platforms
    .map((platform) => {
      const connection = connections.find((item) => item.platform === platform.key);
      if (!connection) {
        const ret = encodeURIComponent('/app.html#/creator/social');
        return `<article class="deal-card"><div class="deal-card-top"><div><h3>${platform.label}</h3><p>Not connected</p></div>${badge('pending')}</div>
          <a class="btn btn-primary btn-sm" href="/api/auth/${platform.key}/login?creator_id=${id}&return_to=${ret}">Connect ${platform.label}</a></article>`;
      }
      return `<article class="deal-card"><div class="deal-card-top"><div><h3>${platform.label}</h3><p>${esc(connection.username || '')}</p></div>${badge(connection.status)}</div>
        <div class="deal-facts"><div><span>Followers</span><strong>${Number(connection.followersCount || 0).toLocaleString('en-IN')}</strong></div><div><span>Source</span><strong>${esc(titleCase(connection.source || 'Mock'))}</strong></div></div>
        <button class="btn btn-danger btn-sm" data-disconnect="${platform.key}">Disconnect</button></article>`;
    })
    .join('');
  shell('social', `
    <div class="page-head"><div><h1>Social accounts</h1><p class="sub">Connect accounts so brands can trust your real numbers.</p></div></div>
    <div class="deal-board">${cards}</div>`);
  root.querySelectorAll('[data-disconnect]').forEach((button) => {
    button.onclick = async () => {
      await API.del(`/api/creators/${id}/connections/${button.dataset.disconnect}`);
      toast('Disconnected', 'success');
      creatorSocial();
    };
  });
}

async function creatorLicenses() {
  const id = getSession().account.id;
  let list = [];
  try { list = await API.get(`/api/creators/${id}/licenses`); } catch {}
  const rows = list.length
    ? list
        .map((license) => `<tr>
          <td>${esc(titleCase(license.mediaScope))}</td>
          <td>${esc(titleCase(license.rateModel))}</td>
          <td>${inr(license.rateAmount)}</td>
          <td>${badge(license.status)}</td>
          <td class="actions">
            <button class="btn btn-soft btn-sm" data-toggle="${license.id}" data-status="${license.status}">${license.status === 'active' ? 'Pause' : 'Activate'}</button>
            <button class="btn btn-danger btn-sm" data-del="${license.id}">Delete</button>
          </td></tr>`)
        .join('')
    : `<tr><td colspan="5" class="empty">No likeness licenses yet.</td></tr>`;
  shell('licenses', `
    <div class="page-head"><h1>Likeness licensing</h1><p class="sub">Let brands make approved AI ads with your look.</p></div>
    <section class="workspace-panel"><form id="lf" class="inline-form">
      <div class="field"><label>Media scope</label>${select('mediaScope', MEDIA_SCOPE, 'static')}</div>
      <div class="field"><label>Rate model</label>${select('rateModel', RATE_MODEL, 'per_generation')}</div>
      <div class="field"><label>Rate (₹)</label><input name="rateAmount" type="number" value="1000" /></div>
      <div class="field"><label>Status</label>${select('status', LICENSE_STATUS, 'active')}</div>
      <button class="btn btn-primary" type="submit">Add license</button>
    </form></section>
    <section class="workspace-panel"><table class="tbl"><thead><tr><th>Scope</th><th>Rate model</th><th>Rate</th><th>Status</th><th></th></tr></thead><tbody>${rows}</tbody></table></section>`);
  document.getElementById('lf').onsubmit = async (event) => {
    event.preventDefault();
    const data = formData(event.target);
    data.rateAmount = Number(data.rateAmount) || 0;
    try { await API.post(`/api/creators/${id}/licenses`, data); toast('License added', 'success'); creatorLicenses(); }
    catch (err) { toast(err.detail || 'Failed', 'error'); }
  };
  root.querySelectorAll('[data-toggle]').forEach((button) => {
    button.onclick = async () => {
      const next = button.dataset.status === 'active' ? 'paused' : 'active';
      await API.patch(`/api/licenses/${button.dataset.toggle}`, { status: next });
      creatorLicenses();
    };
  });
  root.querySelectorAll('[data-del]').forEach((button) => {
    button.onclick = async () => {
      await API.del(`/api/licenses/${button.dataset.del}`);
      toast('Deleted', 'success');
      creatorLicenses();
    };
  });
}

async function creatorPayouts() {
  const id = getSession().account.id;
  let list = [];
  try { list = await API.get(`/api/creators/${id}/payout-accounts`); } catch {}
  const rows = list.length
    ? list
        .map((account) => `<tr>
          <td>${esc(titleCase(account.method))}</td>
          <td>${esc(account.method === 'upi' ? account.upiVpa || '' : `${account.accountName || ''} · ${account.ifsc || ''}`)}</td>
          <td>${badge(account.verification)}</td>
          <td>${account.isDefault ? badge('default') : ''}</td>
          <td class="actions"><button class="btn btn-danger btn-sm" data-del="${account.id}">Delete</button></td></tr>`)
        .join('')
    : `<tr><td colspan="5" class="empty">No payout accounts yet.</td></tr>`;
  shell('payouts', `
    <div class="page-head"><h1>Payout accounts</h1><p class="sub">Where linc sends your earnings.</p></div>
    <section class="workspace-panel"><form id="pf" class="inline-form">
      <div class="field"><label>Method</label>${select('method', PAYOUT_METHODS, 'upi')}</div>
      <div class="field"><label>Account name</label><input name="accountName" required /></div>
      <div class="field"><label>UPI VPA</label><input name="upiVpa" placeholder="name@upi" /></div>
      <div class="field"><label>Account number</label><input name="accountNumber" /></div>
      <div class="field"><label>IFSC</label><input name="ifsc" /></div>
      <button class="btn btn-primary" type="submit">Add account</button>
    </form></section>
    <section class="workspace-panel"><table class="tbl"><thead><tr><th>Method</th><th>Details</th><th>Status</th><th></th><th></th></tr></thead><tbody>${rows}</tbody></table></section>`);
  document.getElementById('pf').onsubmit = async (event) => {
    event.preventDefault();
    const data = formData(event.target);
    Object.keys(data).forEach((key) => data[key] === '' && delete data[key]);
    try { await API.post(`/api/creators/${id}/payout-accounts`, data); toast('Added', 'success'); creatorPayouts(); }
    catch (err) { toast(err.detail || 'Failed', 'error'); }
  };
  root.querySelectorAll('[data-del]').forEach((button) => {
    button.onclick = async () => {
      await API.del(`/api/payout-accounts/${button.dataset.del}`);
      toast('Deleted', 'success');
      creatorPayouts();
    };
  });
}

async function creatorDeals() {
  const id = getSession().account.id;
  let list = [];
  try { list = await API.get(`/api/creators/${id}/deals`); } catch {}
  const cards = list.length
    ? list.map(dealCard).join('')
    : `<div class="empty-state"><h3>No deals yet</h3><p>Brand offers will appear here with clear pricing, deliverables and response buttons.</p></div>`;
  shell('deals', `
    <div class="page-head"><div><h1>Your deals</h1><p class="sub">Review offers quickly. Accept, negotiate or decline without touching technical status fields.</p></div></div>
    <div class="deal-board">${cards}</div>`);
  root.querySelectorAll('[data-deal-action]').forEach((button) => {
    button.onclick = async () => {
      try {
        await dealAction(button.dataset.dealAction, button.dataset.status);
        toast(`Deal ${titleCase(button.dataset.status)}`, 'success');
        creatorDeals();
      } catch (err) {
        toast(err.detail || 'Action not allowed', 'error');
      }
    };
  });
  root.querySelectorAll('[data-counter-form]').forEach((form) => {
    form.onsubmit = async (event) => {
      event.preventDefault();
      const current = list.find((deal) => deal.id === form.dataset.counterForm);
      const data = formData(form);
      const quote = Number(data.quoteAmount) || current?.quoteAmount || 0;
      try {
        await dealAction(form.dataset.counterForm, 'negotiate', { quoteAmount: quote });
        toast('Counter offer sent', 'success');
        creatorDeals();
      } catch (err) {
        toast(err.detail || 'Action not allowed', 'error');
      }
    };
  });
}

function dealCard(deal) {
  const brief = deal.brief || {};
  const canAct = deal.status === 'offered' && deal.lastOfferBy === 'brand';
  const waiting = deal.status === 'countered' && deal.lastOfferBy === 'creator';
  return `<article class="deal-card">
    <div class="deal-card-top">
      <div><span class="eyebrow">${esc(titleCase(deal.type))}</span><h3>${esc(brief.campaign || 'Creator offer')}</h3></div>
      ${badge(deal.status)}
    </div>
    <p>${esc(brief.deliverables || 'Deliver creator content for this campaign.')}</p>
    <div class="deal-facts">
      <div><span>Offer</span><strong>${inr(deal.quoteAmount)}</strong></div>
      <div><span>Objective</span><strong>${esc(titleCase(brief.objective || 'Campaign'))}</strong></div>
      <div><span>Category</span><strong>${esc(brief.productCategory || 'General')}</strong></div>
    </div>
    <div class="deal-actions">
      ${
        canAct
          ? `<button class="btn btn-primary btn-sm" data-deal-action="${deal.id}" data-status="accept">Accept</button>
             <button class="btn btn-danger btn-sm" data-deal-action="${deal.id}" data-status="reject">Reject</button>`
          : waiting
            ? `<span class="brief-box muted">Waiting for brand response</span>`
            : `<a class="btn btn-soft btn-sm" href="#/creator/deals/${deal.id}">Open details</a>`
      }
    </div>
    ${
      canAct
        ? `<form class="counter-inline" data-counter-form="${deal.id}">
            <label>Counter price</label>
            <input name="quoteAmount" type="number" min="1" value="${Number(deal.quoteAmount || 0)}" />
            <button class="btn btn-soft btn-sm" type="submit">Negotiate</button>
          </form>`
        : ''
    }
  </article>`;
}

// ----- Home dashboard helpers (reuse landing dashboard markup/classes) -----

const SOCIAL_PLATFORMS = [
  { key: 'instagram', label: 'Instagram' },
  { key: 'youtube', label: 'YouTube' },
];
const ACTIVITY_ICON = { earning: '₹', campaign: '↗', match: '↔', delivery: '✓' };
const DEAL_PILL = {
  offered: 'review', countered: 'review', in_review: 'review', content_submitted: 'review',
  accepted: 'paid', approved: 'paid', completed: 'paid', paid: 'paid',
  contracted: 'filming', in_production: 'filming',
};
const DEAL_PROGRESS = {
  offered: 20, countered: 25, accepted: 40, contracted: 60, in_production: 70,
  content_submitted: 80, in_review: 80, revisions: 75, approved: 90, completed: 100,
};

function platformIcon(key) {
  if (key === 'youtube') {
    return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="2.5" y="5.5" width="19" height="13" rx="4" /><path d="M10 9.5l5 2.5-5 2.5z" fill="currentColor" stroke="none" /></svg>`;
  }
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="18" height="18" rx="5" /><circle cx="12" cy="12" r="4" /><circle cx="17.5" cy="6.5" r="1.2" fill="currentColor" stroke="none" /></svg>`;
}

const socialBar = (pct, max) =>
  `<span class="ig-bar"><span style="width:${Math.min((pct / max) * 100, 100)}%"></span></span>`;

function metricValue(metric) {
  if (metric.format === 'percent') return `${metric.value}%`;
  if (metric.format === 'hours') return `${compactNumber(metric.value)}h`;
  if (metric.format === 'duration') {
    const m = Math.floor(metric.value / 60);
    const s = Math.round(metric.value % 60);
    return `${m}:${String(s).padStart(2, '0')}`;
  }
  return compactNumber(metric.value);
}

async function socialBoardHtml(id) {
  let connections = [];
  try { connections = await API.get(`/api/creators/${id}/connections`); } catch {}
  const cards = await Promise.all(
    SOCIAL_PLATFORMS.map(async (p) => {
      const conn = connections.find((c) => c.platform === p.key);
      if (!conn) {
        const ret = encodeURIComponent('/app.html#/creator');
        return `<div class="social-card"><div class="social-connect">
          <div class="social-logo ${p.key}">${platformIcon(p.key)}</div>
          <div class="social-connect-copy"><h4>Connect ${p.label}</h4><p>Show brands your real ${p.label} numbers — followers, engagement and audience.</p></div>
          <a class="btn btn-primary" href="/api/auth/${p.key}/login?creator_id=${id}&return_to=${ret}">Connect ${p.label}</a>
        </div></div>`;
      }
      let ins = null;
      try { ins = await API.get(`/api/creators/${id}/insights/${p.key}`); } catch {}
      if (!ins) {
        return `<div class="social-card"><div class="social-insights"><div class="ig-head">
          <div class="social-logo sm ${p.key}">${platformIcon(p.key)}</div>
          <div><strong>${esc(conn.username || '')}</strong><span>${p.label} · connected</span></div>
          <button class="ig-disconnect" data-disconnect="${p.key}">Disconnect</button></div></div></div>`;
      }
      const maxAge = Math.max(...ins.audience.ageGender.map((a) => a.female + a.male));
      const tiles = [
        `<div><span>${esc(ins.followersLabel)}</span><strong>${compactNumber(ins.followers)}</strong></div>`,
        ...ins.metrics.map((m) => `<div><span>${esc(m.label)}</span><strong>${metricValue(m)}</strong></div>`),
      ].join('');
      return `<div class="social-card"><div class="social-insights">
        <div class="ig-head">
          <div class="social-logo sm ${p.key}">${platformIcon(p.key)}</div>
          <div><strong>${p.key === 'youtube' ? '' : '@'}${esc(ins.username)}</strong><span>${p.label} · connected</span></div>
          <span class="ig-tag">${ins.source === 'live' ? 'Live data' : 'Sample data'}</span>
          <button class="ig-disconnect" data-disconnect="${p.key}">Disconnect</button>
        </div>
        <div class="ig-metrics">${tiles}</div>
        <div class="ig-cols">
          <div class="ig-block"><h5>Audience age &amp; gender</h5>
            ${ins.audience.ageGender.map((a) => `<div class="ig-row"><span class="ig-label">${esc(a.label)}</span>${socialBar(a.female + a.male, maxAge)}<span class="ig-val">${(a.female + a.male).toFixed(0)}%</span></div>`).join('')}
            <div class="ig-legend"><span class="dot-f"></span>Women &nbsp;<span class="dot-m"></span>Men</div></div>
          <div class="ig-block"><h5>Top cities</h5>
            ${ins.audience.topCities.map((c) => `<div class="ig-row"><span class="ig-label">${esc(c.name)}</span>${socialBar(c.share, ins.audience.topCities[0].share)}<span class="ig-val">${c.share}%</span></div>`).join('')}</div>
        </div></div></div>`;
    }),
  );
  return cards.join('');
}

function wireSocialBoard(id) {
  root.querySelectorAll('[data-disconnect]').forEach((button) => {
    button.onclick = async () => {
      await API.del(`/api/creators/${id}/connections/${button.dataset.disconnect}`);
      toast('Disconnected', 'success');
      creatorHome();
    };
  });
}

function creatorDealsPanel(deals) {
  if (!deals.length) {
    return `<div class="creator-deals"><p style="padding:1rem;text-align:center;color:var(--text-dim);font-size:.9rem">No deals yet. Brand offers will show up here.</p></div>`;
  }
  return `<div class="creator-deals">${deals
    .slice(0, 3)
    .map((d) => {
      const brief = d.brief || {};
      const pct = DEAL_PROGRESS[d.status] || 30;
      return `<div class="creator-deal-card">
        <div class="deal-top"><span class="status-pill ${DEAL_PILL[d.status] || 'contract'}">${esc(titleCase(d.status))}</span><span class="deal-amount">${inr(d.quoteAmount)}</span></div>
        <h4>${esc(brief.campaign || titleCase(d.type))}</h4>
        <p>${esc(brief.productCategory || titleCase(d.type))} · <a href="#/creator/deals/${d.id}">Open</a></p>
        <div class="deal-progress"><div class="bar ${pct >= 100 ? 'done' : ''}" style="width:${pct}%"></div></div>
      </div>`;
    })
    .join('')}</div>`;
}

function licensePanel(licenses) {
  const active = licenses.filter((l) => l.status === 'active');
  const top = licenses.reduce((m, l) => Math.max(m, Number(l.rateAmount || 0)), 0);
  const copy = active.length
    ? 'Brands can make approved AI ads with your look — and you get paid every time.'
    : 'Add a license to let brands make AI ads with your look and earn passively.';
  return `<p class="license-copy">${copy} <a href="#/creator/licenses">Manage licensing</a></p>
    <div class="license-stats">
      <div><span>Licenses</span><strong>${licenses.length}</strong></div>
      <div><span>Active</span><strong>${active.length}</strong></div>
      <div><span>Top rate</span><strong>${inr(top)}</strong></div>
    </div>`;
}

function earningsChartPanel(deals) {
  const sum = (statuses) => deals.filter((d) => statuses.includes(d.status)).reduce((s, d) => s + Number(d.quoteAmount || 0), 0);
  const booked = sum(['accepted', 'approved', 'completed']);
  const production = sum(['contracted', 'in_production']);
  const pending = sum(['offered', 'countered', 'in_review', 'content_submitted']);
  const max = Math.max(booked, production, pending, 1);
  const h = (v) => `${Math.max(8, Math.round((v / max) * 100))}%`;
  return `<div class="earnings-chart">
    <div class="chart-bar accent" style="--h:${h(booked)}"><span>Booked</span><strong>${inr(booked)}</strong></div>
    <div class="chart-bar" style="--h:${h(production)}"><span>Production</span><strong>${inr(production)}</strong></div>
    <div class="chart-bar" style="--h:${h(pending)}"><span>Pending</span><strong>${inr(pending)}</strong></div>
  </div>`;
}

function activityListItems(items) {
  if (!items.length) return '<li class="table-loading">No activity yet.</li>';
  return items
    .map((a) => `<li><span class="activity-icon ${a.type}">${ACTIVITY_ICON[a.type] || '•'}</span><div><strong>${esc(a.text)}</strong><span>${esc(a.meta)} · ${esc(a.time)}</span></div></li>`)
    .join('');
}
