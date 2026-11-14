import { NAME, whatsappLink } from '../brand';
import { WhatsAppIcon } from './Icons';
import Mascot from './Mascot';

const LINKS = [['How it works', '/#how'], ['Features', '/#features'], ['FAQ', '/#faq']];

// A floating frosted-glass bar that rides over the page as you scroll.
export default function Header() {
  return (
    <header className="sticky top-3 z-50 px-3 sm:top-4 sm:px-6">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-4 rounded-full border border-white/70 bg-white/55 pr-2 pl-3 shadow-[0_10px_30px_-10px_rgba(14,42,31,0.18)] backdrop-blur-xl backdrop-saturate-150 sm:h-16 sm:pl-4">
        <a href="/" className="flex items-center gap-2">
          <Mascot pose="icon" className="h-8 w-8 sm:h-9 sm:w-9" title={`${NAME} home`} />
          <span className="font-display text-lg font-extrabold sm:text-xl">{NAME}</span>
        </a>
        <nav className="hidden items-center gap-7 text-[15px] font-semibold text-muted md:flex">
          {LINKS.map(([label, href]) => <a key={href} href={href} className="transition-colors hover:text-ink">{label}</a>)}
        </nav>
        <a href={whatsappLink('Hi')} target="_blank" rel="noreferrer"
          className="flex items-center gap-2 rounded-full bg-leaf-deep px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-ink sm:px-5">
          <WhatsAppIcon size={16} /> Say hi
        </a>
      </div>
    </header>
  );
}
