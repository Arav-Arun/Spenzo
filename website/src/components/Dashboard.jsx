import { useState } from 'react';
import { compactInr, dayLabel, inr } from '../lib/format';
import Mascot from './Mascot';

const TABS = ['Spend', 'Split', 'Save', 'Activity'];
const KIND_LABEL = { stock: 'Stocks', mutual_fund: 'Mutual funds', crypto_wallet: 'Crypto' };
const KIND_COLOR = { stock: 'bg-leaf', mutual_fund: 'bg-mango', crypto_wallet: 'bg-ink' };

const Card = ({ children, className = '' }) => <section className={`rounded-2xl border border-line bg-card p-5 ${className}`}>{children}</section>;
const Label = ({ children }) => <h3 className="mb-3 text-sm font-semibold text-muted">{children}</h3>;
const Empty = ({ children, pose = 'thinking' }) => (
  <div className="flex flex-col items-center gap-2 rounded-xl bg-paper px-4 py-5 text-center text-sm text-muted">
    <Mascot pose={pose} className="h-16 w-16" />
    <p>{children}</p>
  </div>
);

function Bar({ pct, tone = 'leaf' }) {
  const fill = { leaf: 'bg-leaf', mango: 'bg-mango', chilli: 'bg-chilli' }[tone];
  return (
    <div className="h-2.5 overflow-hidden rounded-full bg-leaf-soft" role="progressbar" aria-valuenow={Math.round(pct)} aria-valuemin={0} aria-valuemax={100}>
      <div className={`h-full rounded-full ${fill}`} style={{ width: `${Math.min(Math.max(pct, 2), 100)}%` }} />
    </div>
  );
}

function DailyChart({ daily }) {
  const max = Math.max(...daily.map((d) => d.spent), 1);
  const biggest = daily.reduce((a, b) => (b.spent > a.spent ? b : a), daily[0]);
  return (
    <div>
      <div className="flex h-32 items-end gap-[3px]" aria-label="Spending per day">
        {daily.map((d) => (
          <div key={d.date} title={`${dayLabel(d.date)}: ${inr(d.spent)}`}
            className={`flex-1 rounded-t-[3px] ${d === biggest && d.spent ? 'bg-mango' : d.spent ? 'bg-leaf' : 'bg-leaf-soft'}`}
            style={{ height: `${d.spent ? Math.max((d.spent / max) * 100, 4) : 3}%` }} />
        ))}
      </div>
      <div className="mt-2 flex justify-between text-xs text-muted tabular">
        <span>1</span><span>{Math.ceil(daily.length / 2)}</span><span>{daily.length}</span>
      </div>
      {biggest?.spent > 0 && <p className="mt-2 text-xs text-muted">Biggest day: {dayLabel(biggest.date)}, {inr(biggest.spent)}</p>}
    </div>
  );
}

function SpendTab({ data }) {
  const { summary, daily, budgets } = data;
  const budgetFor = Object.fromEntries(budgets.map((b) => [b.category, b]));
  const top = summary.by_category[0]?.total || 1;
  return (
    <div className="grid gap-4 lg:grid-cols-[1.3fr_1fr]">
      <Card>
        <Label>Every day this month</Label>
        <DailyChart daily={daily} />
      </Card>
      <Card>
        <Label>Where it went</Label>
        {summary.by_category.length ? (
          <ul className="space-y-3.5">
            {summary.by_category.map((c) => {
              const b = budgetFor[c.category];
              return (
                <li key={c.category}>
                  <div className="mb-1 flex justify-between text-sm"><span>{c.category}</span><span className="font-semibold tabular">{inr(c.total)}</span></div>
                  <Bar pct={b ? b.used_pct : (c.total / top) * 100} tone={b && b.used_pct >= 100 ? 'chilli' : b && b.used_pct >= 80 ? 'mango' : 'leaf'} />
                  {b && <p className="mt-1 text-xs text-muted">{b.used_pct}% of {inr(b.limit)} budget · {b.left > 0 ? `${inr(b.left)} left` : 'over budget'}</p>}
                </li>
              );
            })}
          </ul>
        ) : <Empty>Nothing logged this month yet.</Empty>}
      </Card>
    </div>
  );
}

