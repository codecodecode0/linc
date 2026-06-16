import { API } from '../services/api.js';
import { getSession } from '../services/session.js';
import { OBJECTIVES, PAY_KINDS } from '../shared/constants.js';
import { formData, root, toast } from '../shared/dom.js';
import { esc, inr, titleCase } from '../shared/format.js';
import { recommendationPlan } from '../services/recommendations.js';
import { badge, quickCard, select, shell } from '../components/ui.js';
import { dealDetail } from './deals.js';

export function routeBrand(parts) {
  const sub = parts[1] || '';
  if (sub === 'campaigns' && parts[2]) return campaignDetail(parts[2]);
  if (sub === 'campaigns') return brandCampaigns();
  if (sub === 'creators') return brandCreators();
  if (sub === 'payments') return brandPayments();
  if (sub === 'deals' && parts[2]) return dealDetail(parts[2], 'brand');
  return brandHome();
}

async function brandHome() {
  const brand = getSession().account;
  const [campaigns, creators, activity] = await Promise.all([
    API.get(`/api/brands/${brand.id}/campaigns`).catch(() => []),
    API.get('/api/creators').catch(() => []),
    API.get('/api/activity').catch(() => []),
  ]);
  const active = campaigns.filter((c) => c.status === 'active').length;
  const totalBudget = campaigns.reduce((sum, c) => sum + Number(c.budgetAmount || 0), 0);

  const campaignRows = campaigns.length
    ? campaigns
        .slice(0, 6)
        .map((c) => `<tr>
          <td><a href="#/brand/campaigns/${c.id}">${esc(c.name)}</a></td>
          <td>${esc(titleCase(c.objective))}</td>
          <td>${inr(c.budgetAmount)}</td>
          <td>${badge(c.status)}</td></tr>`)
        .join('')
    : `<tr><td colspan="4" class="empty">No campaigns yet — create your first one.</td></tr>`;
  const creatorCards = creators.length
    ? creators.map(creatorSuggestCard).join('')
    : `<div class="table-loading">No creators yet.</div>`;

  shell('', `
    <div class="dash-header">
      <div><h2>Brand home</h2><p class="dash-sub">${esc(brand.name)} · ${esc(brand.category || 'Marketing')}</p></div>
      <a class="btn btn-primary" href="#/brand/campaigns">+ New campaign</a>
    </div>
    <div class="dash-grid">
      <div class="dash-main">
        <div class="panel">
          <div class="panel-head"><h3>Your campaigns</h3><span class="panel-meta">Updated live</span></div>
          <div class="deals-table"><table class="tbl"><thead><tr><th>Name</th><th>Objective</th><th>Budget</th><th>Status</th></tr></thead><tbody>${campaignRows}</tbody></table></div>
        </div>
        <div class="panel">
          <div class="panel-head"><h3>Creators we suggest</h3><span class="panel-meta">Picked for your brand</span></div>
          <div class="creators-grid">${creatorCards}</div>
        </div>
      </div>
      <aside class="dash-sidebar">
        <div class="panel ai-panel">
          <div class="panel-head"><h3>Make AI photo ads</h3></div>
          <div class="ai-preview">
            <div class="ai-canvas"><div class="ai-variant v1"></div><div class="ai-variant v2"></div><div class="ai-variant v3"></div></div>
            <p class="ai-caption">Turn one creator shoot into dozens of AI photo ads — with their approval.</p>
            <a class="btn btn-outline btn-block" href="#/brand/creators">Find a creator</a>
          </div>
        </div>
        <div class="panel">
          <div class="panel-head"><h3>At a glance</h3></div>
          <ul class="sidebar-stats">
            <li><span>Campaigns</span><strong>${campaigns.length}</strong></li>
            <li><span>Active</span><strong>${active}</strong></li>
            <li><span>Total budget</span><strong>${inr(totalBudget)}</strong></li>
            <li><span>Creators available</span><strong>${creators.length}</strong></li>
          </ul>
        </div>
        <div class="panel">
          <div class="panel-head"><h3>Live activity</h3></div>
          <ul class="activity-list">${activityListItems(activity)}</ul>
        </div>
      </aside>
    </div>`);
}

