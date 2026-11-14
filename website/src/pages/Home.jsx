import { ArrowRight } from 'lucide-react';
import { NAME, whatsappLink } from '../brand';
import Dashboard from '../components/Dashboard';
import FeatureShowcase from '../components/FeatureShowcase';
import Footer from '../components/Footer';
import Header from '../components/Header';
import { WhatsAppIcon } from '../components/Icons';
import Mascot from '../components/Mascot';
import PhoneChat from '../components/PhoneChat';
import { SAMPLE_OVERVIEW, SAMPLE_PORTFOLIO } from '../lib/sample';

const HERO_CHAT = [
  { me: true, text: 'chai 20', time: '9:12' },
  { text: '✅ ₹20 · Chai / Food & Dining', buttons: ['↩️ Undo', '📊 This month'], time: '9:12' },
  { me: true, text: 'dinner 3000 split with Arav and Riya', time: '21:40' },
  { text: '✅ ₹1,000 · Dinner / Food & Dining\nArav and Riya owe you ₹1,000 each 🤝', time: '21:40' },
  { me: true, text: 'can I afford a 40k phone next month?', time: '21:41' },
  { text: 'You usually spend ~₹31k a month, so ₹40k is a stretch. Put away ₹10k a month and it’s yours by March 🎯', time: '21:41' },
];

const STEPS = [
  { pose: 'wave', title: 'Say hi on WhatsApp', body: 'Tap the button and send the message. That’s your account made. No app, no forms, no password.' },
  { pose: 'salute', title: 'Tell it what you spend', body: 'Type it, send a photo of the bill, or a voice note. In English, Hinglish or Hindi.' },
  { pose: 'report', title: 'Ask, and see the full picture', body: 'Ask anything about your money, or tap a button to open your dashboard.' },
];

const PROMISES = [
  ['No bank login', `${NAME} never asks for passwords, card numbers, PINs or OTPs. It only knows what you tell it.`],
  ['Only you can see it', 'Everything is tied to your WhatsApp number. Nobody else can open your data.'],
  ['Delete anytime', 'Send “delete my data” and tap Yes. Everything is gone for good.'],
  ['Free to use', 'No plans, no ads, and your data is never sold.'],
];

const FAQ = [
  ['Is it free?', 'Yes. There’s no paid plan and no ads.'],
  ['Do I need to download an app?', 'No. Spenzo lives in WhatsApp. The dashboard opens in your browser from a button in the chat.'],
  ['Do I have to connect my bank?', 'No. You tell Spenzo what you spend. It never asks for bank logins, card numbers or passwords.'],
  ['Who can see my data?', 'Only you. It’s tied to your WhatsApp number, and the dashboard only opens from a link sent to your own chat.'],
  ['Will it tell me which stocks to buy?', 'No. It shows facts about your own investments, like their value and how they’re doing. It never gives buy or sell tips.'],
  ['Will it spam me?', 'No. It only speaks up in its replies to you, at most once per message, and “stop nudges” turns that off.'],
  ['How do I delete my data?', 'Send “delete my data” on WhatsApp and tap Yes. It’s permanent.'],
];

function Section({ id, title, intro, children, className = '' }) {
  return (
    <section id={id} className={`mx-auto max-w-6xl px-4 py-16 sm:px-6 md:py-24 ${className}`}>
      {title && <h2 className="max-w-2xl text-3xl font-extrabold md:text-[2.6rem] md:leading-tight">{title}</h2>}
      {intro && <p className="mt-4 max-w-2xl text-lg leading-relaxed text-muted">{intro}</p>}
      <div className={title ? 'mt-12' : ''}>{children}</div>
    </section>
  );
}

const WhatsAppButton = ({ label = 'Say hi on WhatsApp' }) => (
  <a href={whatsappLink('Hi')} target="_blank" rel="noreferrer"
    className="squircle inline-flex items-center justify-center gap-2 border border-leaf-deep bg-leaf-deep px-6 py-4 font-medium text-white shadow-sm transition-colors hover:bg-ink">
    <WhatsAppIcon size={19} /> {label} <ArrowRight size={17} />
  </a>
);

export default function Home() {
  return (
    <div className="min-h-screen font-sans">
      <Header />

      <main className="mx-auto grid max-w-6xl items-center gap-14 px-4 pt-10 pb-16 sm:px-6 md:pt-16 lg:min-h-[calc(100svh-5.5rem)] lg:grid-cols-[1.05fr_0.95fr] lg:py-10">
        <div>
          <h1 className="mb-6 text-5xl leading-[1.02] font-extrabold md:text-7xl">Just text your&nbsp;money.</h1>
          <p className="mb-9 max-w-xl text-lg leading-relaxed text-muted md:text-xl">
            {NAME} is your money buddy on WhatsApp. Track what you spend, split bills with friends, save for goals and
            keep an eye on your investments, all just by chatting.
          </p>
          <WhatsAppButton />
        </div>
        <div className="relative isolate mx-auto w-fit">
          <PhoneChat messages={HERO_CHAT} />
        </div>
      </main>

      <Section id="how" title="Three steps. Nothing to install.">
        <ol className="grid gap-4 md:grid-cols-3">
          {STEPS.map((s) => (
            <li key={s.title} className="rounded-3xl border border-line bg-card p-6">
              <Mascot pose={s.pose} className="mb-3 h-20 w-20" />
              <h3 className="mb-2 text-xl font-bold">{s.title}</h3>
              <p className="leading-relaxed text-muted">{s.body}</p>
            </li>
          ))}
        </ol>
      </Section>

      <div>
        <Section id="features" title="Everything you can do in one chat" intro="See exactly what each conversation looks like, or tap a feature to jump to it.">
          <FeatureShowcase />
        </Section>
      </div>

      <Section title="Your whole month, one tap away" intro="Every reply has a button that opens your dashboard: spending by day, budgets, goals, friends and investments. No password, ever.">
        <div className="rounded-3xl border border-line bg-paper p-3 sm:p-6">
          <h3 className="mb-4 px-1 font-display text-lg font-bold">November 2026</h3>
          <Dashboard data={SAMPLE_OVERVIEW} portfolio={SAMPLE_PORTFOLIO} />
        </div>
      </Section>

      <Section title="Your money stays yours">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {PROMISES.map(([t, b]) => (
            <div key={t} className="rounded-3xl border border-line bg-card p-6">
              <h3 className="mb-2 text-lg font-bold">{t}</h3>
              <p className="leading-relaxed text-muted">{b}</p>
            </div>
          ))}
        </div>
      </Section>

      <div>
        <Section id="faq" title="Questions people ask">
          <div className="grid gap-3 md:grid-cols-2">
            {FAQ.map(([q, a]) => (
              <details key={q} className="group rounded-2xl border border-line bg-card p-5 open:border-leaf">
                <summary className="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold">
                  {q}<span className="text-xl leading-none text-leaf transition-transform group-open:rotate-45">+</span>
                </summary>
                <p className="mt-3 leading-relaxed text-muted">{a}</p>
              </details>
            ))}
          </div>
        </Section>
      </div>

      <Footer />
    </div>
  );
}
