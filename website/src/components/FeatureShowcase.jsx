import { useEffect, useRef, useState } from 'react';
import Mascot from './Mascot';
import PhoneChat, { PhoneVideo } from './PhoneChat';

// Each feature, explained plainly, next to the exact conversation it creates.
// Real screen recordings replace the drawn chat: put website/public/demo/<key>.mp4 (and <key>.jpg as
// its first frame) in place, then add the key here.
const RECORDED = new Set([]);
const LOG_BUTTONS = ['↩️ Undo', '✏️ Edit', '📊 This month'];
const FEATURES = [
  {
    key: 'log',
    title: 'Log what you spend in seconds',
    short: 'Log spends',
    pose: 'salute',
    body: 'Type it the way you’d text a friend, send a photo of the bill or a voice note, or forward your bank statement PDF to fill in the whole month. Spenzo picks the categories for you.',
    chat: [
      { me: true, text: 'uber 260', time: '9:05' },
      { text: '✅ ₹260 · Uber / Transport', buttons: ['↩️ Undo', '📊 This month'], time: '9:05' },
      { me: true, photo: 'bill', time: '13:20' },
      { text: '✅ ₹1,240 · Domino’s / Food & Dining', time: '13:20' },
      { me: true, voice: '0:04', time: '19:02' },
      { text: '🎙️ “paid 450 for electricity”\n✅ ₹450 · Electricity / Bills & Rent', time: '19:02' },
    ],
  },
  {
    key: 'split',
    title: 'Split bills with friends',
    short: 'Split bills',
    pose: 'split',
    body: 'Tell Spenzo who was there, or forward the bill from your group chat. It works out everyone’s share, keeps a running tab with each friend, and makes payment links you can forward.',
    chat: [
      { me: true, text: 'dinner 3000 split with Arav and Riya', time: '21:40' },
      { text: '✅ ₹1,000 · Dinner / Food & Dining\nArav and Riya owe you ₹1,000 each 🤝', time: '21:40' },
      { me: true, text: 'who owes me?', time: '10:12' },
      { text: '🤝 Who owes what\n• Arav owes you ₹1,000\n• Riya owes you ₹1,000\n• You owe Kabir ₹200', time: '10:12' },
      { me: true, text: 'riya paid me back', time: '18:30' },
      { text: '👍 Done. You and Riya are all square.', time: '18:30' },
    ],
  },
  {
    key: 'budgets',
    title: 'Budgets that warn you early',
    short: 'Budgets',
    pose: 'worried',
    body: 'Set a limit in plain words. Spenzo tells you when you’ve used 80%, when you’re over, and if you’re spending too fast for the month.',
    chat: [
      { me: true, text: 'keep food under 6k a month', time: '9:00' },
      { text: '🎯 Food & Dining budget set to ₹6,000 a month. I’ll tell you at 80%.', time: '9:00' },
      { me: true, text: 'swiggy 420', time: '20:45' },
      { text: '✅ ₹420 · Swiggy / Food & Dining\n\n😬 Food is at 82% of ₹6,000, ₹1,070 left for 15 days.', buttons: LOG_BUTTONS, time: '20:45' },
    ],
  },
  {
    key: 'goals',
    title: 'Save up for what you want',
    short: 'Save up',
    pose: 'save',
    body: 'Name a goal and a date. Spenzo tells you how much to put away each month, and on payday it asks if you want to move money to it.',
    chat: [
      { me: true, text: 'Goa trip 30k by March', time: '11:15' },
      { text: '🎯 Goa trip: ₹30,000 by 31 March. That’s ₹7,500 a month.', time: '11:15' },
      { me: true, text: 'salary aaya 60k', time: '10:02' },
      { text: '💸 Salary logged!\n\nPayday! Move ₹7,500 to Goa trip? That keeps it on track.', buttons: ['Move ₹7,500', 'Not now'], time: '10:02' },
      { me: true, text: 'Move ₹7,500', time: '10:02' },
      { text: '🎯 ₹7,500 moved to Goa trip. You’re at 25%.', time: '10:02' },
    ],
  },
  {
    key: 'invest',
    title: 'Keep an eye on your investments',
    short: 'Investments',
    pose: 'grow',
    body: 'Send a screenshot of your Groww or Zerodha holdings, or forward your mutual fund statement. Spenzo tracks your stocks and funds at live prices. Facts only, never tips.',
    chat: [
      { me: true, photo: 'holdings', time: '19:10' },
      { text: '📈 Added 4 holdings: TCS, Reliance, Parag Parikh Flexi Cap and Nifty 50 Index.', time: '19:10' },
      { me: true, text: 'how are my investments doing?', time: '19:11' },
      { text: 'Worth ₹1,48,230 right now, up ₹12,380 (9.1%) on what you paid.\nTCS is 38% of your portfolio.', time: '19:11' },
    ],
  },
  {
    key: 'ask',
    title: 'Ask anything about your money',
    short: 'Ask anything',
    pose: 'thinking',
    body: 'Where did it go? Can you afford it? Spenzo answers from your real numbers, in English, Hinglish or Hindi, and sends a chart when a picture says it better.',
    chat: [
      { me: true, text: 'where did my money go this month?', time: '22:01' },
      { text: '📊 November so far: ₹26,530\nRent ₹18,000 · Food ₹4,930 · Shopping ₹2,600 · Transport ₹1,000', time: '22:01' },
      { me: true, text: 'kya main 40k ka phone le sakta hoon?', time: '22:03' },
      { text: 'Abhi thoda tight hai. Har mahine ~₹31k kharcha hota hai. ₹10k mahina bachao aur March tak phone tumhara 🎯', time: '22:03' },
    ],
  },
  {
    key: 'dashboard',
    title: 'See everything on your dashboard',
    short: 'Dashboard',
    pose: 'report',
    body: 'Tap the button in any reply to see your month in charts: budgets, goals, friends and investments. No password, ever.',
    chat: [
      { me: true, text: 'where did it all go?', time: '21:00' },
      { text: '📊 November so far: ₹26,530\nRent ₹18,000 · Food ₹4,930 · Shopping ₹2,600', link: 'See everything', time: '21:00' },
    ],
  },
];

