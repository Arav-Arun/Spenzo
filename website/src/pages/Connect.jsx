import { useEffect, useState } from 'react';
import { API_URL, NAME, whatsappLink } from '../brand';
import Footer from '../components/Footer';
import Header from '../components/Header';
import { WhatsAppIcon } from '../components/Icons';

// /connect#k=<personal key>: Spenzo sends this link when you say "connect ai" on WhatsApp.
// The key stays in this tab only; it's removed from the address bar straight away.
const PLACEHOLDER = 'YOUR-PRIVATE-LINK';

const APPS = [
  {
    name: 'Claude',
    steps: ['Open Claude (app or claude.ai) → Settings → Connectors.', 'Choose “Add custom connector”, name it Spenzo, and paste your link.'],
    copy: (url) => url,
    copyLabel: 'Copy link',
  },
  {
    name: 'ChatGPT',
    steps: ['In ChatGPT settings, open Apps & Connectors and turn on developer mode.', 'Create a connector named Spenzo and paste your link as the server URL.'],
    copy: (url) => url,
    copyLabel: 'Copy link',
  },
  {
    name: 'Cursor',
    steps: ['Open Cursor Settings → MCP → Add new MCP server.', 'Paste this into the file it opens and save.'],
    copy: (url) => JSON.stringify({ mcpServers: { spenzo: { url } } }, null, 2),
    copyLabel: 'Copy config',
  },
  {
    name: 'Claude Code',
    steps: ['Run this once in your terminal.'],
    copy: (url) => `claude mcp add --transport http spenzo "${url}"`,
    copyLabel: 'Copy command',
  },
  {
    name: 'Any other app',
    steps: ['Paste this prompt into an AI agent that can edit its own settings, or follow it yourself.'],
    copy: (url) => `Add an MCP server called "Spenzo" using Streamable HTTP at this URL: ${url}\nIt's my personal finance assistant: expenses, budgets, goals, friends I owe or who owe me, and investments. Use it whenever I ask about my money.`,
    copyLabel: 'Copy prompt',
  },
];

function CopyBox({ text, label }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch { /* clipboard blocked: the text is visible to copy by hand */ }
  };
  return (
    <div className="mt-4 overflow-hidden rounded-2xl border border-line bg-ink text-paper">
      <pre className="max-h-48 overflow-auto p-4 font-mono text-[13px] leading-relaxed whitespace-pre-wrap break-all">{text}</pre>
      <div className="flex justify-end border-t border-white/10 p-2">
        <button onClick={copy} className="rounded-full bg-paper px-4 py-2 text-sm font-semibold text-ink hover:bg-white">
          {copied ? 'Copied ✓' : label}
        </button>
      </div>
    </div>
  );
}

export default function Connect() {
  const [key] = useState(() => new URLSearchParams(window.location.hash.slice(1)).get('k') || '');
  const [app, setApp] = useState(0);

  // Take the key out of the address bar so it isn't left in history or copied by accident.
  useEffect(() => {
    if (key) window.history.replaceState(null, '', '/connect');
  }, [key]);

  const url = key ? `${API_URL}/mcp?key=${key}` : PLACEHOLDER;
  const chosen = APPS[app];

  return (
    <div className="min-h-screen font-sans">
      <Header />
      <main className="mx-auto max-w-3xl px-4 pt-14 pb-20 sm:px-6">
        <h1 className="text-4xl font-extrabold md:text-5xl">Use {NAME} inside your AI</h1>
        <p className="mt-4 text-lg leading-relaxed text-muted">
          Ask Claude, ChatGPT or Cursor about your money: “plan my savings for a trip”, “what did I spend on food this year?”,
          “make me a spreadsheet of this month”. They use the same data as your WhatsApp chat.
        </p>

        <ol className="mt-12 space-y-10">
          <li>
            <h2 className="text-xl font-bold">1. Get your private link</h2>
            {key ? (
              <p className="mt-3 rounded-2xl bg-leaf-soft px-4 py-3 font-semibold text-leaf-deep">✅ Your private link is ready. It’s filled in below.</p>
            ) : (
              <>
                <p className="mt-2 text-muted">Send <b className="text-ink">connect ai</b> to {NAME} on WhatsApp, then tap the button in the reply. It brings you back here with your link filled in.</p>
                <a href={whatsappLink('connect ai')} target="_blank" rel="noreferrer"
                  className="mt-4 inline-flex items-center gap-2 rounded-full bg-leaf-deep px-6 py-3.5 font-semibold text-white hover:bg-ink">
                  <WhatsAppIcon size={18} /> Get my link on WhatsApp
                </a>
              </>
            )}
          </li>

          <li>
            <h2 className="text-xl font-bold">2. Add it to your app</h2>
            <div className="mt-4 flex flex-wrap gap-2" role="tablist">
              {APPS.map((a, i) => (
                <button key={a.name} role="tab" aria-selected={i === app} onClick={() => setApp(i)}
                  className={`rounded-full px-4 py-2 text-sm font-semibold transition-colors ${i === app ? 'bg-ink text-white' : 'border border-line bg-card text-muted hover:text-ink'}`}>
                  {a.name}
                </button>
              ))}
            </div>
            <ul className="mt-5 space-y-1.5 text-ink/85">{chosen.steps.map((s) => <li key={s}>{s}</li>)}</ul>
            <CopyBox text={chosen.copy(url)} label={chosen.copyLabel} />
          </li>

          <li>
            <h2 className="text-xl font-bold">3. Ask about your money</h2>
            <p className="mt-2 text-muted">Try “How much did I spend on food this month?” or “Make me a plan to save ₹50,000 by June.”</p>
          </li>
        </ol>

        <p className="mt-12 rounded-2xl border border-line bg-card p-5 text-sm leading-relaxed text-muted">
          <b className="text-ink">Keep your link private.</b> Anyone with it can see your {NAME} data. If it ever leaks, send
          <b className="text-ink"> sign me out everywhere</b> on WhatsApp and every old link stops working.
        </p>
      </main>
      <Footer />
    </div>
  );
}
