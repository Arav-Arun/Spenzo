// ₹1,23,456 with Indian grouping; paise only when there are any.
export const inr = (n) => `${n < 0 ? '-' : ''}₹${Math.abs(n).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
export const compactInr = (n) => (Math.abs(n) >= 100000 ? `₹${(n / 100000).toFixed(1).replace(/\.0$/, '')}L`
  : Math.abs(n) >= 1000 ? `₹${(n / 1000).toFixed(1).replace(/\.0$/, '')}k` : inr(n));
export const monthLabel = (ym) => new Date(`${ym}-01T00:00:00`).toLocaleDateString('en-IN', { month: 'long', year: 'numeric' });
export const dayLabel = (iso) => new Date(`${iso}T00:00:00`).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' });
export const shiftMonth = (ym, by) => {
  const d = new Date(`${ym}-01T00:00:00`);
  d.setMonth(d.getMonth() + by);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
};
