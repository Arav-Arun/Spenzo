import { useCallback, useEffect, useState } from 'react';
import { NAME, whatsappLink } from '../brand';
import Dashboard from '../components/Dashboard';
import { WhatsAppIcon } from '../components/Icons';
import Mascot from '../components/Mascot';
import { deleteTransaction, exportCsv, getOverview, getPortfolio, session, signIn, signOut } from '../lib/api';
import { monthLabel, shiftMonth } from '../lib/format';

const thisMonth = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`; };

function SignIn({ error }) {
  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-sm rounded-3xl border border-line bg-card p-8 text-center shadow-[0_20px_60px_rgba(14,42,31,0.08)]">
        <Mascot pose="wave" className="mx-auto mb-4 h-28 w-28" />
        <h1 className="mb-2 text-2xl font-extrabold">Open your dashboard</h1>
        <p className="mb-6 text-muted">{NAME} sends you a one-tap link on WhatsApp. No password needed.</p>
        {error && <p className="mb-4 rounded-lg bg-chilli-soft px-3 py-2 text-sm text-chilli">{error}</p>}
        <a href={whatsappLink('login')} target="_blank" rel="noreferrer"
          className="flex items-center justify-center gap-2 rounded-full bg-leaf-deep px-6 py-3.5 font-semibold text-white hover:bg-ink">
          <WhatsAppIcon size={18} /> Continue with WhatsApp
        </a>
        <p className="mt-4 text-xs text-muted">Send the message that opens, then tap <b>Open dashboard</b> in the reply.</p>
      </div>
    </main>
  );
}

export default function DashboardPage() {
  const [signedIn, setSignedIn] = useState(Boolean(session()));
  const [error, setError] = useState('');
  const [month, setMonth] = useState(thisMonth());
  const [data, setData] = useState(null);
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(false);

  // Arriving from WhatsApp: /app#t=<one-time token>
  useEffect(() => {
    const token = new URLSearchParams(window.location.hash.slice(1)).get('t');
    if (!token) return;
    window.history.replaceState(null, '', '/app');
    signIn(token).then(() => setSignedIn(true)).catch((e) => setError(e.message));
  }, []);

  const load = useCallback(async () => {
    if (!signedIn) return;
    setLoading(true);
    try {
      setData(await getOverview(month));
      setError('');
    } catch (e) {
      setError(e.message);
      if (!session()) setSignedIn(false);
    } finally {
      setLoading(false);
    }
  }, [signedIn, month]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => {
    if (signedIn) getPortfolio().then(setPortfolio).catch(() => setPortfolio({ holdings: [], facts: [], mix_pct: {} }));
  }, [signedIn]);

  if (!signedIn) return <SignIn error={error} />;

  const remove = async (id) => {
    await deleteTransaction(id);
    load();
  };
  const isCurrent = month >= thisMonth();

  return (
    <div className="min-h-screen pb-16 font-sans">
      <header className="border-b border-line bg-card">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6">
          <a href="/" className="flex items-center gap-2">
            <Mascot pose="icon" className="h-8 w-8" />
            <span className="font-display text-lg font-extrabold">{NAME}</span>
          </a>
          <div className="flex items-center gap-1 text-sm font-semibold">
            <button onClick={() => exportCsv().catch((e) => setError(e.message))}
              className="rounded-lg px-3 py-2 text-muted hover:bg-paper hover:text-ink">Export CSV</button>
            <button onClick={() => { signOut(); setSignedIn(false); }} className="rounded-lg px-3 py-2 text-muted hover:bg-paper hover:text-ink">Sign out</button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 pt-6 sm:px-6">
        {error && (
          <div className="mb-4 flex items-center gap-3 rounded-xl bg-chilli-soft px-4 py-2.5 text-sm text-chilli">
            <Mascot pose="worried" className="h-10 w-10 shrink-0" /> {error}
          </div>
        )}
        <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="text-sm text-muted">Hi {data?.name?.split(' ')[0] || 'there'} 👋</p>
            <h1 className="text-3xl font-extrabold">{monthLabel(month)}</h1>
          </div>
          <div className="flex items-center gap-1 rounded-full border border-line bg-card p-1">
            <button aria-label="Previous month" onClick={() => setMonth(shiftMonth(month, -1))} className="rounded-full px-3 py-1.5 hover:bg-paper">‹</button>
            <button onClick={() => setMonth(thisMonth())} className="px-2 text-sm font-semibold">This month</button>
            <button aria-label="Next month" disabled={isCurrent} onClick={() => setMonth(shiftMonth(month, 1))} className="rounded-full px-3 py-1.5 hover:bg-paper disabled:opacity-30">›</button>
          </div>
        </div>
        {data ? <div className={loading ? 'opacity-60 transition-opacity' : ''}><Dashboard data={data} portfolio={portfolio} onDelete={remove} /></div>
          : <div className="flex flex-col items-center gap-3 py-20 text-muted"><Mascot pose="nap" className="h-24 w-24" />Loading your month…</div>}
      </main>
    </div>
  );
}
