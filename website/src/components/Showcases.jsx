import React from 'react';
import { Bot, GlobeLock } from 'lucide-react';
import { WhatsAppIcon } from './Icons';

export default function Showcases() {
  return (
    <section className="bg-[#0a0a0a] border-t border-white/5 py-16 md:py-24 px-6 z-10 relative">
      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* WhatsApp Native */}
        <div className="bg-[#0c0c0c] border border-white/10 p-8 flex flex-col justify-between">
          <div className="mb-10">
            <div className="w-12 h-12 rounded bg-[#a7dd5d]/10 flex items-center justify-center text-[#a7dd5d] mb-6">
              <WhatsAppIcon size={24} />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">WhatsApp Native</h2>
            <p className="text-neutral-400 leading-relaxed">
              Text your expenses naturally. Spenzo categorizes them instantly. Snap a receipt to extract the merchant and total automatically.
            </p>
          </div>
          
          {/* WhatsApp Mockup */}
          <div className="bg-[#111b21] p-4 rounded-xl font-sans text-sm flex flex-col gap-3 h-48 justify-end border border-white/5 border-b-0 rounded-b-none">
             <div className="self-end bg-[#005c4b] text-white px-4 py-2.5 rounded-lg rounded-tr-none max-w-[80%] shadow-sm">
               Spent ₹150 on chai and samosa
             </div>
             <div className="self-start bg-[#202c33] text-white px-4 py-2.5 rounded-lg rounded-tl-none max-w-[80%] shadow-sm">
               ✅ ₹150 logged - Chai and Samosa / Food &amp; Dining
             </div>
          </div>
        </div>

        {/* Claude Desktop Integration */}
        <div className="bg-[#0c0c0c] border border-white/10 p-8 flex flex-col justify-between relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-[#a7dd5d]/5 blur-[50px] pointer-events-none" />
          <div className="mb-10">
            <div className="w-12 h-12 rounded bg-[#a7dd5d]/10 flex items-center justify-center text-[#a7dd5d] mb-6">
              <Bot size={24} />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Claude Desktop MCP</h2>
            <p className="text-neutral-400 leading-relaxed">
              Use Spenzo as a native tool inside Claude for hands-free financial management. Hook it directly into <code>claude_desktop_config.json</code>.
            </p>
          </div>
          
          <pre className="p-5 bg-[#000000] border border-white/10 rounded-xl rounded-b-none border-b-0 overflow-x-auto text-[12px] font-mono text-neutral-300 shadow-inner h-48 flex items-end pb-0">
{`"mcpServers": {
  "spenzo": {
    "command": "uv",
    "args": [
      "run", "fastmcp", "run",
      "/PATH/TO/Spenzo/server/main.py"
    ]
  }
}`}
          </pre>
        </div>

        {/* Web3 Portfolio Sync */}
        <div className="bg-[#0c0c0c] border border-white/10 p-8 flex flex-col justify-between relative overflow-hidden group">
          <div className="absolute bottom-0 left-0 w-32 h-32 bg-[#a7dd5d]/5 blur-[50px] pointer-events-none" />
          <div className="mb-10">
            <div className="w-12 h-12 rounded bg-[#a7dd5d]/10 flex items-center justify-center text-[#a7dd5d] mb-6">
              <GlobeLock size={24} />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Web3 Wallet Sync</h2>
            <p className="text-neutral-400 leading-relaxed text-sm">
              Connect your public Solana or Ethereum address directly in the chat. Spenzo's MCP pulls your token balances seamlessly.
            </p>
          </div>
          
          {/* Web3 Mockup */}
          <div className="bg-[#111b21] p-4 rounded-xl font-sans text-sm flex flex-col gap-3 h-48 justify-end border border-white/5 border-b-0 rounded-b-none">
             <div className="self-end bg-[#005c4b] text-white px-4 py-2.5 rounded-lg rounded-tr-none max-w-[80%] shadow-sm">
               Link my Solana wallet 7xK3...
             </div>
             <div className="self-start bg-[#202c33] text-white px-4 py-2.5 rounded-lg rounded-tl-none max-w-[90%] shadow-sm leading-relaxed">
               ✅ Synced! You hold 45.2 SOL ($8,136) in liquid assets.
             </div>
          </div>
        </div>

      </div>
    </section>
  );
}
