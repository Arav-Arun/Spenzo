// Data for the dashboard preview on the homepage.
const days = Array.from({ length: 30 }, (_, i) => {
  const d = `2026-11-${String(i + 1).padStart(2, '0')}`;
  const spent = i < 15 ? [420, 180, 2600, 350, 90, 760, 1200, 240, 310, 18000, 450, 120, 980, 560, 270][i] : 0;
  return { date: d, spent };
});

export const SAMPLE_OVERVIEW = {
  name: 'Arav',
  month: '2026-11',
  summary: {
    spent: 26530, income: 60000, left: 33470, count: 41,
    by_category: [
      { category: 'Bills & Rent', total: 18000 }, { category: 'Food & Dining', total: 4930 },
      { category: 'Shopping', total: 2600 }, { category: 'Transport', total: 1000 },
    ],
  },
  daily: days,
  budgets: [
    { category: 'Food & Dining', limit: 6000, spent: 4930, left: 1070, used_pct: 82, projected: 9860, days_left: 15 },
    { category: 'Shopping', limit: 5000, spent: 2600, left: 2400, used_pct: 52, projected: 5200, days_left: 15 },
  ],
  goals: [
    { name: 'Goa trip', target: 30000, saved: 12000, pct: 40, left: 18000, deadline: '2027-03-31', per_month_needed: 4500, behind_by: 0 },
    { name: 'New laptop', target: 80000, saved: 15000, pct: 19, left: 65000, deadline: '2027-08-31', per_month_needed: 7222, behind_by: 2500 },
  ],
  debts: {
    they_owe_you: [
      { person: 'Kabir', net: 1200, for: ['concert tickets'], since: '2026-10-28' },
      { person: 'Riya', net: 1000, for: ['dinner'], since: '2026-11-12' },
    ],
    you_owe: [{ person: 'Arjun', net: 300, for: ['cab'], since: '2026-11-14' }],
    total_owed_to_you: 2200, total_you_owe: 300,
  },
  recent: [
    { id: 1, date: '2026-11-15', kind: 'expense', amount: 270, category: 'Food & Dining', description: 'Swiggy', note: '', tags: ['swiggy'] },
    { id: 2, date: '2026-11-14', kind: 'expense', amount: 560, category: 'Transport', description: 'Uber to airport', note: '', tags: [] },
    { id: 3, date: '2026-11-13', kind: 'expense', amount: 980, category: 'Food & Dining', description: 'Dinner', note: 'Total 2,940 split 3 ways', tags: ['riya', 'arav'] },
    { id: 4, date: '2026-11-12', kind: 'expense', amount: 120, category: 'Food & Dining', description: 'Chai and samosa', note: '', tags: [] },
    { id: 5, date: '2026-11-10', kind: 'expense', amount: 18000, category: 'Bills & Rent', description: 'Rent', note: '', tags: [] },
    { id: 6, date: '2026-11-01', kind: 'income', amount: 60000, category: 'Salary', description: 'Salary', note: '', tags: [] },
  ],
};

export const SAMPLE_PORTFOLIO = {
  value: 44380,
  gain_on_holdings_with_known_cost: { holdings: ['Tata Consultancy Services', 'Parag Parikh Flexi Cap'], invested: 42000, now_worth: 44380, gain: 2380, gain_pct: 5.7 },
  mix_pct: { stock: 54, mutual_fund: 46 },
  holdings: [
    { name: 'Tata Consultancy Services', kind: 'stock', value: 24000, share_pct: 54, gain_pct: 4.9, today_pct: 1.2 },
    { name: 'Parag Parikh Flexi Cap Fund - Direct Plan - Growth', kind: 'mutual_fund', value: 20380, share_pct: 46, gain_pct: 6.4 },
  ],
  facts: ['Tata Consultancy Services is 54% of the portfolio.'],
  note: 'Prices can be up to 15 minutes old. Mutual fund values use the latest published NAV.',
};
