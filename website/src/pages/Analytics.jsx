import React, { useEffect, useState, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { ArrowLeft, ArrowRight, Loader2, AlertCircle, TrendingUp, Calendar, Hash, ArrowUpRight, Plus, GlobeLock, Bitcoin } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || "https://spenzo-xhgy.onrender.com";
const COLORS = ['#a7dd5d', '#c8ed8c', '#e0f4b5', '#748c3a', '#4a5a24', '#2e3a15', '#f0ffcc'];

export default function Analytics() {
  const [searchParams] = useSearchParams();
  const phone = searchParams.get('phone');
  const navigate = useNavigate();

  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Removed exact navigation to allow rendering the login form below
  useEffect(() => {
    if (!phone) return;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout

    const fetchExpenses = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API}/analytics/expenses?phone=${encodeURIComponent(phone)}`, {
          signal: controller.signal
        });
        if (!res.ok) throw new Error(`HTTP Error ${res.status}`);
        const json = await res.json();
        
        if (!json || json.length === 0) {
          setError('No expenses found for this number. Check if you have linked it on WhatsApp!');
        } else {
          setExpenses(json);
        }
      } catch (err) {
        if (err.name === 'AbortError') {
          setError('Request timed out. The Spenzo server might be waking up or your connection is slow. Please refresh in 10 seconds.');
        } else {
          setError(`Failed to sync: ${err.message}. Please check your internet or refresh.`);
        }
      } finally {
        setLoading(false);
        clearTimeout(timeoutId);
      }
    };

    fetchExpenses();
    return () => controller.abort();
  }, [phone, navigate]);

  // Derive metrics
  const stats = useMemo(() => {
    if (!expenses.length) return null;

    const now = new Date();
    let totalAll = 0;
    let totalMonth = 0;
    let totalWeek = 0;

    const catSums = {};
    const dailySums = {};

    expenses.forEach(e => {
      const amt = parseFloat(e.amount) || 0;
      totalAll += amt;

      const d = new Date(e.date);
      // Month
      if (d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()) {
        totalMonth += amt;
      }
      // Week
      const diffTime = Math.abs(now - d);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      if (diffDays <= 7) {
        totalWeek += amt;
      }

      // Categories
      const cat = e.category || 'Other';
      catSums[cat] = (catSums[cat] || 0) + amt;

      // Daily (Last 30 days)
      if (diffDays <= 30) {
        const dateStr = d.toISOString().split('T')[0];
        dailySums[dateStr] = (dailySums[dateStr] || 0) + amt;
      }
    });

    // Top Category
    const topCat = Object.keys(catSums).sort((a,b) => catSums[b] - catSums[a])[0];

    // Format Donut Data
    const donutData = Object.keys(catSums).map(k => ({ name: k, value: catSums[k] })).sort((a,b) => b.value - a.value);

    // Format Line Data (Last 30 days chronological)
    const lineData = [];
    const _30daysAgo = new Date();
    _30daysAgo.setDate(now.getDate() - 29);

    for (let i = 0; i < 30; i++) {
      const iter = new Date(_30daysAgo);
      iter.setDate(_30daysAgo.getDate() + i);
      const dStr = iter.toISOString().split('T')[0];
      const displayStr = iter.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      lineData.push({
        date: displayStr,
        amount: dailySums[dStr] || 0
      });
    }

    return {
      totalAll, totalMonth, totalWeek, txCount: expenses.length, topCat, donutData, lineData
    };
  }, [expenses]);

  const formatCurrency = (val) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(val);

  if (!phone) {
    return (
      <div className="min-h-screen bg-black text-[#f0f0f0] flex flex-col font-sans selection:bg-[#a7dd5d] selection:text-black">
        <header className="h-16 border-b border-white/10 flex items-center px-6 lg:px-10">
          <button onClick={() => navigate('/')} className="flex items-center gap-2 text-neutral-400 hover:text-white transition-colors">
            <ArrowLeft size={16} /> <span className="text-sm font-semibold tracking-wide uppercase">Back</span>
          </button>
        </header>
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-[#0c0c0c] border border-white/10 p-8 shadow-2xl">
            <h2 className="text-2xl font-bold mb-2">Access Dashboard</h2>
            <p className="text-neutral-500 mb-8 text-sm">Enter your registered WhatsApp number to view your real-time analytics.</p>
            <form onSubmit={(e) => {
               e.preventDefault();
               const val = e.target.phone.value;
               const cleanPhone = val.replace(/[^0-9+]/g, '');
               navigate(`/analytics?phone=${encodeURIComponent(cleanPhone)}`);
            }} className="flex flex-col gap-4">
              <input name="phone" type="tel" placeholder="+91 98765 43210" required className="bg-black border border-white/10 text-white font-mono text-sm px-4 py-3 outline-none focus:border-[#a7dd5d]/50 transition-colors" />
              <button type="submit" className="bg-[#a7dd5d] text-black font-bold uppercase tracking-wider text-sm px-6 py-3 hover:bg-[#bbf06a] transition-all flex justify-center items-center gap-2">
                Launch Analytics <ArrowRight size={16} />
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-black text-[#f0f0f0]">
        <Loader2 className="animate-spin text-[#a7dd5d] mb-4" size={40} />
        <p className="font-mono text-xs uppercase tracking-widest text-neutral-500">Syncing with Spenzo</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-black text-[#f0f0f0] px-6 text-center">
        <AlertCircle className="text-red-500 mb-4" size={48} />
        <h2 className="text-2xl font-semibold mb-2">Something went wrong</h2>
        <p className="text-neutral-400 mb-8 font-mono text-sm max-w-md">{error}</p>
        <button onClick={() => navigate('/')} className="flex items-center gap-2 text-[#a7dd5d] hover:text-white transition-colors font-semibold uppercase text-sm tracking-wide">
          <ArrowLeft size={16} /> Return Home
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-[#f0f0f0] font-sans pb-20 selection:bg-[#a7dd5d] selection:text-black">
      {/* Header */}
      <header className="h-16 border-b border-white/10 flex items-center justify-between px-6 lg:px-10 sticky top-0 bg-black/80 backdrop-blur-md z-20">
        <div className="flex items-center gap-6">
          <button onClick={() => navigate('/')} className="text-neutral-400 hover:text-white transition-colors">
            <ArrowLeft size={20} />
          </button>
          <div className="flex items-center gap-3">
             <img src="/spenzo-logo.png" alt="Spenzo Logo" className="h-6 w-auto" />
             <span className="font-semibold text-sm hidden sm:block">Spenzo Analytics</span>
          </div>
        </div>
        <div className="font-mono text-xs text-[#a7dd5d] flex items-center gap-2 bg-[#a7dd5d]/10 px-3 py-1.5 rounded border border-[#a7dd5d]/20">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#a7dd5d] opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[#a7dd5d]"></span>
          </span>
          {phone}
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 mt-10">
        <div className="mb-10 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2">Dashboard Overview</h1>
            <p className="text-neutral-500 text-sm">Your aggregated personal financial data, updated in real-time.</p>
          </div>
        </div>

        {/* Top Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-[#0c0c0c] border border-white/5 p-6 relative overflow-hidden group hover:border-[#a7dd5d]/30 transition-colors">
            <div className="absolute top-0 left-0 w-1 h-full bg-neutral-800 group-hover:bg-[#a7dd5d] transition-colors" />
            <div className="flex justify-between items-start mb-4">
              <span className="font-mono text-xs text-neutral-500 uppercase tracking-widest">All Time</span>
              <TrendingUp className="text-neutral-600 group-hover:text-[#a7dd5d] transition-colors" size={16} />
            </div>
            <div className="text-3xl font-bold">{formatCurrency(stats.totalAll)}</div>
          </div>
          
          <div className="bg-[#0c0c0c] border border-white/5 p-6 relative overflow-hidden group hover:border-[#a7dd5d]/30 transition-colors">
            <div className="absolute top-0 left-0 w-1 h-full bg-neutral-800 group-hover:bg-[#a7dd5d] transition-colors" />
            <div className="flex justify-between items-start mb-4">
              <span className="font-mono text-xs text-neutral-500 uppercase tracking-widest">This Month</span>
              <Calendar className="text-neutral-600 group-hover:text-[#a7dd5d] transition-colors" size={16} />
            </div>
            <div className="text-3xl font-bold">{formatCurrency(stats.totalMonth)}</div>
          </div>

          <div className="bg-[#0c0c0c] border border-white/5 p-6 relative overflow-hidden group hover:border-[#a7dd5d]/30 transition-colors">
            <div className="absolute top-0 left-0 w-1 h-full bg-neutral-800 group-hover:bg-[#a7dd5d] transition-colors" />
            <div className="flex justify-between items-start mb-4">
              <span className="font-mono text-xs text-neutral-500 uppercase tracking-widest">This Week</span>
              <Calendar className="text-neutral-600 group-hover:text-[#a7dd5d] transition-colors" size={16} />
            </div>
            <div className="text-3xl font-bold">{formatCurrency(stats.totalWeek)}</div>
          </div>

          <div className="bg-[#0c0c0c] border border-white/5 p-6 relative overflow-hidden group hover:border-[#a7dd5d]/30 transition-colors">
            <div className="absolute top-0 left-0 w-1 h-full bg-neutral-800 group-hover:bg-[#a7dd5d] transition-colors" />
            <div className="flex justify-between items-start mb-4">
              <span className="font-mono text-xs text-neutral-500 uppercase tracking-widest">Transactions</span>
              <Hash className="text-neutral-600 group-hover:text-[#a7dd5d] transition-colors" size={16} />
            </div>
            <div className="text-3xl font-bold">{stats.txCount}</div>
            <div className="text-xs text-[#a7dd5d] mt-2 font-medium">Top: {stats.topCat}</div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
          {/* Donut Chart */}
          <div className="lg:col-span-1 bg-[#0c0c0c] border border-white/5 p-6 flex flex-col">
            <h3 className="font-mono text-xs text-neutral-500 uppercase tracking-widest mb-6 border-b border-white/5 pb-4">Spend By Category</h3>
            <div className="flex-1 min-h-[250px] relative">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={stats.donutData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={85}
                    paddingAngle={2}
                    dataKey="value"
                    stroke="none"
                  >
                    {stats.donutData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip 
                    formatter={(value) => formatCurrency(value)}
                    contentStyle={{ backgroundColor: '#141414', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '4px', color: '#fff' }}
                    itemStyle={{ color: '#a7dd5d' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center pointer-events-none">
                <span className="block text-2xl font-bold text-white">{stats.donutData.length}</span>
                <span className="block text-[10px] uppercase tracking-widest text-[#a7dd5d] font-mono">Categories</span>
              </div>
            </div>
          </div>

          {/* Line Chart */}
          <div className="lg:col-span-2 bg-[#0c0c0c] border border-white/5 p-6 flex flex-col">
            <h3 className="font-mono text-xs text-neutral-500 uppercase tracking-widest mb-6 border-b border-white/5 pb-4">Daily Spend (Last 30 Days)</h3>
            <div className="flex-1 min-h-[250px]">
               <ResponsiveContainer width="100%" height="100%">
                <LineChart data={stats.lineData} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                  <XAxis 
                    dataKey="date" 
                    stroke="#444" 
                    fontSize={10} 
                    tickLine={false} 
                    axisLine={false} 
                    tickMargin={10}
                    minTickGap={30}
                  />
                  <YAxis 
                    stroke="#444" 
                    fontSize={10} 
                    tickLine={false} 
                    axisLine={false} 
                    tickFormatter={(val) => `₹${val}`}
                  />
                  <RechartsTooltip 
                    formatter={(value) => [formatCurrency(value), "Spent"]}
                    contentStyle={{ backgroundColor: '#141414', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '4px', color: '#fff' }}
                    labelStyle={{ color: '#888', marginBottom: '4px' }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="amount" 
                    stroke="#a7dd5d" 
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4, fill: '#000', stroke: '#a7dd5d', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Transactions Table */}
        <div className="bg-[#0c0c0c] border border-white/5 overflow-hidden">
          <div className="p-6 border-b border-white/5 flex items-center justify-between">
            <h3 className="font-mono text-xs text-neutral-500 uppercase tracking-widest">Recent Transactions</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/5 bg-[#0a0a0a]">
                  <th className="py-4 px-6 font-mono text-xs uppercase tracking-widest text-neutral-500 font-normal">Date</th>
                  <th className="py-4 px-6 font-mono text-xs uppercase tracking-widest text-neutral-500 font-normal">Description</th>
                  <th className="py-4 px-6 font-mono text-xs uppercase tracking-widest text-neutral-500 font-normal">Category</th>
                  <th className="py-4 px-6 font-mono text-xs uppercase tracking-widest text-neutral-500 font-normal text-right">Amount</th>
                </tr>
              </thead>
              <tbody>
                {expenses.map(tx => (
                  <tr key={tx.id} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors group">
                    <td className="py-4 px-6 text-sm text-neutral-400 font-mono">
                      {new Date(tx.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                    </td>
                    <td className="py-4 px-6 text-sm">
                      <div className="font-medium text-neutral-200">{tx.subcategory || tx.category}</div>
                      {tx.note && <div className="text-xs text-neutral-500 mt-1 line-clamp-1">{tx.note}</div>}
                    </td>
                    <td className="py-4 px-6 text-sm">
                      <span className="inline-flex items-center px-2 py-1 rounded bg-[#a7dd5d]/10 text-[#a7dd5d] border border-[#a7dd5d]/20 text-xs font-mono">
                        {tx.category}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-sm font-bold text-[#a7dd5d] text-right font-mono">
                      {formatCurrency(tx.amount)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </main>
    </div>
  );
}