async function brandCampaigns() {
  const brand = getSession().account;
  let campaigns = [];
  try { campaigns = await API.get(`/api/brands/${brand.id}/campaigns`); } catch {}
  const rows = campaigns.length
    ? campaigns
        .map((campaign) => `<tr>
          <td><a href="#/brand/campaigns/${campaign.id}">${esc(campaign.name)}</a></td>
          <td>${esc(titleCase(campaign.objective))}</td>
          <td>${inr(campaign.budgetAmount)}</td>
          <td>${badge(campaign.status)}</td>
          <td class="actions"><a class="btn btn-soft btn-sm" href="#/brand/campaigns/${campaign.id}">Open</a></td></tr>`)
        .join('')
    : `<tr><td colspan="5" class="empty">No campaigns yet — create your first one.</td></tr>`;
  shell('campaigns', `
    <div class="page-head"><div><h1>Campaigns</h1><p class="sub">Plan creator campaigns with enough context for strong recommendations.</p></div></div>
    <section class="workspace-panel">
      <div class="panel-title">
        <div><h3>Create a campaign</h3><p>Brief is optional, but category, objective and budget make recommendations sharper.</p></div>
      </div>
      <form id="cf" class="campaign-form">
        <div class="field"><label>Campaign name</label><input name="name" placeholder="Glow serum launch" required /></div>
        <div class="field"><label>Product category</label><input name="productCategory" value="${esc(brand.category || '')}" placeholder="Beauty, food, tech..." /></div>
        <div class="field"><label>Objective</label>${select('objective', OBJECTIVES, 'conversions')}</div>
        <div class="field"><label>Budget (₹)</label><input name="budgetAmount" type="number" min="0" step="5000" value="150000" /></div>
        <div class="field span-2"><label>Target audience</label><input name="audience" placeholder="Women 18-34 in Mumbai and Delhi, premium skincare buyers" /></div>
        <div class="field span-2"><label>Campaign brief <span class="optional-label">optional</span></label><textarea name="brief" rows="4" placeholder="What should creators communicate? Include product benefits, tone, must-haves and avoid-list."></textarea></div>
        <button class="btn btn-primary" type="submit">Create campaign</button>
      </form>
    </section>
    <section class="workspace-panel">
      <div class="panel-title"><div><h3>Campaign pipeline</h3><p>Draft campaigns can be refined before sending creator offers.</p></div></div>
      <table class="tbl"><thead><tr><th>Name</th><th>Objective</th><th>Budget</th><th>Status</th><th></th></tr></thead><tbody>${rows}</tbody></table>
    </section>`);
  document.getElementById('cf').onsubmit = async (event) => {
    event.preventDefault();
    const data = formData(event.target);
    data.budgetAmount = Number(data.budgetAmount) || 0;
    data.targetAudience = { summary: data.audience || '', brief: data.brief || '' };
    delete data.audience;
    delete data.brief;
    Object.keys(data).forEach((key) => data[key] === '' && delete data[key]);
    try {
      await API.post(`/api/brands/${brand.id}/campaigns`, data);
      toast('Campaign created', 'success');
      brandCampaigns();
    } catch (err) {
      toast(err.detail || 'Failed', 'error');
    }
  };
}

