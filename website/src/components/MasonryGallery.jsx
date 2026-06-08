import React, { useState, useEffect } from 'react';

export default function MasonryGallery({ title, subtitle, images, columnsClass = "columns-1 sm:columns-2 lg:columns-3" }) {
  const [lightbox, setLightbox] = useState(null);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (lightbox === null) return;
      if (e.key === 'Escape') setLightbox(null);
      if (e.key === 'ArrowRight') setLightbox(p => (p + 1) % images.length);
      if (e.key === 'ArrowLeft') setLightbox(p => (p - 1 + images.length) % images.length);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [lightbox, images.length]);

  return (
    <section className="py-16 md:py-24 px-4 md:px-6 z-10 relative border-t border-white/5 bg-black">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-[1000px] h-[300px] bg-[#a7dd5d]/5 blur-[120px] pointer-events-none" />
      <div className="max-w-7xl mx-auto relative z-10">
        <div className="text-center mb-10 md:mb-16">
          <h2 className="text-2xl md:text-3xl font-bold tracking-tight mb-3 md:mb-4 text-white">{title}</h2>
          <p className="text-neutral-400 max-w-2xl mx-auto text-sm md:text-base">{subtitle}</p>
        </div>
        <div className={`${columnsClass} gap-3 md:gap-4 space-y-3 md:space-y-4`}>
          {images.map((src, i) => (
            <div
              key={i}
              onClick={() => setLightbox(i)}
              className="break-inside-avoid cursor-zoom-in bg-[#050505] border border-white/10 rounded-xl overflow-hidden hover:border-[#a7dd5d]/50 hover:shadow-[0_0_30px_rgba(167,221,93,0.08)] active:scale-[0.98] transition-all duration-300 group"
            >
              <img src={src} className="w-full h-auto block group-hover:scale-[1.02] transition-transform duration-300" loading="lazy" />
            </div>
          ))}
        </div>

        {lightbox !== null && (
          <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-sm flex items-center justify-center p-2 md:p-4" onClick={() => setLightbox(null)}>
            <button className="absolute top-4 right-4 md:top-8 md:right-8 w-10 h-10 md:w-12 md:h-12 bg-white/10 border border-white/10 rounded-full flex items-center justify-center text-white hover:bg-white/30 transition-colors z-[110] text-xl font-light focus:outline-none" onClick={() => setLightbox(null)}>✕</button>
            <button onClick={e => { e.stopPropagation(); setLightbox(p => (p - 1 + images.length) % images.length); }} className="absolute left-2 md:left-4 top-1/2 -translate-y-1/2 w-10 h-10 md:w-12 md:h-12 rounded-full bg-white/15 hover:bg-[#a7dd5d] hover:text-black transition-colors text-2xl font-bold z-[110] focus:outline-none">‹</button>
            <img src={images[lightbox]} alt="Expanded" className="max-h-[88vh] max-w-[88vw] md:max-h-[90vh] md:max-w-[90vw] rounded-xl shadow-2xl border border-white/10 object-contain" onClick={e => e.stopPropagation()} />
            <button onClick={e => { e.stopPropagation(); setLightbox(p => (p + 1) % images.length); }} className="absolute right-2 md:right-4 top-1/2 -translate-y-1/2 w-10 h-10 md:w-12 md:h-12 rounded-full bg-white/15 hover:bg-[#a7dd5d] hover:text-black transition-colors text-2xl font-bold z-[110] focus:outline-none">›</button>
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-xs font-mono text-neutral-400 uppercase tracking-widest">{lightbox + 1} / {images.length}</div>
          </div>
        )}
      </div>
    </section>
  );
}
