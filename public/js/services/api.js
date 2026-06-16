const TOKEN_KEY = 'linc_token';

export const API = {
  token: () => localStorage.getItem(TOKEN_KEY),
  setToken(token) {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  },
  get: (path) => request('GET', path),
  post: (path, body) => request('POST', path, body),
  patch: (path, body) => request('PATCH', path, body),
  del: (path) => request('DELETE', path),
};

async function request(method, path, body) {
  const headers = { 'Content-Type': 'application/json' };
  const token = API.token();
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(path, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw { status: res.status, detail: (data && data.detail) || res.statusText };
  }
  return data;
}

