// Tiny API client for the linc app. Talks to the same-origin FastAPI backend,
// attaches the session bearer token, and normalizes errors.
const API = (() => {
  const TOKEN_KEY = 'linc_token';

  const token = () => localStorage.getItem(TOKEN_KEY);
  const setToken = (t) =>
    t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY);

  async function req(method, path, body) {
    const headers = { 'Content-Type': 'application/json' };
    const t = token();
    if (t) headers.Authorization = `Bearer ${t}`;
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

  return {
    token,
    setToken,
    get: (p) => req('GET', p),
    post: (p, b) => req('POST', p, b),
    patch: (p, b) => req('PATCH', p, b),
    del: (p) => req('DELETE', p),
  };
})();
