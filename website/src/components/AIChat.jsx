// An AI assistant using Spenzo. Set this to true once website/public/demo/ai.mp4 (a real recording
// of Claude or ChatGPT using Spenzo, with ai.jpg as its first frame) is in place.
const RECORDED = false;

export default function AIChat() {
  if (RECORDED) {
    return (
      <video src="/demo/ai.mp4" poster="/demo/ai.jpg" autoPlay muted loop playsInline preload="metadata"
        className="w-full max-w-xl rounded-2xl border border-white/10 shadow-[0_30px_80px_-30px_rgba(0,0,0,0.6)]" />
    );
  }
  return (
    <div className="w-full max-w-xl overflow-hidden rounded-2xl border border-white/10 bg-[#17211C] text-[14.5px] leading-relaxed text-paper shadow-[0_30px_80px_-30px_rgba(0,0,0,0.6)]">
      <div className="flex items-center gap-2 border-b border-white/10 px-4 py-3">
        <span className="h-3 w-3 rounded-full bg-[#ff5f57]" /><span className="h-3 w-3 rounded-full bg-[#febc2e]" /><span className="h-3 w-3 rounded-full bg-[#28c840]" />
        <span className="ml-3 text-sm text-paper/50">Your AI assistant</span>
      </div>
      <div className="space-y-4 p-5">
        <div className="ml-auto w-fit max-w-[85%] rounded-2xl rounded-br-md bg-white/10 px-4 py-2.5">
          Make me a plan to save ₹1 lakh by June. Use my Spenzo data.
        </div>
        <div className="flex flex-wrap gap-2 text-xs">
          {['summarize', 'budget_status', 'goals_status'].map((t) => (
            <span key={t} className="rounded-full border border-mango/40 bg-mango/10 px-2.5 py-1 font-medium text-mango">Spenzo · {t}</span>
          ))}
        </div>
        <div className="space-y-2 text-paper/85">
          <p>You spend about <b className="text-paper">₹31,300</b> a month and earn <b className="text-paper">₹60,000</b>, so you have roughly ₹28,700 left over.</p>
          <p>To reach ₹1,00,000 by June you need <b className="text-paper">₹14,300 a month</b>. That fits, with about ₹14,400 a month still spare. Trimming delivery from ₹4,200 to ₹2,500 would get you there a month early.</p>
          <p>Want me to set that up as a goal in Spenzo?</p>
        </div>
      </div>
    </div>
  );
}
