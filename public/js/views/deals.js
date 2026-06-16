import { API } from '../services/api.js';
import { CONTENT_TYPES } from '../shared/constants.js';
import { formData, toast } from '../shared/dom.js';
import { esc, inr, titleCase } from '../shared/format.js';
import { badge, select, shell } from '../components/ui.js';

const canCreatorAccept = (deal) => deal.status === 'offered' && deal.lastOfferBy === 'brand';
const canBrandAcceptCounter = (deal) => deal.status === 'countered' && deal.lastOfferBy === 'creator';

export async function dealAction(dealId, action, patch = {}) {
  return API.post(`/api/deals/${dealId}/actions`, { action, ...patch });
}

export async function dealDetail(dealId, role) {
  let deal;
  let content = [];
  try {
    deal = await API.get(`/api/deals/${dealId}`);
  } catch {
    location.hash = `#/${role}`;
    return;
  }
  try {
    content = await API.get(`/api/deals/${dealId}/content`);
  } catch {}

  const back = role === 'brand' ? `#/brand/campaigns/${deal.campaignId}` : '#/creator/deals';
  const brief = deal.brief || {};
  const deliverables = deal.deliverables || [];
  const deliverableList = deliverables.length
    ? deliverables
        .map(
          (d) => `<li><strong>${esc(d.quantity)}x ${esc(titleCase(d.type))}</strong>${d.title ? ` · ${esc(d.title)}` : ''}${d.notes ? `<span>${esc(d.notes)}</span>` : ''}</li>`,
        )
        .join('')
    : `<li><strong>${esc(titleCase(deal.type))}</strong><span>${esc(brief.deliverables || 'Creator content')}</span></li>`;

  const contentRows = content.length
    ? content
        .map(
          (item) => `<tr>
            <td>${esc(item.title)}</td>
            <td>${esc(titleCase(item.type))}</td>
            <td>${badge(item.status)}</td>
            <td>${item.assetUrl ? `<a href="${esc(item.assetUrl)}" target="_blank">View</a>` : '—'}</td>
            <td class="actions">
              ${
                role === 'brand'
                  ? `<button class="btn btn-soft btn-sm" data-cstatus="${item.id}" data-v="approved">Approve</button>
                     <button class="btn btn-soft btn-sm" data-cstatus="${item.id}" data-v="revisions_requested">Revise</button>`
                  : `<button class="btn btn-soft btn-sm" data-csubmit="${item.id}">Submit</button>`
              }
            </td></tr>`,
        )
        .join('')
    : `<tr><td colspan="5" class="empty">No assets have been added yet.</td></tr>`;

  shell(role === 'brand' ? 'campaigns' : 'deals', `
    <button class="back" onclick="location.hash='${back}'">&larr; Back</button>
    <div class="page-head"><div><h1>${esc(brief.campaign || 'Deal')}</h1>
      <p class="sub">${esc(titleCase(deal.type))} · ${badge(deal.status)} · ${inr(deal.quoteAmount)}</p></div></div>
    <section class="workspace-panel">
      <div class="panel-title"><div><h3>Offer summary</h3><p>${esc(brief.deliverables || 'Creator deliverables for this campaign.')}</p></div></div>
      <div class="deal-facts">
        <div><span>Objective</span><strong>${esc(titleCase(brief.objective || 'Campaign'))}</strong></div>
        <div><span>Category</span><strong>${esc(brief.productCategory || 'General')}</strong></div>
        <div><span>Quote</span><strong>${inr(deal.quoteAmount)}</strong></div>
      </div>
      <ul class="deliverable-list">${deliverableList}</ul>
      ${brief.audience ? `<p class="brief-box">${esc(brief.audience)}</p>` : ''}
      ${brief.brief ? `<p class="brief-box">${esc(brief.brief)}</p>` : ''}
      ${actionsFor(deal, role)}
    </section>
    <section class="workspace-panel">
      <div class="panel-title"><div><h3>Add asset</h3><p>Assets are the actual uploaded drafts against the agreed deliverables.</p></div></div>
      <form id="cf" class="inline-form">
        <div class="field"><label>Title</label><input name="title" placeholder="First draft video" required /></div>
        <div class="field"><label>Type</label>${select('type', CONTENT_TYPES, 'raw_video')}</div>
        <button class="btn btn-primary" type="submit">Add asset</button>
      </form>
    </section>
    <section class="workspace-panel">
      <div class="panel-title"><div><h3>Assets</h3><p>Review submitted files and request revisions without changing the deal scope.</p></div></div>
      <table class="tbl"><thead><tr><th>Title</th><th>Type</th><th>Status</th><th>Asset</th><th></th></tr></thead><tbody>${contentRows}</tbody></table>
    </section>`);

  wireDealActions(deal, role);
  document.getElementById('cf').onsubmit = async (event) => {
    event.preventDefault();
    try {
      await API.post(`/api/deals/${dealId}/content`, formData(event.target));
      toast('Asset added', 'success');
      dealDetail(dealId, role);
    } catch (err) {
      toast(err.detail || 'Failed', 'error');
    }
  };
  document.querySelectorAll('[data-cstatus]').forEach((button) => {
    button.onclick = async () => {
      await API.patch(`/api/content/${button.dataset.cstatus}`, { status: button.dataset.v });
      if (button.dataset.v === 'approved') await dealAction(dealId, 'approve_content').catch(() => {});
      if (button.dataset.v === 'revisions_requested') await dealAction(dealId, 'request_revisions').catch(() => {});
      dealDetail(dealId, role);
    };
  });
  document.querySelectorAll('[data-csubmit]').forEach((button) => {
    button.onclick = async () => {
      const url = prompt('Asset URL (link to your uploaded video/image):', 'https://');
      if (url === null) return;
      await API.patch(`/api/content/${button.dataset.csubmit}`, { status: 'submitted', assetUrl: url });
      await dealAction(dealId, 'submit_content').catch(() => {});
      dealDetail(dealId, role);
    };
  });
}

