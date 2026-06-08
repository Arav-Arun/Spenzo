import React from 'react';
import { MessageCircle, Image, Search, Edit3, GlobeLock, Users, QrCode, Bitcoin } from 'lucide-react';

export default function Features() {
  const list = [
    { icon: MessageCircle, title: 'Conversational Logging', desc: 'Text "Spent ₹450 on Uber". GPT-4o extracts the date, normalizes the category, and upserts instantly.' },
    { icon: Image, title: 'Vision OCR Parsing', desc: 'Snap a photo of a crumpled receipt. The system extracts the merchant and exact total automatically.' },
    { icon: Search, title: 'Deep Semantic Search', desc: 'Ask "Did I buy coffee last month?" Query your entire PostgreSQL ledger using pure natural language.' },
    { icon: Edit3, title: 'Ledger Management', desc: 'Make a mistake? Simply say "Wait, that Uber was actually ₹500" and the bot actively patches the database.' },
    { icon: GlobeLock, title: 'Cross-Platform Sync', desc: 'Link your desktop Claude MCP with your WhatsApp isolated session securely via Twilio OTP.' },
    { icon: Users, title: 'The Splitwise Killer', desc: 'A dedicated IOU Ledger. Ask "Who owes me?" to list all active debtors.' },
    { icon: QrCode, title: 'Dynamic UPI Dispatch', desc: 'Spenzo instantly builds 1-click GPay/PhonePe upi://pay intent links to settle those debts instantly.' },
    { icon: Bitcoin, title: 'Live Asset Ticker', desc: 'Ping CoinGecko directly in chat. "What\'s the price of SOL?" accurately monitors crypto holdings.' }
  ];

  return (
    <section className="py-16 md:py-24 px-6 z-10 relative border-t border-white/5 bg-[#050505]">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight mb-4 text-[#a7dd5d]">Omni-Channel Capabilities</h2>
          <p className="text-neutral-400">Everything you need to manage your wealth, consolidated into a single NLP layer.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {list.map((f, i) => (
            <div key={i} className="p-6 border border-white/5 bg-[#0c0c0c] hover:border-[#a7dd5d]/20 transition-colors group">
              <f.icon className="text-neutral-500 mb-4 group-hover:text-[#a7dd5d] transition-colors" size={24} />
              <h3 className="text-lg font-bold mb-2 text-white">{f.title}</h3>
              <p className="text-sm text-neutral-400 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
