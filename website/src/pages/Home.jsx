import React, { useState, useCallback, useEffect } from 'react';
import { ArrowRight, Terminal, MessageCircle, Bot, Zap, Image, DollarSign, Bitcoin, LayoutDashboard, GlobeLock, Database, Brain, Palette, Code2, LineChart, Gem, FileText, ArrowLeftRight, TrendingUp, Flame, QrCode, Users, Search, Edit3, Download } from 'lucide-react';
import { Link } from 'react-router-dom';

const CLAUDE_IMGS = Array.from({ length: 13 }, (_, i) => `/screenshots/img${i + 1}.png`);
const WHATSAPP_IMGS = [
  "/screenshots/IMG_0712.PNG",
  "/screenshots/IMG_0713.PNG",
  "/screenshots/IMG_0721.PNG",
  "/screenshots/IMG_0722.PNG",
  "/screenshots/IMG_0723.PNG",
  "/screenshots/IMG_0724.PNG",
  "/screenshots/IMG_0725.PNG"
];

function ScreenshotGallery({ title, subtitle, images }) {
  const [index, setIndex] = useState(0);
  const [lightbox, setLightbox] = useState(null);

  const prev = useCallback(() => setIndex((i) => (i - 1 + images.length) % images.length), [images.length]);
  const next = useCallback(() => setIndex((i) => (i + 1) % images.length), [images.length]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (lightbox !== null) {
        if (e.key === 'Escape') setLightbox(null);
        if (e.key === 'ArrowRight') setLightbox(p => (p + 1) % images.length);
        if (e.key === 'ArrowLeft') setLightbox(p => (p - 1 + images.length) % images.length);
      } else {
        if (e.key === 'ArrowRight') next();
        if (e.key === 'ArrowLeft') prev();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [next, prev, lightbox, images.length]);

  return (
    <section className="py-16 md:py-24 px-4 md:px-6 z-10 relative border-t border-white/5 bg-black overflow-hidden">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-[1000px] h-[300px] bg-[#a7dd5d]/5 blur-[120px] pointer-events-none" />
      <div className="max-w-7xl mx-auto text-center mb-10 md:mb-16 relative z-10">
        <h2 className="text-2xl md:text-3xl font-bold tracking-tight mb-3 md:mb-4 text-white">{title}</h2>
        <p className="text-neutral-400 max-w-2xl mx-auto text-sm md:text-base">{subtitle}</p>
      </div>

      <div 
        className="relative w-full max-w-4xl mx-auto h-[50vh] sm:h-[60vh] min-h-[350px] flex items-center justify-center"
        style={{ perspective: '1200px' }}
      >
        {images.map((img, i) => {
          let offset = i - index;
          if (offset < -images.length / 2) offset += images.length;
          if (offset > images.length / 2) offset -= images.length;
          
          let style = {};
          if (offset === 0) {
            style = { transform: 'translateX(0) scale(1) rotateY(0deg)', zIndex: 30, opacity: 1 };
          } else if (offset === 1) {
            style = { transform: 'translateX(25%) scale(0.85) rotateY(-15deg)', zIndex: 20, opacity: 0.6 };
          } else if (offset === -1) {
            style = { transform: 'translateX(-25%) scale(0.85) rotateY(15deg)', zIndex: 20, opacity: 0.6 };
          } else if (offset === 2) {
            style = { transform: 'translateX(45%) scale(0.7) rotateY(-25deg)', zIndex: 10, opacity: 0.3 };
          } else if (offset === -2) {
            style = { transform: 'translateX(-45%) scale(0.7) rotateY(25deg)', zIndex: 10, opacity: 0.3 };
          } else {
            style = { transform: 'translateX(0) scale(0.5)', zIndex: 0, opacity: 0, pointerEvents: 'none' };
          }

          return (
            <div 
              key={i} 
              className="absolute w-[65%] sm:w-[50%] h-full flex items-center justify-center cursor-pointer transition-all duration-[600ms] ease-[cubic-bezier(0.25,1,0.5,1)]"
              style={style}
              onClick={() => {
                if (offset > 0) next();
                else if (offset < 0) prev();
                else setLightbox(i);
              }}
            >
              <img src={img} className="max-h-full max-w-full rounded-2xl border border-white/10 shadow-[0_20px_50px_rgba(0,0,0,0.5)] object-contain bg-[#050505]" alt="Screenshot" loading="lazy" />
            </div>
          )
        })}

        <button onClick={prev} className="absolute left-2 sm:-left-8 z-40 w-12 h-12 bg-white/5 border border-white/10 rounded-full flex items-center justify-center text-white hover:bg-[#a7dd5d] hover:text-black transition-colors backdrop-blur-md shadow-lg"><span className="text-xl font-bold -ml-1">‹</span></button>
        <button onClick={next} className="absolute right-2 sm:-right-8 z-40 w-12 h-12 bg-white/5 border border-white/10 rounded-full flex items-center justify-center text-white hover:bg-[#a7dd5d] hover:text-black transition-colors backdrop-blur-md shadow-lg"><span className="text-xl font-bold -mr-1">›</span></button>
      </div>

      <div className="text-center mt-8 text-xs font-mono text-neutral-500 uppercase tracking-widest relative z-10">
        {index + 1} / {images.length} · Tap lateral cards to rotate · Tap center to expand
      </div>

      {lightbox !== null && (
        <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-sm flex items-center justify-center p-2 md:p-4" onClick={() => setLightbox(null)}>
          <button className="absolute top-4 right-4 md:top-8 md:right-8 w-10 h-10 md:w-12 md:h-12 bg-white/10 border border-white/10 rounded-full flex items-center justify-center text-white hover:bg-white/30 transition-colors z-[110] text-xl font-light focus:outline-none" onClick={() => setLightbox(null)}>✕</button>
          <button onClick={e => { e.stopPropagation(); setLightbox(p => (p - 1 + images.length) % images.length); }} className="absolute left-2 md:left-4 top-1/2 -translate-y-1/2 w-10 h-10 md:w-12 md:h-12 rounded-full bg-white/15 hover:bg-[#a7dd5d] hover:text-black transition-colors text-2xl font-bold z-[110] focus:outline-none">‹</button>
          <img src={images[lightbox]} alt="Expanded" className="max-h-[88vh] max-w-[88vw] md:max-h-[90vh] md:max-w-[90vw] rounded-xl shadow-2xl border border-white/10 object-contain" onClick={e => e.stopPropagation()} />
          <button onClick={e => { e.stopPropagation(); setLightbox(p => (p + 1) % images.length); }} className="absolute right-2 md:right-4 top-1/2 -translate-y-1/2 w-10 h-10 md:w-12 md:h-12 rounded-full bg-white/15 hover:bg-[#a7dd5d] hover:text-black transition-colors text-2xl font-bold z-[110] focus:outline-none">›</button>
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-xs font-mono text-neutral-400 uppercase tracking-widest">{lightbox + 1} / {images.length}</div>
        </div>
      )}
    </section>
  );
}

function MasonryGallery({ title, subtitle, images, columnsClass = "columns-1 sm:columns-2 lg:columns-3" }) {
  const [lightbox, setLightbox] = useState(null);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (lightbox === null) return;
      if (e.key === 'Escape') setLightbox(null);
      if (e.key === 'ArrowRight') setLightbox(p => (p + 1) % images.length);
      if (e.key === 'ArrowLeft') setLightbox(p => (p - 1 + images.length) % images.length);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [lightbox, images.length]);

  return (
    <section className="py-16 md:py-24 px-4 md:px-6 z-10 relative border-t border-white/5 bg-black">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-[1000px] h-[300px] bg-[#a7dd5d]/5 blur-[120px] pointer-events-none" />
      <div className="max-w-7xl mx-auto relative z-10">
        <div className="text-center mb-10 md:mb-16">
          <h2 className="text-2xl md:text-3xl font-bold tracking-tight mb-3 md:mb-4 text-white">{title}</h2>
          <p className="text-neutral-400 max-w-2xl mx-auto text-sm md:text-base">{subtitle}</p>
        </div>
        <div className={`${columnsClass} gap-3 md:gap-4 space-y-3 md:space-y-4`}>
          {images.map((src, i) => (
            <div
              key={i}
              onClick={() => setLightbox(i)}
              className="break-inside-avoid cursor-zoom-in bg-[#050505] border border-white/10 rounded-xl overflow-hidden hover:border-[#a7dd5d]/50 hover:shadow-[0_0_30px_rgba(167,221,93,0.08)] active:scale-[0.98] transition-all duration-300 group"
            >
              <img src={src} className="w-full h-auto block group-hover:scale-[1.02] transition-transform duration-300" loading="lazy" />
            </div>
          ))}
        </div>

        {lightbox !== null && (
          <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-sm flex items-center justify-center p-2 md:p-4" onClick={() => setLightbox(null)}>
            <button className="absolute top-4 right-4 md:top-8 md:right-8 w-10 h-10 md:w-12 md:h-12 bg-white/10 border border-white/10 rounded-full flex items-center justify-center text-white hover:bg-white/30 transition-colors z-[110] text-xl font-light focus:outline-none" onClick={() => setLightbox(null)}>✕</button>
            <button onClick={e => { e.stopPropagation(); setLightbox(p => (p - 1 + images.length) % images.length); }} className="absolute left-2 md:left-4 top-1/2 -translate-y-1/2 w-10 h-10 md:w-12 md:h-12 rounded-full bg-white/15 hover:bg-[#a7dd5d] hover:text-black transition-colors text-2xl font-bold z-[110] focus:outline-none">‹</button>
            <img src={images[lightbox]} alt="Expanded" className="max-h-[88vh] max-w-[88vw] md:max-h-[90vh] md:max-w-[90vw] rounded-xl shadow-2xl border border-white/10 object-contain" onClick={e => e.stopPropagation()} />
            <button onClick={e => { e.stopPropagation(); setLightbox(p => (p + 1) % images.length); }} className="absolute right-2 md:right-4 top-1/2 -translate-y-1/2 w-10 h-10 md:w-12 md:h-12 rounded-full bg-white/15 hover:bg-[#a7dd5d] hover:text-black transition-colors text-2xl font-bold z-[110] focus:outline-none">›</button>
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-xs font-mono text-neutral-400 uppercase tracking-widest">{lightbox + 1} / {images.length}</div>
          </div>
        )}
      </div>
    </section>
  );
}

const WhatsAppIcon = ({ size = 24, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" className={className} xmlns="http://www.w3.org/2000/svg">
    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51a12.8 12.8 0 0 0-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z"/>
  </svg>
);

const ReactLogo = ({size=24, className=""}) => (
  <svg width={size} height={size} viewBox="-11.5 -10.23 23 20.46" className={className}>
    <circle cx="0" cy="0" r="2.05" fill="#61dafb"/>
    <g stroke="#61dafb" strokeWidth="1" fill="none">
      <ellipse rx="11" ry="4.2"/>
      <ellipse rx="11" ry="4.2" transform="rotate(60)"/>
      <ellipse rx="11" ry="4.2" transform="rotate(120)"/>
    </g>
  </svg>
);

const SupabaseLogo = ({size=24, className=""}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <path fillRule="evenodd" clipRule="evenodd" d="M21.36 12L12 21V12H2.64L12 3V12H21.36Z" fill="#3ECF8E"/>
  </svg>
);

export default function Home() {
  const [activeTab, setActiveTab] = useState('whatsapp');

  return (
    <div className="min-h-screen bg-black text-[#f0f0f0] flex flex-col font-sans selection:bg-[#a7dd5d] selection:text-black overflow-x-hidden relative">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 h-16 border-b border-white/10 flex items-center justify-between px-6 lg:px-10 z-[120] bg-black/80 backdrop-blur-md">
        <a href="/" className="flex items-center gap-2 group">
          <img src="/spenzo-logo.png" alt="Spenzo Logo" className="h-8 w-auto group-hover:scale-105 transition-transform duration-300" />
          <span className="font-semibold tracking-tight text-lg">Spenzo</span>
        </a>
        <nav className="flex items-center gap-6 ml-8">
          <Link 
            to="/analytics" 
            className="font-semibold tracking-wide uppercase bg-white/5 text-white border border-white/10 hover:bg-white/10 transition-colors flex items-center gap-2 rounded-sm text-sm px-4 py-2 hover:border-[#a7dd5d]"
          >
            <LineChart size={16} /> Analytics
          </Link>
        </nav>
      </header>

      {/* Hero Section */}
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

      {/* Visual Showcases */}
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
      "/PATH/TO/Spenzo/main.py"
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

      {/* Interactive QuickStart Guide */}
      <section className="bg-[#050505] border-t border-white/5 py-16 md:py-24 px-4 md:px-6 z-10 relative">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold tracking-tight mb-4 text-white">QuickStart Guide</h2>
            <p className="text-neutral-400">Get up and running with Spenzo in under 2 minutes.</p>
          </div>
          
          {/* Tabs */}
          <div className="flex justify-center gap-4 mb-8 flex-wrap">
            <button 
              onClick={() => setActiveTab('whatsapp')}
              className={`px-6 py-3 rounded-md font-semibold text-sm transition-all ${activeTab === 'whatsapp' ? 'bg-[#a7dd5d] text-black shadow-[0_0_15px_rgba(167,221,93,0.3)]' : 'bg-[#0c0c0c] text-neutral-400 border border-white/10 hover:text-white'}`}
            >
              1. WhatsApp
            </button>
            <button 
              onClick={() => setActiveTab('claude-exe')}
              className={`px-6 py-3 rounded-md font-semibold text-sm transition-all ${activeTab === 'claude-exe' ? 'bg-[#a7dd5d] text-black shadow-[0_0_15px_rgba(167,221,93,0.3)]' : 'bg-[#0c0c0c] text-neutral-400 border border-white/10 hover:text-white'}`}
            >
              2. Claude (No Setup)
            </button>
            <button 
              onClick={() => setActiveTab('claude-cloud')}
              className={`px-6 py-3 rounded-md font-semibold text-sm transition-all ${activeTab === 'claude-cloud' ? 'bg-[#a7dd5d] text-black shadow-[0_0_15px_rgba(167,221,93,0.3)]' : 'bg-[#0c0c0c] text-neutral-400 border border-white/10 hover:text-white'}`}
            >
              3. Claude (Cloud API)
            </button>
            <button 
              onClick={() => setActiveTab('claude-src')}
              className={`px-6 py-3 rounded-md font-semibold text-sm transition-all ${activeTab === 'claude-src' || activeTab === 'claude' ? 'bg-[#a7dd5d] text-black shadow-[0_0_15px_rgba(167,221,93,0.3)]' : 'bg-[#0c0c0c] text-neutral-400 border border-white/10 hover:text-white'}`}
            >
              4. Claude (Source/Dev)
            </button>
          </div>

          {/* Content */}
          <div className="bg-[#0c0c0c] border border-white/10 p-8 rounded-xl min-h-[320px]">
             {activeTab === 'whatsapp' && (
               <div className="space-y-8 animate-in fade-in duration-500">
                 <div className="flex items-start gap-5 group">
                    <div className="w-10 h-10 rounded-full bg-[#a7dd5d]/10 text-[#a7dd5d] flex items-center justify-center font-bold shrink-0 border border-[#a7dd5d]/20 group-hover:bg-[#a7dd5d] group-hover:text-black transition-colors">1</div>
                    <div>
                      <h4 className="text-white font-bold text-lg mb-2">Message the Bot</h4>
                      <p className="text-neutral-400 leading-relaxed">Add <strong className="text-white">+1 (415) 523-8886</strong> to your contacts and open WhatsApp to message the Twilio sandbox number.</p>
                    </div>
                 </div>
                 <div className="flex items-start gap-5 group">
                    <div className="w-10 h-10 rounded-full bg-[#a7dd5d]/10 text-[#a7dd5d] flex items-center justify-center font-bold shrink-0 border border-[#a7dd5d]/20 group-hover:bg-[#a7dd5d] group-hover:text-black transition-colors">2</div>
                    <div>
                      <h4 className="text-white font-bold text-lg mb-2">Join the Sandbox</h4>
                      <p className="text-neutral-400 leading-relaxed">Send the exact phrase <code className="bg-white/10 text-[#a7dd5d] px-2 py-1 rounded text-sm font-mono tracking-widest">join conversation-heading</code> to authenticate your session.</p>
                    </div>
                 </div>
                 <div className="flex items-start gap-5 group">
                    <div className="w-10 h-10 rounded-full bg-[#a7dd5d]/10 text-[#a7dd5d] flex items-center justify-center font-bold shrink-0 border border-[#a7dd5d]/20 group-hover:bg-[#a7dd5d] group-hover:text-black transition-colors">3</div>
                    <div>
                      <h4 className="text-white font-bold text-lg mb-2">Start Tracking</h4>
                      <p className="text-neutral-400 leading-relaxed">Say "Hi" to see the menu, or just text "Spent ₹150 on coffee" to instantly log your first expense!</p>
                    </div>
                 </div>
               </div>
             )}

             {activeTab === 'claude-exe' && (
               <div className="space-y-8 animate-in fade-in duration-500">
                 <div className="flex items-start gap-5 group">
                    <div className="w-10 h-10 rounded-full bg-[#a7dd5d]/10 text-[#a7dd5d] flex items-center justify-center font-bold shrink-0 border border-[#a7dd5d]/20 group-hover:bg-[#a7dd5d] group-hover:text-black transition-colors">1</div>
                    <div className="w-full">
                      <h4 className="text-white font-bold text-lg mb-2">Download the App</h4>
                      <p className="text-neutral-400 leading-relaxed">Download our zero-setup standalone executable from Google Drive to your Desktop. Absolutely no Python installation or coding required!</p>
                      <div className="flex flex-wrap gap-3 mt-4">
                        <a href="https://drive.google.com/drive/folders/1hJIwEehKF4R0T--kcmxNspcS11a5qXkg?usp=share_link" target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 text-sm text-black bg-[#a7dd5d] py-2 px-5 rounded font-semibold hover:bg-white transition-colors">
                            <Download size={18} /> Download Mac Binary
                        </a>
                        <a href="https://drive.google.com/drive/folders/1hJIwEehKF4R0T--kcmxNspcS11a5qXkg?usp=share_link" target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 text-sm text-neutral-300 bg-[#1c1c1c] border border-white/10 py-2 px-5 rounded font-semibold hover:bg-[#a7dd5d] hover:text-black hover:border-[#a7dd5d] transition-colors">
                            <Download size={18} /> Download Windows .exe
                        </a>
                      </div>
                    </div>
                 </div>
                 <div className="flex items-start gap-5 group">
                    <div className="w-10 h-10 rounded-full bg-[#a7dd5d]/10 text-[#a7dd5d] flex items-center justify-center font-bold shrink-0 border border-[#a7dd5d]/20 group-hover:bg-[#a7dd5d] group-hover:text-black transition-colors">2</div>
                    <div className="w-full">
                      <h4 className="text-white font-bold text-lg mb-2">Update Claude Config</h4>
                      <p className="text-neutral-400 leading-relaxed mb-3">Open your Claude Desktop config file and paste this standard tool block. Update the <code className="text-[#a7dd5d]">command</code> path to point exactly to the downloaded file on your desktop.</p>
                      <div className="bg-[#050505] p-3 md:p-4 rounded-lg border border-white/10 text-neutral-300 text-xs md:text-sm font-mono whitespace-pre-wrap break-all overflow-x-auto max-w-full">
{`"mcpServers": {
  "spenzo": {
    "command": "/Users/YOUR_NAME/Desktop/spenzo-mac", /* or spenzo-win.exe */
    "env": { "SUPABASE_URL": "...", "OPENAI_API_KEY": "..." }
  }
}`}
                      </div>
                    </div>
                 </div>
                 <div className="flex items-start gap-5 group">
                    <div className="w-10 h-10 rounded-full bg-[#a7dd5d]/10 text-[#a7dd5d] flex items-center justify-center font-bold shrink-0 border border-[#a7dd5d]/20 group-hover:bg-[#a7dd5d] group-hover:text-black transition-colors">3</div>
                    <div>
                      <h4 className="text-white font-bold text-lg mb-2">Restart & Chat</h4>
                      <p className="text-neutral-400 leading-relaxed">Restart Claude Desktop and enjoy the full native financial experience safely and seamlessly.</p>
                    </div>
                 </div>
               </div>
             )}

             {activeTab === 'claude-cloud' && (
               <div className="space-y-8 animate-in fade-in duration-500">
                 <div className="flex items-start gap-5 group">
                    <div className="w-10 h-10 rounded-full bg-[#a7dd5d]/10 text-[#a7dd5d] flex items-center justify-center font-bold shrink-0 border border-[#a7dd5d]/20 group-hover:bg-[#a7dd5d] group-hover:text-black transition-colors">1</div>
                    <div className="w-full">
                      <h4 className="text-white font-bold text-lg mb-2">Remote Server Setup</h4>
                      <p className="text-neutral-400 leading-relaxed">The Spenzo logic is hosted safely in the cloud. Just download our tiny <code>sse_relay.py</code> connection script!</p>
                    </div>
                 </div>
                 <div className="flex items-start gap-5 group">
                    <div className="w-10 h-10 rounded-full bg-[#a7dd5d]/10 text-[#a7dd5d] flex items-center justify-center font-bold shrink-0 border border-[#a7dd5d]/20 group-hover:bg-[#a7dd5d] group-hover:text-black transition-colors">2</div>
                    <div>
                      <h4 className="text-white font-bold text-lg mb-2">Configure Relay</h4>
                      <div className="bg-[#050505] p-3 md:p-4 rounded-lg border border-white/10 text-neutral-300 text-xs md:text-sm font-mono mt-3 whitespace-pre-wrap break-all overflow-x-auto max-w-full">
{`"mcpServers": {
  "spenzo-cloud": {
    "command": "python",
    "args": ["/Users/YOUR_NAME/Desktop/sse_relay.py", "https://api.spenzo.xyz"]
  }
}`}
                      </div>
                    </div>
                 </div>
                 <div className="flex items-start gap-5 group">
                    <div className="w-10 h-10 rounded-full bg-[#a7dd5d]/10 text-[#a7dd5d] flex items-center justify-center font-bold shrink-0 border border-[#a7dd5d]/20 group-hover:bg-[#a7dd5d] group-hover:text-black transition-colors">3</div>
                    <div>
                      <h4 className="text-white font-bold text-lg mb-2">Zero Local Environment</h4>
                      <p className="text-neutral-400 leading-relaxed">Your machine does exactly 0 compute. The relay forwards Claude's stdio directly to the remote Spenzo servers.</p>
                    </div>
                 </div>
               </div>
             )}

             {(activeTab === 'claude-src' || activeTab === 'claude') && (
               <div className="space-y-8 animate-in fade-in duration-500">
                 <div className="flex items-start gap-5 group">
                    <div className="w-10 h-10 rounded-full bg-[#a7dd5d]/10 text-[#a7dd5d] flex items-center justify-center font-bold shrink-0 border border-[#a7dd5d]/20 group-hover:bg-[#a7dd5d] group-hover:text-black transition-colors">1</div>
                    <div className="w-full">
                      <h4 className="text-white font-bold text-lg mb-2">Clone &amp; Install</h4>
                      <div className="bg-[#050505] p-3 md:p-4 rounded-lg border border-white/10 text-neutral-300 text-xs md:text-sm font-mono mt-3 whitespace-pre-wrap break-all overflow-x-auto max-w-full">
                        git clone https://github.com/Arav-Arun/Spenzo.git<br/>
                        cd Spenzo<br/>
                        uv sync
                      </div>
                    </div>
                 </div>
                 <div className="flex items-start gap-5 group">
                    <div className="w-10 h-10 rounded-full bg-[#a7dd5d]/10 text-[#a7dd5d] flex items-center justify-center font-bold shrink-0 border border-[#a7dd5d]/20 group-hover:bg-[#a7dd5d] group-hover:text-black transition-colors">2</div>
                    <div>
                      <h4 className="text-white font-bold text-lg mb-2">Set Environment Variables</h4>
                      <p className="text-neutral-400 leading-relaxed">Create a <code>.env</code> file in the root codebase containing your Supabase, Twilio, Alchemy, and Helius secrets.</p>
                    </div>
                 </div>
                 <div className="flex items-start gap-5 group">
                    <div className="w-10 h-10 rounded-full bg-[#a7dd5d]/10 text-[#a7dd5d] flex items-center justify-center font-bold shrink-0 border border-[#a7dd5d]/20 group-hover:bg-[#a7dd5d] group-hover:text-black transition-colors">3</div>
                    <div>
                      <h4 className="text-white font-bold text-lg mb-2">Update Claude Config</h4>
                      <p className="text-neutral-400 leading-relaxed">Add the Py/UV target to your <code>claude_desktop_config.json</code> and restart.</p>
                    </div>
                 </div>
               </div>
             )}
          </div>
        </div>
      </section>

      <ScreenshotGallery 
        title="WhatsApp Integration in Action" 
        subtitle="Real screenshots of Spenzo functioning perfectly on WhatsApp. Tap to expand." 
        images={WHATSAPP_IMGS} 
      />
      
      <div className="sm:hidden">
        <ScreenshotGallery 
          title="Spenzo MCP in Claude Desktop" 
          subtitle="Real screenshots of Spenzo running live inside Claude Desktop. Tap any image to rotate or expand." 
          images={CLAUDE_IMGS} 
        />
      </div>
      <div className="hidden sm:block">
        <MasonryGallery 
          title="Spenzo MCP in Claude Desktop" 
          subtitle="Real screenshots of Spenzo running live inside Claude Desktop. Click any image to expand." 
          images={CLAUDE_IMGS} 
        />
      </div>

      {/* Feature Grid */}
      <section className="py-16 md:py-24 px-6 z-10 relative border-t border-white/5 bg-[#050505]">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight mb-4 text-[#a7dd5d]">Omni-Channel Capabilities</h2>
            <p className="text-neutral-400">Everything you need to manage your wealth, consolidated into a single NLP layer.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: MessageCircle, title: 'Conversational Logging', desc: 'Text "Spent ₹450 on Uber". GPT-4o extracts the date, normalizes the category, and upserts instantly.' },
              { icon: Image, title: 'Vision OCR Parsing', desc: 'Snap a photo of a crumpled receipt. The system extracts the merchant and exact total automatically.' },
              { icon: Search, title: 'Deep Semantic Search', desc: 'Ask "Did I buy coffee last month?" Query your entire PostgreSQL ledger using pure natural language.' },
              { icon: Edit3, title: 'Ledger Management', desc: 'Make a mistake? Simply say "Wait, that Uber was actually ₹500" and the bot actively patches the database.' },
              { icon: LayoutDashboard, title: 'Real-time Analytics', desc: 'View beautiful, dynamically updating mobile-optimized spending charts and category donuts.' },
              { icon: GlobeLock, title: 'Cross-Platform Sync', desc: 'Link your desktop Claude MCP with your WhatsApp isolated session securely via Twilio OTP.' },
              { icon: Users, title: 'The Splitwise Killer', desc: 'A dedicated IOU Ledger. Ask "Who owes me?" to list all active debtors.' },
              { icon: QrCode, title: 'Dynamic UPI Dispatch', desc: 'Spenzo instantly builds 1-click GPay/PhonePe upi://pay intent links to settle those debts instantly.' },
              { icon: Bitcoin, title: 'Live Asset Ticker', desc: 'Ping CoinGecko directly in chat. "What\'s the price of SOL?" accurately monitors crypto holdings.' }
            ].map((f, i) => (
              <div key={i} className="p-6 border border-white/5 bg-[#0c0c0c] hover:border-[#a7dd5d]/20 transition-colors group">
                <f.icon className="text-neutral-500 mb-4 group-hover:text-[#a7dd5d] transition-colors" size={24} />
                <h3 className="text-lg font-bold mb-2 text-white">{f.title}</h3>
                <p className="text-sm text-neutral-400 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Web3 Advanced Features */}
      <section className="py-16 md:py-24 px-6 z-10 relative border-t border-white/5 bg-[#050505]">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight mb-4 text-[#a7dd5d]">The Web3 Edge</h2>
            <p className="text-neutral-400">Four ways Spenzo's MCP turns natural chat into a Bloomberg Terminal for crypto.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-8">
            {[
              { icon: LineChart, title: 'The Whale Snapshot', prompt: "What's my crypto worth right now?", desc: 'Scans your entire wallet (USDC, SOL, Meme coins), pings live prices, and instantly calculates your exact fiat net worth.' },
              { icon: ArrowLeftRight, title: '1-Click DEX Execution', prompt: 'Swap 10 SOL for USDC.', desc: 'Pings Jupiter aggregators for live quotes and securely generates a 1-Click execution deep-link to route trades natively in your mobile wallet.' },
              { icon: Flame, title: 'Real-time Gas Burn', prompt: 'How much did I burn on gas?', desc: 'Hits Blockscout and Helius RPCs to sweep your recent on-chain transactions and compute exact capital lost to execution friction.' },
              { icon: TrendingUp, title: 'DeFi Yield Crawler', prompt: 'How much interest did I earn?', desc: 'Crawls Lido, RocketPool, and Jito smart contracts your wallet interacts with to output active staked balances and APY rewards.' }
            ].map((f, i) => (
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


      {/* Footer */}
      <footer className="py-8 text-center text-xs font-mono text-neutral-600 uppercase tracking-widest bg-[#0a0a0a] z-10 relative">
        SPENZO &copy; {new Date().getFullYear()} : Made by <a href="https://aravarun.xyz" target="_blank" rel="noreferrer" className="text-[#a7dd5d] hover:underline">Arav Arun</a>
      </footer>
    </div>
  );
}
