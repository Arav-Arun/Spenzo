import { NAME } from '../brand';
import Mascot from './Mascot';

// An iPhone with Spenzo's WhatsApp chat on screen, buttons and all, as it really looks.
const Icon = {
  back: <path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />,
  video: <path d="M3 7.5A2.5 2.5 0 0 1 5.5 5h8A2.5 2.5 0 0 1 16 7.5v9a2.5 2.5 0 0 1-2.5 2.5h-8A2.5 2.5 0 0 1 3 16.5zM16 10l5-3v10l-5-3z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />,
  phone: <path d="M6.6 3.5l2.7.4 1.3 4-1.9 1.5a12 12 0 0 0 5.9 5.9l1.5-1.9 4 1.3.4 2.7a2 2 0 0 1-2 2.1A17 17 0 0 1 4.5 5.5a2 2 0 0 1 2.1-2z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />,
  plus: <path d="M12 5v14M5 12h14" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />,
  camera: <path d="M4 8.5A2.5 2.5 0 0 1 6.5 6h1.8l1.4-2h4.6l1.4 2h1.8A2.5 2.5 0 0 1 20 8.5v8a2.5 2.5 0 0 1-2.5 2.5h-11A2.5 2.5 0 0 1 4 16.5zM12 16a3.2 3.2 0 1 0 0-6.4 3.2 3.2 0 0 0 0 6.4z" fill="none" stroke="currentColor" strokeWidth="1.8" />,
  mic: <path d="M12 3a3 3 0 0 1 3 3v6a3 3 0 0 1-6 0V6a3 3 0 0 1 3-3zM6 11a6 6 0 0 0 12 0M12 17v3" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />,
};
const Svg = ({ name, className = 'h-5 w-5' }) => <svg viewBox="0 0 24 24" className={className} aria-hidden="true">{Icon[name]}</svg>;

// Like a real iPhone: the time centred in the left "ear", icons in the right, the island between.
function StatusBar() {
  return (
    <div className="grid h-11 shrink-0 grid-cols-[1fr_88px_1fr] items-center pt-1 text-[14px] font-semibold text-black">
      <span className="text-center tabular">9:41</span>
      <span className="h-[25px] rounded-full bg-black" />
      <span className="flex items-center justify-center gap-[5px]" aria-hidden="true">
        <svg viewBox="0 0 17 11" className="h-[11px] w-[17px]">
          <g fill="currentColor"><rect x="0" y="7" width="3" height="4" rx=".9" /><rect x="4.6" y="5" width="3" height="6" rx=".9" /><rect x="9.2" y="2.6" width="3" height="8.4" rx=".9" /><rect x="13.8" y="0" width="3" height="11" rx=".9" /></g>
        </svg>
        <svg viewBox="0 0 16 12" className="h-[11px] w-[15px]">
          <g fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round"><path d="M1.6 4.6a9.3 9.3 0 0 1 12.8 0" /><path d="M4.2 7.4a5.6 5.6 0 0 1 7.6 0" /></g>
          <circle cx="8" cy="10.2" r="1.45" fill="currentColor" />
        </svg>
        <svg viewBox="0 0 27 13" className="h-[12px] w-[25px]">
          <rect x=".5" y=".5" width="23" height="12" rx="3.6" fill="none" stroke="currentColor" opacity=".35" />
          <rect x="2.2" y="2.2" width="19.6" height="8.6" rx="2.2" fill="currentColor" />
          <path d="M25 4.6v3.8a2 2 0 0 0 0-3.8z" fill="currentColor" opacity=".4" />
        </svg>
      </span>
    </div>
  );
}

