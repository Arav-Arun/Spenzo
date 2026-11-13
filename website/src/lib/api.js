import { API_URL } from '../brand';

const KEY = 'spenzo_session';
const store = {
  get: () => { try { return localStorage.getItem(KEY); } catch { return null; } },
  set: (v) => { try { localStorage.setItem(KEY, v); } catch { /* private mode: session lasts this tab only */ } },
  clear: () => { try { localStorage.removeItem(KEY); } catch { /* ignore */ } },
};

let memorySession = null;
export const session = () => memorySession || store.get();
export const signOut = () => { memorySession = null; store.clear(); };

async function call(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(session() ? { Authorization: `Bearer ${session()}` } : {}), ...options.headers },
  });
  if (res.status === 401) { signOut(); throw new Error((await res.json().catch(() => ({}))).detail || 'Please sign in again.'); }
  if (!res.ok) throw new Error(`Something went wrong (${res.status}). Try again in a moment.`);
  return res;
}

// Swap the one-time link token from WhatsApp for a 30-day session.
export async function signIn(token) {
  const data = await (await call('/api/session', { method: 'POST', body: JSON.stringify({ token }) })).json();
  memorySession = data.session;
  store.set(data.session);
  return data;
}

export const getOverview = async (month) => (await call(`/api/overview?month=${month}`)).json();
export const getPortfolio = async () => (await call('/api/portfolio')).json();
export const deleteTransaction = async (id) => (await call(`/api/transactions/${id}`, { method: 'DELETE' })).json();
export async function exportCsv() {
  const blob = await (await call('/api/export.csv')).blob();
  const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: 'spenzo.csv' });
  a.click();
  URL.revokeObjectURL(a.href);
}