function actionsFor(deal, role) {
  if (role === 'creator') {
    if (canCreatorAccept(deal)) {
      return `<div class="deal-actions detail-actions">
        <button class="btn btn-primary" data-deal-action="accept">Accept offer</button>
        <button class="btn btn-danger" data-deal-action="reject">Reject</button>
      </div>
      <form class="counter-inline detail-counter" data-counter-form>
        <label>Counter price</label>
        <input name="quoteAmount" type="number" min="1" value="${Number(deal.quoteAmount || 0)}" />
        <button class="btn btn-soft" type="submit">Negotiate price</button>
      </form>`;
    }
    if (deal.status === 'countered' && deal.lastOfferBy === 'creator') {
      return `<p class="brief-box muted">Counter sent. Waiting for the brand to accept or revise the offer.</p>`;
    }
    return `<p class="brief-box muted">No action needed from you right now.</p>`;
  }

  if (canBrandAcceptCounter(deal)) {
    return `<div class="deal-actions detail-actions">
      <button class="btn btn-primary" data-deal-action="accept">Accept counter</button>
      <button class="btn btn-danger" data-deal-action="reject">Withdraw</button>
    </div>
    <form class="counter-inline detail-counter" data-revise-form>
      <label>Revised price</label>
      <input name="quoteAmount" type="number" min="1" value="${Number(deal.quoteAmount || 0)}" />
      <button class="btn btn-soft" type="submit">Revise offer</button>
    </form>`;
  }
  if (deal.status === 'offered') {
    return `<div class="deal-actions detail-actions">
      <button class="btn btn-danger" data-deal-action="withdraw">Withdraw</button>
    </div>
    <form class="counter-inline detail-counter" data-revise-form>
      <label>Revised price</label>
      <input name="quoteAmount" type="number" min="1" value="${Number(deal.quoteAmount || 0)}" />
      <button class="btn btn-soft" type="submit">Revise offer</button>
    </form>`;
  }
  if (deal.status === 'accepted') {
    return `<div class="deal-actions detail-actions"><button class="btn btn-primary" data-deal-action="mark_contracted">Mark contracted</button></div>`;
  }
  if (deal.status === 'contracted') {
    return `<div class="deal-actions detail-actions"><button class="btn btn-primary" data-deal-action="start_production">Move to production</button></div>`;
  }
  if (deal.status === 'approved') {
    return `<div class="deal-actions detail-actions"><button class="btn btn-primary" data-deal-action="complete">Complete deal</button></div>`;
  }
  return `<p class="brief-box muted">No brand action is available in the current state.</p>`;
}

function wireDealActions(deal, role) {
  document.querySelectorAll('[data-deal-action]').forEach((button) => {
    button.onclick = async () => {
      try {
        await dealAction(deal.id, button.dataset.dealAction);
        toast('Deal updated', 'success');
        dealDetail(deal.id, role);
      } catch (err) {
        toast(err.detail || 'Action not allowed', 'error');
      }
    };
  });
  const counterForm = document.querySelector('[data-counter-form]');
  if (counterForm) {
    counterForm.onsubmit = async (event) => {
      event.preventDefault();
      const data = formData(counterForm);
      const quote = Number(data.quoteAmount) || deal.quoteAmount;
      try {
        await dealAction(deal.id, 'negotiate', { quoteAmount: quote });
        toast('Counter offer sent', 'success');
        dealDetail(deal.id, role);
      } catch (err) {
        toast(err.detail || 'Action not allowed', 'error');
      }
    };
  }
  const reviseForm = document.querySelector('[data-revise-form]');
  if (reviseForm) {
    reviseForm.onsubmit = async (event) => {
      event.preventDefault();
      const data = formData(reviseForm);
      const quote = Number(data.quoteAmount) || deal.quoteAmount;
      try {
        await dealAction(deal.id, 'revise_offer', { quoteAmount: quote });
        toast('Offer revised', 'success');
        dealDetail(deal.id, role);
      } catch (err) {
        toast(err.detail || 'Action not allowed', 'error');
      }
    };
  }
}