function Bubble({ m }) {
  const meta = (
    <span className="float-right mt-1.5 ml-2 flex items-center gap-0.5 text-[10.5px] leading-none text-black/45">
      {m.time || '9:41'}
      {m.me && <svg viewBox="0 0 16 11" className="h-[11px] w-[15px] text-[#53BDEB]" aria-label="read"><path d="M1 6l3 3 6-7M6 9l1 1 6-8" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" /></svg>}
    </span>
  );
  const shadow = 'shadow-[0_1px_0.5px_rgba(0,0,0,0.13)]';
  if (m.me) {
    return (
      <div className={`flow-root max-w-[82%] self-end rounded-lg rounded-tr-[3px] bg-[#D9FDD3] px-2.5 py-1.5 ${shadow}`}>
        {m.text}{meta}
      </div>
    );
  }
  const extras = m.buttons?.length;
  return (
    <div className="max-w-[86%] self-start">
      <div className={`flow-root bg-white px-2.5 py-1.5 whitespace-pre-line ${shadow} ${extras ? 'rounded-t-lg rounded-tl-[3px]' : 'rounded-lg rounded-tl-[3px]'}`}>
        {m.text}{meta}
      </div>
      {extras && (
        <div className="mt-px flex flex-col gap-px">
          {m.buttons.map((b, i, all) => (
            <span key={b} className={`flex items-center justify-center bg-white py-2 text-[13px] font-medium text-[#027EB5] ${shadow} ${i === all.length - 1 ? 'rounded-b-lg' : ''}`}>
              {b}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

// The iPhone itself.
function PhoneFrame({ children, className = '' }) {
  const side = 'absolute w-[3px] bg-[#3a3a3c]';
  return (
    <div className={`relative w-[300px] sm:w-[322px] ${className}`}>
      {/* side buttons: action, volume up/down on the left, power on the right */}
      <span className={`${side} top-[104px] -left-[2px] h-7 rounded-l-sm`} />
      <span className={`${side} top-[148px] -left-[2px] h-12 rounded-l-sm`} />
      <span className={`${side} top-[206px] -left-[2px] h-12 rounded-l-sm`} />
      <span className={`${side} top-[172px] -right-[2px] h-[72px] rounded-r-sm`} />

      <div className="rounded-[3.1rem] bg-gradient-to-b from-[#3a3a3c] to-[#1c1c1e] p-[3px] shadow-[0_0_0_1px_rgba(0,0,0,0.4)]">
        <div className="rounded-[2.95rem] bg-black p-[9px]">
          <div className="aspect-[9/19.5] overflow-hidden rounded-[2.4rem] bg-[#EFEAE2]">{children}</div>
        </div>
      </div>
    </div>
  );
}

// A real screenshot on the phone's screen, under the status bar.
export function PhoneShot({ src, alt, className = '' }) {
  return (
    <PhoneFrame className={className}>
      <div className="flex h-full flex-col bg-white">
        <StatusBar />
        <img src={src} alt={alt} decoding="async" className="block min-h-0 w-full flex-1 object-cover object-top" />
      </div>
    </PhoneFrame>
  );
}

export default function PhoneChat({ messages, className = '' }) {
  return (
    <PhoneFrame className={className}>
      <div className="flex h-full flex-col text-[13.5px] leading-snug text-[#111b21]">
        <div className="bg-[#F7F8FA]"><StatusBar /></div>

        <div className="flex shrink-0 items-center gap-2 border-b border-black/10 bg-[#F7F8FA] px-2 pb-2">
          <Svg name="back" className="h-6 w-6 text-[#007AFF]" />
          <div className="h-9 w-9 shrink-0 overflow-hidden rounded-full"><Mascot pose="avatar" className="h-full w-full object-cover" /></div>
          <div className="min-w-0 flex-1 leading-tight">
            <div className="truncate text-[15px] font-semibold">{NAME}</div>
            <div className="text-[11.5px] text-black/50">online</div>
          </div>
          <Svg name="video" className="h-6 w-6 text-[#007AFF]" />
          <Svg name="phone" className="mr-1 ml-3 h-5 w-5 text-[#007AFF]" />
        </div>

        <div className="flex min-h-0 flex-1 flex-col justify-end gap-1.5 overflow-hidden px-2.5 py-3"
          style={{ backgroundImage: 'radial-gradient(rgba(0,0,0,0.045) 1px, transparent 1.2px)', backgroundSize: '14px 14px' }}>
          <span className="mb-1 self-center rounded-md bg-white/90 px-2 py-0.5 text-[11px] text-black/55 shadow-sm">Today</span>
          {messages.map((m, i) => <Bubble key={i} m={m} />)}
        </div>

        <div className="shrink-0 bg-[#F7F8FA] px-2 pt-2 pb-1">
          <div className="flex items-center gap-2">
            <Svg name="plus" className="h-6 w-6 text-[#007AFF]" />
            <div className="h-8 flex-1 rounded-full border border-black/10 bg-white" />
            <Svg name="camera" className="h-6 w-6 text-[#007AFF]" />
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[#25D366] text-white"><Svg name="mic" className="h-[18px] w-[18px]" /></span>
          </div>
          <div className="mx-auto mt-2.5 mb-1 h-[5px] w-28 rounded-full bg-black" />
        </div>
      </div>
    </PhoneFrame>
  );
}
