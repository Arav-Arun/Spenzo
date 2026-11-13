import { useEffect, useRef, useState } from 'react';
import Mascot from './Mascot';
import PhoneChat from './PhoneChat';

// Each feature, explained plainly, next to the exact conversation it creates.
const LOG_BUTTONS = ['↩️ Undo', '✏️ Edit', '📊 This month'];
const FEATURES = [
  {
    title: 'Log what you spend in seconds',
    pose: 'salute',
    body: 'Type it the way you’d text a friend, send a photo of the bill, or a voice note. Spenzo picks the category for you, and Undo is one tap away.',
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
    title: 'Split bills with friends',
    pose: 'split',
    body: 'Tell Spenzo who was there. It works out everyone’s share, keeps a running tab with each friend, and makes payment links you can forward.',
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
    title: 'Budgets that warn you early',
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
    title: 'Save up for what you want',
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
    title: 'Keep an eye on your investments',
    pose: 'grow',
    body: 'Send a screenshot of your Groww or Zerodha holdings. Spenzo tracks your stocks, mutual funds and crypto at live prices. Facts only, never tips.',
    chat: [
      { me: true, photo: 'holdings', time: '19:10' },
      { text: '📈 Added 4 holdings: TCS, Reliance, Parag Parikh Flexi Cap and Nifty 50 Index.', time: '19:10' },
      { me: true, text: 'how are my investments doing?', time: '19:11' },
      { text: 'Worth ₹1,48,230 right now, up ₹12,380 (9.1%) on what you paid.\nTCS is 38% of your portfolio.', time: '19:11' },
    ],
  },
  {
    title: 'Ask anything about your money',
    pose: 'thinking',
    body: 'Where did it go? Can you afford it? Spenzo answers from your real numbers, in English, Hinglish or Hindi, whichever you use.',
    chat: [
      { me: true, text: 'where did my money go this month?', time: '22:01' },
      { text: '📊 November so far: ₹26,530\nRent ₹18,000 · Food ₹4,930 · Shopping ₹2,600 · Transport ₹1,000', time: '22:01' },
      { me: true, text: 'kya main 40k ka phone le sakta hoon?', time: '22:03' },
      { text: 'Abhi thoda tight hai. Har mahine ~₹31k kharcha hota hai. ₹10k mahina bachao aur March tak phone tumhara 🎯', time: '22:03' },
    ],
  },
  {
    title: 'See everything on your dashboard',
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

  return (
    <div ref={box} onMouseEnter={() => setHovering(true)} onMouseLeave={() => setHovering(false)}
      className="grid items-start gap-10 lg:grid-cols-[1fr_auto] lg:gap-16">
      <ol className="space-y-2.5" role="tablist" aria-label="Features">
        {FEATURES.map((f, i) => {
          const on = i === active;
          return (
            <li key={f.title}>
              <button role="tab" aria-selected={on} onClick={() => setActive(i)}
                className={`relative flex w-full items-center gap-4 overflow-hidden rounded-2xl border p-4 text-left transition-colors sm:p-5 ${on ? 'border-leaf bg-card' : 'border-transparent hover:border-line hover:bg-card/60'}`}>
                <Mascot pose={f.pose} title="" className={`shrink-0 transition-all ${on ? 'h-16 w-16' : 'h-12 w-12 opacity-80 grayscale-[35%]'}`} />
                <span className="min-w-0">
                  <span className={`block text-lg font-bold ${on ? 'text-ink' : 'text-ink/70'}`}>{f.title}</span>
                  {on && <span className="mt-1 block leading-relaxed text-muted">{f.body}</span>}
                </span>
                {on && rotating && (   /* restarts with the timer whenever rotation resumes */
                  <span aria-hidden="true" className="absolute bottom-0 left-0 h-[3px] w-full origin-left bg-leaf"
                    style={{ animation: `progress ${SECONDS}s linear forwards` }} />
                )}
              </button>
            </li>
          );
        })}
      </ol>
      <div className="relative isolate mx-auto w-fit lg:sticky lg:top-28">
        <PhoneChat key={active} messages={FEATURES[active].chat} className="animate-[fadein_.35s_ease-out]" />
      </div>
    </div>
  );
}
