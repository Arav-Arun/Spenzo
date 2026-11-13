import { NAME } from '../brand';
import Mascot from '../components/Mascot';

// /pay?pa=name@bank&am=500.00&tn=dinner
// WhatsApp won't make upi:// links tappable, so Spenzo sends this page instead.
const UPI_ID = /^[\w.-]{2,256}@[A-Za-z]{2,64}$/;

export default function Pay() {
  const q = new URLSearchParams(window.location.search);
  const pa = q.get('pa') ?? '';
  const am = Number(q.get('am'));
  const tn = (q.get('tn') ?? '').slice(0, 50);
  const valid = UPI_ID.test(pa) && am > 0 && am < 1e7;
  // pa is validated, so it goes in raw: some UPI apps show "%40" and "+" literally.
  const upi = `upi://pay?pa=${pa}&am=${am.toFixed(2)}&cu=INR&tn=${encodeURIComponent(tn)}`;
  const qr = `https://api.qrserver.com/v1/create-qr-code/?size=240x240&margin=8&data=${encodeURIComponent(upi)}`;

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10 font-sans">
      <div className="w-full max-w-sm rounded-3xl border border-line bg-card p-8 text-center shadow-[0_20px_60px_rgba(14,42,31,0.08)]">
        <Mascot pose="pay" className="mx-auto mb-4 h-24 w-24" />
        {valid ? (
          <>
            <p className="text-sm text-muted">You&rsquo;re paying</p>
            <p className="mb-1 font-mono text-ink">{pa}</p>
            <p className="font-display text-5xl font-extrabold text-leaf-deep tabular">₹{am.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</p>
            {tn && <p className="mt-1 text-sm text-muted">for {tn}</p>}
            <a href={upi} className="mt-7 block rounded-full bg-leaf-deep py-4 font-semibold text-white hover:bg-ink">Pay with any UPI app</a>
            <p className="mt-6 mb-3 text-xs text-muted">On a computer? Scan with your phone:</p>
            <img src={qr} alt="UPI QR code for this payment" width="200" height="200" className="mx-auto rounded-xl border border-line" />
          </>
        ) : (
          <p className="text-muted">This payment link is incomplete. Ask whoever sent it for a new one.</p>
        )}
        <a href="/" className="mt-8 inline-block text-xs font-semibold text-muted hover:text-leaf-deep">Split bills with {NAME} on WhatsApp →</a>
      </div>
    </main>
  );
}
