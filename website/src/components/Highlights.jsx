import { Camera, ChartColumn, CheckCheck, FileText, Gift, IndianRupee, Languages, Mic, Siren, Target, TrendingUp, Users } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { NAME } from '../brand';

// The main features, each with a screenshot from Spenzo's real WhatsApp number cropped to the
// message and the reply (assets/web/highlights). `at` picks which part shows when the shot is
// taller than its frame.
const SHOWN = [
  { icon: CheckCheck, title: 'Log a spend in a second', body: 'Type “chai 20”. After your first few, Spenzo just ticks it. Say “undo” to take one back.', shot: 'ticks', at: 'object-bottom' },
  { icon: FileText, title: 'Forward your bank statement', body: 'The whole month in one go. Locked PDFs ask for the password, which is used once and never kept.', shot: 'statement', at: 'object-bottom' },
  { icon: Camera, title: 'Snap the bill', body: 'A photo of a bill or a payment screenshot is read and logged with the right category.', shot: 'bill', at: 'object-bottom' },
  { icon: Users, title: 'Split with friends', body: 'Your share is logged and everyone else’s is tracked, so “who owes me?” always has an answer.', shot: 'split', at: 'object-bottom' },
  { icon: Target, title: 'Goals that cheer you on', body: 'Say what you’re saving for and by when. Baaz sends a sticker halfway, and celebrates at the finish.', shot: 'goal', at: 'object-center' },
  { icon: Gift, title: 'Your month, Wrapped', body: 'Early each month: your top spot, your usual, your biggest day, made to share.', shot: 'wrapped', at: 'object-top' },
];

// Smaller features: icon and text only.
const ALSO = [
  { icon: Siren, title: 'Budgets that warn you early', body: '“Keep food under 6k”: a heads-up at 80%, when you’re over, and if you’re spending too fast.' },
  { icon: ChartColumn, title: 'Charts on request', body: '“Swiggy this year vs last” comes back as a picture, with the numbers that matter.' },
  { icon: TrendingUp, title: 'Investments at live prices', body: 'Send your Groww or Zerodha holdings screenshot, or your mutual fund statement. Facts only, never tips.' },
  { icon: IndianRupee, title: 'Pay links for friends', body: 'Share your UPI ID once and every “who owes me?” comes with a tap-to-pay link to forward.' },
  { icon: Languages, title: 'English, Hinglish or Hindi', body: '“kitna kharcha hua is mahine?” works just as well as “where did my money go?”' },
  { icon: Mic, title: 'Voice notes too', body: 'Hold the mic and say “paid 450 for electricity”. Spenzo hears it and logs it.' },
];

// Fade in as it scrolls into view (once), unless the visitor prefers less motion.
function useReveal() {
  const ref = useRef(null);
  const [shown, setShown] = useState(() => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false);
  useEffect(() => {
    if (shown) return;
    const io = new IntersectionObserver(([e]) => e.isIntersecting && setShown(true), { threshold: 0.15 });
    io.observe(ref.current);
    return () => io.disconnect();
  }, [shown]);
  return [ref, shown];
}

function Reveal({ index, children }) {
  const [ref, shown] = useReveal();
  return (
    <div ref={ref} style={{ transitionDelay: `${(index % 3) * 90}ms` }}
      className={`h-full transition duration-700 ease-out ${shown ? 'translate-y-0 opacity-100' : 'translate-y-6 opacity-0'}`}>
      {children}
    </div>
  );
}

function Heading({ icon, title, body, small }) {
  const Icon = icon;
  return (
    <div className="flex gap-4">
      <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-leaf-soft text-leaf-deep"><Icon size={20} strokeWidth={2.2} /></span>
      <div className="min-w-0">
        <h3 className={`${small ? 'text-base' : 'text-lg'} leading-snug font-bold`}>{title}</h3>
        <p className="mt-1.5 leading-relaxed text-muted">{body}</p>
      </div>
    </div>
  );
}

const LIFT = 'transition duration-300 hover:-translate-y-1 hover:shadow-[0_24px_48px_-28px_rgba(14,42,31,0.35)]';

export default function Highlights() {
  return (
    <>
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {SHOWN.map((c, i) => (
          <Reveal key={c.title} index={i}>
            <article className={`flex h-full flex-col overflow-hidden rounded-xl border border-line bg-card ${LIFT}`}>
              <div className="flex-1 p-6"><Heading {...c} /></div>
              <div className="mx-3 mb-3 h-80 overflow-hidden rounded-lg border border-line/70 bg-[#EFEAE2]">
                <img src={`/highlights/${c.shot}.webp`} alt={`${c.title}: a real ${NAME} chat`} loading="lazy" decoding="async"
                  className={`h-full w-full object-cover ${c.at}`} />
              </div>
            </article>
          </Reveal>
        ))}
      </div>

      <div className="mt-5 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {ALSO.map((c, i) => (
          <Reveal key={c.title} index={i}>
            <article className={`h-full rounded-xl border border-line bg-card p-6 ${LIFT}`}><Heading small {...c} /></article>
          </Reveal>
        ))}
      </div>
    </>
  );
}