async function campaignDetail(campaignId) {
  const brand = getSession().account;
  let campaign;
  let deals = [];
  let creators = [];
  try { campaign = await API.get(`/api/campaigns/${campaignId}`); } catch { location.hash = '#/brand/campaigns'; return; }
  try { deals = await API.get(`/api/campaigns/${campaignId}/deals`); } catch {}
  try { creators = await API.get('/api/creators'); } catch {}

  const creatorName = (id) => (creators.find((creator) => creator.id === id) || {}).name || id;
  const existingCreatorIds = new Set(deals.map((deal) => deal.creatorId));
  const plan = recommendationPlan(campaign, creators, brand);
  const committed = deals.reduce((sum, deal) => sum + Number(deal.quoteAmount || 0), 0);
  const remainingBudget = Math.max(0, Number(campaign.budgetAmount || 0) - committed);
  const brief = (campaign.targetAudience && campaign.targetAudience.brief) || '';
  const audience = (campaign.targetAudience && campaign.targetAudience.summary) || '';

  const recommendationCards = plan.length
    ? plan.map((item) => recommendationCard(item, existingCreatorIds)).join('')
    : `<p class="empty">Add a budget and creator pool to generate recommendations.</p>`;
  const dealRows = deals.length
    ? deals
        .map((deal) => `<tr>
          <td>${esc(creatorName(deal.creatorId))}</td>
          <td>${esc((deal.deliverables || []).map((d) => `${d.quantity}x ${titleCase(d.type)}`).join(', ') || titleCase(deal.type))}</td>
          <td>${inr(deal.quoteAmount)}</td>
          <td>${badge(deal.status)}</td>
          <td class="actions"><a class="btn btn-soft btn-sm" href="#/brand/deals/${deal.id}">Manage</a></td></tr>`)
        .join('')
    : `<tr><td colspan="5" class="empty">No creator offers yet. Start with the recommended plan below.</td></tr>`;

  shell('campaigns', `
    <button class="back" onclick="location.hash='#/brand/campaigns'">&larr; Campaigns</button>
    <div class="page-head"><div><h1>${esc(campaign.name)}</h1>
      <p class="sub">${esc(titleCase(campaign.objective))} · ${badge(campaign.status)} · ${esc(campaign.productCategory || brand.category || 'General')} · Budget ${inr(campaign.budgetAmount)}</p></div></div>
    <div class="stat-row">
      <div class="tile"><span>Total budget</span><strong>${inr(campaign.budgetAmount)}</strong></div>
      <div class="tile"><span>Committed</span><strong>${inr(committed)}</strong></div>
      <div class="tile"><span>Remaining</span><strong>${inr(remainingBudget)}</strong></div>
    </div>
    <section class="workspace-panel">
      <div class="panel-title">
        <div><h3>Campaign context</h3><p>${esc(audience || 'No audience note added yet.')}</p></div>
        <form id="sf" class="status-form">
          ${select('status', ['draft', 'active', 'paused', 'completed', 'archived'], campaign.status)}
          <button class="btn btn-soft btn-sm" type="submit">Update</button>
        </form>
      </div>
      ${brief ? `<p class="brief-box">${esc(brief)}</p>` : `<p class="brief-box muted">No written brief yet. You can still use recommendations from category, objective and budget.</p>`}
    </section>
    <section class="workspace-panel">
      <div class="panel-title">
        <div><h3>Recommended creator plan</h3><p>Built from budget, category fit, engagement, audience profile and fair starting rates.</p></div>
      </div>
      <div class="recommendation-grid">${recommendationCards}</div>
    </section>
    <section class="workspace-panel">
      <div class="panel-title"><div><h3>Creator offers</h3><p>Keep offers simple for creators: clear price, deliverables and next action.</p></div></div>
      <table class="tbl"><thead><tr><th>Creator</th><th>Deliverables</th><th>Quote</th><th>Status</th><th></th></tr></thead><tbody>${dealRows}</tbody></table>
    </section>`);
  document.getElementById('sf').onsubmit = async (event) => {
    event.preventDefault();
    await API.patch(`/api/campaigns/${campaignId}`, { status: formData(event.target).status });
    toast('Updated', 'success');
    campaignDetail(campaignId);
  };
  root.querySelectorAll('[data-offer]').forEach((button) => {
    button.onclick = async () => {
      const creator = creators.find((item) => item.id === button.dataset.offer);
      const planItem = plan.find((item) => item.creator.id === button.dataset.offer);
      const deliverables = [
        {
          title: `${planItem?.videos || 1} creator video${(planItem?.videos || 1) > 1 ? 's' : ''}`,
          type: button.dataset.type,
          quantity: planItem?.videos || 1,
          notes: `Recommended for ${titleCase(campaign.objective)} based on audience and rate fit.`,
        },
      ];
      const payload = {
        creatorId: button.dataset.offer,
        type: button.dataset.type,
        quoteAmount: Number(button.dataset.quote) || 0,
        status: 'offered',
        deliverables,
        brief: {
          campaign: campaign.name,
          objective: campaign.objective,
          productCategory: campaign.productCategory || brand.category || '',
          audience,
          brief,
          deliverables: deliverables.map((item) => `${item.quantity}x ${titleCase(item.type)}`).join(', '),
          whyThisCreator: planItem?.rationale || [],
        },
      };
      try {
        await API.post(`/api/campaigns/${campaignId}/deals`, payload);
        toast(`Offer sent to ${creator ? creator.name : 'creator'}`, 'success');
        campaignDetail(campaignId);
      } catch (err) {
        toast(err.detail || 'Failed', 'error');
      }
    };
  });
}

function recommendationCard(item, existingCreatorIds) {
  return `<article class="recommendation-card">
    <div class="rec-head">
      <div class="creator-avatar">${esc(item.creator.avatar || item.creator.name.slice(0, 2).toUpperCase())}</div>
      <div><h4>${esc(item.creator.name)}</h4><p>${esc(item.creator.niche || 'Creator')} · ${esc(item.creator.city || 'India')}</p></div>
      <strong>${item.score}%</strong>
    </div>
    <div class="rec-meta">
      <span>${inr(item.quote)} allocation</span>
      <span>${item.videos} ${item.videos === 1 ? 'video' : 'videos'}</span>
      <span>${esc(titleCase(item.type))}</span>
    </div>
    <p class="rec-audience">${esc(item.audience.audience)}</p>
    <ul class="reason-list">${item.rationale.map((reason) => `<li>${esc(reason)}</li>`).join('')}</ul>
    <button class="btn btn-primary btn-sm" data-offer="${item.creator.id}" data-type="${item.type}" data-quote="${item.quote}" ${existingCreatorIds.has(item.creator.id) ? 'disabled' : ''}>
      ${existingCreatorIds.has(item.creator.id) ? 'Offer sent' : 'Send recommended offer'}
    </button>
  </article>`;
}

