export const esc = (s) =>
  String(s ?? '').replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]),
  );

export const inr = (n) => `₹${Number(n || 0).toLocaleString('en-IN')}`;

export const titleCase = (s) =>
  String(s || '')
    .replace(/_/g, ' ')
    .replace(/\w\S*/g, (w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase());

export const compactNumber = (n) => {
  const value = Number(n || 0);
  if (value >= 10000000) return `${(value / 10000000).toFixed(1).replace(/\.0$/, '')}Cr`;
  if (value >= 100000) return `${(value / 100000).toFixed(1).replace(/\.0$/, '')}L`;
  if (value >= 1000) return `${Math.round(value / 1000)}K`;
  return value.toLocaleString('en-IN');
};

export const clamp = (n, min, max) => Math.max(min, Math.min(max, n));