function Person({ p, owesYou }) {
  return (
    <li className="flex items-start justify-between gap-3 py-3">
      <div className="min-w-0">
        <div className="font-semibold">{p.person}</div>
        <div className="truncate text-xs text-muted">{p.for.join(', ') || 'No note'} · since {dayLabel(p.since)}</div>
      </div>
      <div className={`shrink-0 font-semibold tabular ${owesYou ? 'text-leaf-deep' : 'text-chilli'}`}>{inr(p.net)}</div>
    </li>
  );
}

function SplitTab({ debts }) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <Label>Owe you · {inr(debts.total_owed_to_you)}</Label>
        {debts.they_owe_you.length ? <ul className="divide-y divide-line">{debts.they_owe_you.map((p) => <Person key={p.person} p={p} owesYou />)}</ul>
          : <Empty pose="celebrate">Nobody owes you anything.</Empty>}
        {debts.they_owe_you.length > 0 && <p className="mt-3 text-xs text-muted">Send your UPI ID on WhatsApp to get a tap-to-pay link for each person.</p>}
      </Card>
      <Card>
        <Label>You owe · {inr(debts.total_you_owe)}</Label>
        {debts.you_owe.length ? <ul className="divide-y divide-line">{debts.you_owe.map((p) => <Person key={p.person} p={p} />)}</ul>
          : <Empty pose="celebrate">You don't owe anyone.</Empty>}
      </Card>
    </div>
  );
}

function SaveTab({ goals, portfolio }) {
  const known = portfolio?.gain_on_holdings_with_known_cost;
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card>
        <Label>Goals</Label>
        {goals.length ? (
          <ul className="space-y-5">
            {goals.map((g) => (
              <li key={g.name}>
                <div className="mb-1 flex items-baseline justify-between gap-3">
                  <span className="font-semibold">{g.name}</span>
                  <span className="text-sm tabular text-muted">{inr(g.saved)} / {inr(g.target)}</span>
                </div>
                <Bar pct={g.pct} tone="mango" />
                <p className="mt-1 text-xs text-muted">
                  {g.pct}%{g.per_month_needed ? ` · ${inr(g.per_month_needed)} a month to make it` : ''}
                  {g.behind_by > 0 && <span className="ml-1 rounded-full bg-chilli-soft px-2 py-0.5 font-semibold text-chilli">{inr(g.behind_by)} behind</span>}
                </p>
              </li>
            ))}
          </ul>
        ) : <Empty pose="save">No goals yet. On WhatsApp, say something like "Goa trip 30k by March".</Empty>}
      </Card>
      <Card>
        <Label>Investments</Label>
        {!portfolio ? <Empty pose="nap">Loading prices…</Empty> : portfolio.holdings.length ? (
          <>
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <span className="font-display text-3xl font-extrabold tabular">{inr(Math.round(portfolio.value))}</span>
              {known && <span className={`text-sm font-semibold tabular ${known.gain >= 0 ? 'text-leaf-deep' : 'text-chilli'}`}>
                {known.gain >= 0 ? '+' : ''}{inr(known.gain)} ({known.gain_pct}%) on what you paid
              </span>}
            </div>
            <div className="my-4 flex h-2.5 overflow-hidden rounded-full">
              {Object.entries(portfolio.mix_pct).map(([k, v]) => <div key={k} className={KIND_COLOR[k]} style={{ width: `${v}%` }} title={`${KIND_LABEL[k]} ${v}%`} />)}
            </div>
            <div className="mb-3 flex flex-wrap gap-3 text-xs text-muted">
              {Object.entries(portfolio.mix_pct).map(([k, v]) => <span key={k} className="flex items-center gap-1.5"><i className={`h-2 w-2 rounded-full ${KIND_COLOR[k]}`} />{KIND_LABEL[k]} {v}%</span>)}
            </div>
            <ul className="divide-y divide-line text-sm">
              {portfolio.holdings.map((h) => (
                <li key={h.name} className="flex items-center justify-between gap-3 py-2.5">
                  <span className="min-w-0 truncate">{h.name}</span>
                  <span className="shrink-0 text-right tabular">
                    {inr(Math.round(h.value))}
                    {h.gain_pct !== undefined && <span className={`ml-2 text-xs ${h.gain_pct >= 0 ? 'text-leaf-deep' : 'text-chilli'}`}>{h.gain_pct >= 0 ? '+' : ''}{h.gain_pct}%</span>}
                  </span>
                </li>
              ))}
            </ul>
            {portfolio.facts.map((f) => <p key={f} className="mt-3 rounded-lg bg-mango-soft px-3 py-2 text-xs text-[#7A4D00]">{f}</p>)}
            <p className="mt-3 text-xs text-muted">Facts, not advice. {portfolio.note}</p>
          </>
        ) : <Empty pose="grow">No investments yet. Send a screenshot of your Groww or Zerodha holdings on WhatsApp.</Empty>}
      </Card>
    </div>
  );
}