async function brandCreators() {
  let creators = [];
  try { creators = await API.get('/api/creators'); } catch {}
  const cards = creators
    .map((creator) => `<div class="card">
      <div style="display:flex;gap:.75rem;align-items:center;margin-bottom:.75rem">
        <div class="creator-avatar">${esc(creator.avatar || (creator.name || '?').slice(0, 2).toUpperCase())}</div>
        <div><strong>${esc(creator.name)}</strong> ${creator.certified ? badge('certified') : ''}<br>
        <span style="color:var(--text-muted);font-size:.8rem">${esc(creator.handle || '')} ${creator.city ? '· ' + esc(creator.city) : ''}</span></div>
      </div>
      <div style="color:var(--text-muted);font-size:.85rem">${esc(creator.niche || '')}${creator.followers ? ' · ' + esc(creator.followers) + ' followers' : ''}</div>
      <div style="margin-top:.5rem;font-weight:600">${inr(creator.rate)} <span style="font-weight:400;color:var(--text-dim);font-size:.8rem">starting</span></div>
    </div>`)
    .join('');
  shell('creators', `
    <div class="page-head"><div><h1>Find creators</h1><p class="sub">Browse creators, then offer deals from a campaign.</p></div></div>
    <div class="card-grid">${cards || '<p class="empty">No creators yet.</p>'}</div>`);
}

async function brandPayments() {
  const brand = getSession().account;
  let methods = [];
  try { methods = await API.get(`/api/brands/${brand.id}/payment-methods`); } catch {}
  const rows = methods.length
    ? methods
        .map((method) => `<tr>
          <td>${esc(method.gateway)}</td>
          <td>${esc(titleCase(method.kind))}</td>
          <td>${esc(method.label)}</td>
          <td>${method.isDefault ? badge('default') : ''}</td>
          <td class="actions"><button class="btn btn-danger btn-sm" data-del="${method.id}">Delete</button></td></tr>`)
        .join('')
    : `<tr><td colspan="5" class="empty">No payment methods yet.</td></tr>`;
  shell('payments', `
    <div class="page-head"><h1>Payment methods</h1><p class="sub">Used to fund campaigns through the payment gateway.</p></div>
    <section class="workspace-panel"><form id="mf" class="inline-form">
      <div class="field"><label>Type</label>${select('kind', PAY_KINDS, 'card')}</div>
      <div class="field"><label>Label</label><input name="label" placeholder="HDFC ending 4321" required /></div>
      <button class="btn btn-primary" type="submit">Add method</button>
    </form></section>
    <section class="workspace-panel"><table class="tbl"><thead><tr><th>Gateway</th><th>Type</th><th>Label</th><th></th><th></th></tr></thead><tbody>${rows}</tbody></table></section>`);
  document.getElementById('mf').onsubmit = async (event) => {
    event.preventDefault();
    try { await API.post(`/api/brands/${brand.id}/payment-methods`, formData(event.target)); toast('Added', 'success'); brandPayments(); }
    catch (err) { toast(err.detail || 'Failed', 'error'); }
  };
  root.querySelectorAll('[data-del]').forEach((button) => {
    button.onclick = async () => {
      await API.del(`/api/payment-methods/${button.dataset.del}`);
      toast('Deleted', 'success');
      brandPayments();
    };
  });
}

// ----- Home dashboard helpers (reuse landing dashboard markup/classes) -----

const ACTIVITY_ICON = { earning: '₹', campaign: '↗', match: '↔', delivery: '✓' };

function creatorSuggestCard(creator) {
  return `<div class="creator-card">
    <div class="creator-avatar">${esc(creator.avatar || (creator.name || '?').slice(0, 2).toUpperCase())}</div>
    <div class="creator-info">
      <h4>${esc(creator.name)} ${creator.certified ? '<span class="license-badge">Certified</span>' : ''}</h4>
      <div class="handle">${esc(creator.handle || '')}${creator.city ? ' · ' + esc(creator.city) : ''}</div>
      <div class="creator-meta">
        <span>${esc(creator.niche || 'Creator')}</span>
        ${creator.followers ? `<span>${esc(creator.followers)} followers</span>` : ''}
        <span>from ${inr(creator.rate)}</span>
      </div>
    </div>
    <div class="match-score"><strong>${creator.matchScore || '—'}%</strong><span>match</span></div>
  </div>`;
}

function activityListItems(items) {
  if (!items.length) return '<li class="table-loading">No activity yet.</li>';
  return items
    .map((a) => `<li><span class="activity-icon ${a.type}">${ACTIVITY_ICON[a.type] || '•'}</span><div><strong>${esc(a.text)}</strong><span>${esc(a.meta)} · ${esc(a.time)}</span></div></li>`)
    .join('');
}
