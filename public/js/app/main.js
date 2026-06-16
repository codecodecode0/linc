import { API } from '../services/api.js';
import { clearSession, getSession, setSession } from '../services/session.js';
import { go, toast } from '../shared/dom.js';
import { renderLogin, renderSignup } from '../views/auth.js';
import { routeBrand } from '../views/brand.js';
import { routeCreator } from '../views/creator.js';

export async function boot() {
  const params = new URLSearchParams(location.search);
  if (params.get('token')) API.setToken(params.get('token'));
  if (params.get('connected')) toast(`${params.get('connected')} connected`, 'success');
  if (params.get('error')) toast(`Could not connect: ${params.get('error')}`, 'error');
  if (params.toString()) history.replaceState({}, '', location.pathname + location.hash);

  if (API.token()) {
    try {
      setSession(await API.get('/api/auth/me'));
    } catch {
      API.setToken(null);
      clearSession();
    }
  }
  render();
}

export function render() {
  const parts = location.hash.replace(/^#\/?/, '').split('/').filter(Boolean);
  const page = parts[0] || '';
  const session = getSession();

  if (!session) {
    if (page === 'signup') return renderSignup();
    return renderLogin();
  }

  const role = session.accountType;
  if (page !== role) return go(`#/${role}`);
  if (role === 'creator') return routeCreator(parts);
  return routeBrand(parts);
}

window.addEventListener('hashchange', render);