function ActivityTab({ recent, onDelete }) {
  const [confirm, setConfirm] = useState(null);
  if (!recent.length) return <Card><Empty>Nothing this month yet.</Empty></Card>;
  return (
    <Card className="p-0">
      <ul className="divide-y divide-line">
        {recent.map((t) => (
          <li key={t.id} className="flex items-center gap-3 px-5 py-3">
            <div className="min-w-0 flex-1">
              <div className="truncate font-medium">{t.description || t.category}</div>
              <div className="truncate text-xs text-muted">{dayLabel(t.date)} · {t.category}{t.note ? ` · ${t.note}` : ''}</div>
            </div>
            <span className={`shrink-0 font-semibold tabular ${t.kind === 'income' ? 'text-leaf-deep' : ''}`}>{t.kind === 'income' ? '+' : ''}{inr(t.amount)}</span>
            {onDelete && (confirm === t.id ? (
              <span className="flex shrink-0 gap-1">
                <button onClick={() => { onDelete(t.id); setConfirm(null); }} className="rounded-md bg-chilli px-2.5 py-1 text-xs font-semibold text-white">Delete</button>
                <button onClick={() => setConfirm(null)} className="rounded-md px-2 py-1 text-xs text-muted hover:bg-paper">Keep</button>
              </span>
            ) : (
              <button aria-label={`Delete ${t.description || t.category}`} onClick={() => setConfirm(t.id)}
                className="shrink-0 rounded-md px-2 py-1 text-muted hover:bg-chilli-soft hover:text-chilli">✕</button>
            ))}
          </li>
        ))}
      </ul>
    </Card>
  );
}

export default function Dashboard({ data, portfolio, onDelete, initialTab = 'Spend' }) {
  const [tab, setTab] = useState(initialTab);
  const s = data.summary;
  const tiles = [
    { label: 'Spent', value: inr(s.spent), sub: `${s.count} expenses` },
    { label: 'Income', value: s.income ? inr(s.income) : '—', sub: s.income ? 'this month' : 'say "salary 60k"' },
    { label: 'Left', value: s.left !== null && s.left !== undefined ? inr(s.left) : '—', sub: s.income ? `${Math.max(0, Math.round((s.left / s.income) * 100))}% of income` : '' },
    { label: 'Friends owe you', value: compactInr(data.debts.total_owed_to_you), sub: data.debts.they_owe_you.length === 1 ? '1 person' : `${data.debts.they_owe_you.length} people` },
  ];
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {tiles.map((t) => (
          <div key={t.label} className="rounded-2xl border border-line bg-card px-4 py-3.5">
            <div className="text-xs font-semibold uppercase tracking-wide text-muted">{t.label}</div>
            <div className="mt-1 font-display text-2xl font-extrabold tabular">{t.value}</div>
            <div className="text-xs text-muted">{t.sub}</div>
          </div>
        ))}
      </div>
      <div role="tablist" className="flex gap-1 rounded-xl bg-leaf-soft p-1">
        {TABS.map((t) => (
          <button key={t} role="tab" aria-selected={tab === t} onClick={() => setTab(t)}
            className={`flex-1 rounded-lg px-3 py-2 text-sm font-semibold transition-colors ${tab === t ? 'bg-card text-ink shadow-sm' : 'text-leaf-deep hover:bg-white/60'}`}>
            {t}
          </button>
        ))}
      </div>
      {tab === 'Spend' && <SpendTab data={data} />}
      {tab === 'Split' && <SplitTab debts={data.debts} />}
      {tab === 'Save' && <SaveTab goals={data.goals} portfolio={portfolio} />}
      {tab === 'Activity' && <ActivityTab recent={data.recent} onDelete={onDelete} />}
    </div>
  );
}