const SECONDS = 6;

export default function FeatureShowcase() {
  const [active, setActive] = useState(0);
  const [hovering, setHovering] = useState(false);
  const [onScreen, setOnScreen] = useState(false);
  const [calm] = useState(() => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches);
  const box = useRef(null);
  const rotating = !hovering && onScreen && !calm;
  const feature = FEATURES[active];

  // Only rotate while the section is actually being looked at.
  useEffect(() => {
    const seen = new IntersectionObserver(([entry]) => setOnScreen(entry.isIntersecting), { threshold: 0.35 });
    seen.observe(box.current);
    return () => seen.disconnect();
  }, []);

  useEffect(() => {
    if (!rotating) return;
    const next = setTimeout(() => setActive((i) => (i + 1) % FEATURES.length), SECONDS * 1000);
    return () => clearTimeout(next);
  }, [active, rotating]);

  const progress = (on) => on && rotating && (   /* restarts with the timer whenever rotation resumes */
    <span aria-hidden="true" className="absolute bottom-0 left-0 h-[3px] w-full origin-left bg-leaf"
      style={{ animation: `progress ${SECONDS}s linear forwards` }} />
  );
  const mouseOnly = (value) => (e) => e.pointerType === 'mouse' && setHovering(value);

  return (
    <div ref={box} onPointerEnter={mouseOnly(true)} onPointerLeave={mouseOnly(false)}
      className="grid items-start gap-8 lg:grid-cols-[1fr_auto] lg:gap-16">
      {/* Phones: square tiles, four on top and three centred below, with the chosen feature explained underneath. */}
      <div className="min-w-0 lg:hidden">
        <div role="tablist" aria-label="Features" className="mx-auto flex max-w-xl flex-wrap justify-center gap-2 sm:gap-3">
          {FEATURES.map((f, i) => {
            const on = i === active;
            return (
              <button key={f.key} role="tab" aria-selected={on} onClick={() => setActive(i)}
                className={`relative flex aspect-square w-[calc((100%-1.5rem)/4)] flex-col items-center justify-center gap-1.5 overflow-hidden rounded-2xl border p-1 transition-colors sm:w-[calc((100%-2.25rem)/4)] ${on ? 'border-leaf bg-card shadow-sm' : 'border-line bg-card/50'}`}>
                <Mascot pose={f.pose} title="" className={`h-9 w-9 transition sm:h-12 sm:w-12 ${on ? '' : 'opacity-75 grayscale-[35%]'}`} />
                <span className={`text-center text-[11.5px] leading-tight font-bold sm:text-[13px] ${on ? 'text-ink' : 'text-ink/65'}`}>{f.short}</span>
                {progress(on)}
              </button>
            );
          })}
        </div>
        <div key={active} className="mt-5 animate-[fadein_.35s_ease-out]">
          <h3 className="text-xl font-bold">{feature.title}</h3>
          <p className="mt-2 leading-relaxed text-muted">{feature.body}</p>
        </div>
      </div>

      {/* Larger screens: the full list beside the phone. */}
      <ol className="hidden space-y-2.5 lg:block" role="tablist" aria-label="Features">
        {FEATURES.map((f, i) => {
          const on = i === active;
          return (
            <li key={f.key}>
              <button role="tab" aria-selected={on} onClick={() => setActive(i)}
                className={`relative flex w-full items-center gap-4 overflow-hidden rounded-2xl border p-5 text-left transition-colors ${on ? 'border-leaf bg-card' : 'border-transparent hover:border-line hover:bg-card/60'}`}>
                <Mascot pose={f.pose} title="" className={`shrink-0 transition-all ${on ? 'h-16 w-16' : 'h-12 w-12 opacity-80 grayscale-[35%]'}`} />
                <span className="min-w-0">
                  <span className={`block text-lg font-bold ${on ? 'text-ink' : 'text-ink/70'}`}>{f.title}</span>
                  {on && <span className="mt-1 block leading-relaxed text-muted">{f.body}</span>}
                </span>
                {progress(on)}
              </button>
            </li>
          );
        })}
      </ol>

      <div className="relative isolate mx-auto w-fit lg:sticky lg:top-28">
        {RECORDED.has(feature.key)
          ? <PhoneVideo key={active} src={`/demo/${feature.key}.mp4`} poster={`/demo/${feature.key}.jpg`} className="animate-[fadein_.35s_ease-out]" />
          : <PhoneChat key={active} messages={feature.chat} className="animate-[fadein_.35s_ease-out]" />}
      </div>
    </div>
  );
}
