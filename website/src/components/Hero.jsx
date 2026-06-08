import React from 'react';
import { ArrowRight } from 'lucide-react';
import { WhatsAppIcon } from './Icons';

export default function Hero() {
  return (
    <main className="flex flex-col items-center text-center px-4 md:px-6 pt-28 pb-16 md:pt-36 md:pb-32 relative overflow-hidden mt-16 sm:mt-0 border-b border-white/5">
      
      {/* Animated Glows */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-[#a7dd5d]/15 blur-[120px] rounded-full pointer-events-none animate-pulse" style={{ animationDuration: '4s' }} />
      <div className="absolute bottom-0 left-1/4 w-[400px] h-[300px] bg-[#3ECF8E]/10 blur-[100px] rounded-full pointer-events-none" />
      
      {/* Tech Grid Texture */}
      <div className="absolute inset-0 z-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: 'linear-gradient(to right, #fff 1px, transparent 1px), linear-gradient(to bottom, #fff 1px, transparent 1px)', backgroundSize: '50px 50px' }} />
      <div className="absolute inset-0 z-0 bg-[radial-gradient(circle_at_center,transparent_20%,#000_100%)] pointer-events-none" />

      <div className="max-w-4xl z-10 flex flex-col items-center relative mt-8">

        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tighter leading-[1.05] mb-6 drop-shadow-2xl">
          The Ultimate Financial <br className="hidden md:block"/> 
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#a7dd5d] to-[#4ade80] inline-block mt-2">Superpower.</span>
        </h1>
        
        <p className="text-lg md:text-xl text-neutral-400 max-w-2xl mb-12 leading-relaxed font-light">
          An MCP financial tool for <strong className="text-white font-semibold">Claude Desktop</strong> and <strong className="text-white font-semibold">WhatsApp</strong>. Log expenses in natural language, track live crypto, analyze Web3 wallets, split bills, and send 1-click UPI links.
        </p>

        <div className="flex flex-col sm:flex-row w-full justify-center gap-4 mb-16">
          <a 
            href="https://wa.me/14155238886" 
            target="_blank" rel="noreferrer"
            className="bg-gradient-to-r from-[#a7dd5d] to-[#bbf06a] text-black font-bold uppercase tracking-wider text-sm px-8 py-4 shadow-[0_0_20px_rgba(167,221,93,0.2)] hover:shadow-[0_0_40px_rgba(167,221,93,0.4)] hover:scale-[1.03] duration-300 transition-all flex items-center justify-center gap-2 rounded-md"
          >
            <WhatsAppIcon size={18} /> Try on WhatsApp <ArrowRight size={16} />
          </a>
          <a 
            href="https://github.com/Arav-Arun/Spenzo" 
            target="_blank" rel="noreferrer"
            className="border border-white/10 bg-white/5 text-white font-bold uppercase tracking-wider text-sm px-8 py-4 hover:bg-white/10 hover:border-white/30 hover:shadow-xl hover:scale-[1.03] duration-300 transition-all flex items-center justify-center gap-2 rounded-md backdrop-blur-md"
          >
            View on GitHub
          </a>
        </div>
      </div>
    </main>
  );
}
