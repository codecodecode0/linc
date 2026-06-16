import { API } from '../services/api.js';
import { clearSession, getSession } from '../services/session.js';
import { go, root } from '../shared/dom.js';
import { STATUS_CLASS } from '../shared/constants.js';
import { esc, titleCase } from '../shared/format.js';

export function badge(status) {
  return `<span class="badge ${STATUS_CLASS[status] ?? ''}">${esc(titleCase(status))}</span>`;
}

export function select(name, options, current) {
  return `<select name="${name}">${options
    .map((option) => `<option value="${option}" ${option === current ? 'selected' : ''}>${esc(titleCase(option))}</option>`)
    .join('')}</select>`;
}

export function logoMark() {
  return `<a class="logo" href="index.html"><span class="logo-mark">l</span><span class="logo-text">linc</span></a>`;
}

export function shell(active, content) {
  const session = getSession();
  const role = session.accountType;
  const nav =
    role === 'creator'
      ? [
          ['', 'Home'],
          ['profile', 'Profile'],
          ['social', 'Social accounts'],
          ['licenses', 'Licensing'],
          ['payouts', 'Payouts'],
          ['deals', 'Deals'],
        ]
      : [
          ['', 'Home'],
          ['campaigns', 'Campaigns'],
          ['creators', 'Find creators'],
          ['payments', 'Payments'],
        ];
  root.innerHTML = `
    <div class="shell">
      <aside class="sidebar">
        <a class="logo" href="#/${role}"><span class="logo-mark">l</span><span class="logo-text">linc</span></a>
        ${nav
          .map(
            ([key, label]) =>
              `<a class="nav-link ${active === key ? 'active' : ''}" href="#/${role}${key ? '/' + key : ''}">${label}</a>`,
          )
          .join('')}
        <div class="sidebar-foot">
          <div class="who"><strong>${esc(session.account.name)}</strong><span>${role}</span></div>
          <button class="btn btn-soft btn-sm" id="logout">Log out</button>
        </div>
      </aside>
      <main class="main">${content}</main>
    </div>`;
  document.getElementById('logout').onclick = () => {
    API.setToken(null);
    clearSession();
    go('#/login');
  };
}

export const quickCard = (title, description, href) =>
  `<a class="card" href="${href}" style="text-decoration:none;color:inherit">
    <h3>${esc(title)}</h3><p class="sub">${esc(description)}</p>
  </a>`;
