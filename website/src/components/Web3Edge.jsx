import React from 'react';
import { LineChart, ArrowLeftRight, Flame, TrendingUp } from 'lucide-react';

export default function Web3Edge() {
  const list = [
    { icon: LineChart, title: 'The Whale Snapshot', prompt: "What's my crypto worth right now?", desc: 'Scans your entire wallet (USDC, SOL, Meme coins), pings live prices, and instantly calculates your exact fiat net worth.' },
    { icon: ArrowLeftRight, title: '1-Click DEX Execution', prompt: 'Swap 10 SOL for USDC.', desc: 'Pings Jupiter aggregators for live quotes and securely generates a 1-Click execution deep-link to route trades natively in your mobile wallet.' },
    { icon: Flame, title: 'Real-time Gas Burn', prompt: 'How much did I burn on gas?', desc: 'Hits Blockscout and Helius RPCs to sweep your recent on-chain transactions and compute exact capital lost to execution friction.' },
    { icon: TrendingUp, title: 'DeFi Yield Crawler', prompt: 'How much interest did I earn?', desc: 'Crawls Lido, RocketPool, and Jito smart contracts your wallet interacts with to output active staked balances and APY rewards.' }
  ];

  return (
    <section className="py-16 md:py-24 px-6 z-10 relative border-t border-white/5 bg-[#050505]">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight mb-4 text-[#a7dd5d]">The Web3 Edge</h2>
          <p className="text-neutral-400">Four ways Spenzo's MCP turns natural chat into a Bloomberg Terminal for crypto.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-8">
          {list.map((f, i) => (
            <div key={i} className="bg-[#0a0a0a] border border-white/5 p-8 rounded-xl hover:border-[#a7dd5d]/30 transition-all group">
              <div className="flex items-center gap-4 mb-6">
                <div className="p-3 bg-white/5 rounded-lg text-neutral-400 group-hover:bg-[#a7dd5d]/10 group-hover:text-[#a7dd5d] transition-colors">
                  <f.icon size={24} />
                </div>
                <h3 className="text-xl font-bold text-white">{f.title}</h3>
              </div>
              <div className="bg-[#111b21] p-3 rounded-lg border border-white/5 mb-6">
                <span className="text-xs font-mono text-neutral-500 uppercase tracking-widest block mb-1">User Asks:</span>
                <span className="text-sm text-[#a7dd5d]">"{f.prompt}"</span>
              </div>
              <p className="text-neutral-400 text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
