import React, { useState } from 'react';
import { Download } from 'lucide-react';

export default function QuickStart() {
  const [activeTab, setActiveTab] = useState('whatsapp');

  return (
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
            className={`px-6 py-3 rounded-md font-semibold text-sm transition-all ${activeTab === 'claude-src' ? 'bg-[#a7dd5d] text-black shadow-[0_0_15px_rgba(167,221,93,0.3)]' : 'bg-[#0c0c0c] text-neutral-400 border border-white/10 hover:text-white'}`}
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
                    <p className="text-neutral-400 leading-relaxed">Download our zero-setup standalone executable from GitHub Releases. Absolutely no Python installation or coding required!</p>
                    <div className="flex flex-wrap gap-3 mt-4">
                      <a href="https://github.com/Arav-Arun/Spenzo/releases/latest/download/spenzo-mac" target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 text-sm text-black bg-[#a7dd5d] py-2 px-5 rounded font-semibold hover:bg-white transition-colors">
                          <Download size={18} /> Download Mac Binary
                      </a>
                      <a href="https://github.com/Arav-Arun/Spenzo/releases/latest/download/spenzo-win.exe" target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 text-sm text-neutral-300 bg-[#1c1c1c] border border-white/10 py-2 px-5 rounded font-semibold hover:bg-[#a7dd5d] hover:text-black hover:border-[#a7dd5d] transition-colors">
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

           {activeTab === 'claude-src' && (
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
  );
}
