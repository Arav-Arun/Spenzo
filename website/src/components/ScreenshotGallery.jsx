import React, { useState, useCallback, useEffect } from 'react';

export default function ScreenshotGallery({ title, subtitle, images }) {
  const [index, setIndex] = useState(0);
  const [lightbox, setLightbox] = useState(null);

  const prev = useCallback(() => setIndex((i) => (i - 1 + images.length) % images.length), [images.length]);
  const next = useCallback(() => setIndex((i) => (i + 1) % images.length), [images.length]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (lightbox !== null) {
        if (e.key === 'Escape') setLightbox(null);
        if (e.key === 'ArrowRight') setLightbox(p => (p + 1) % images.length);
        if (e.key === 'ArrowLeft') setLightbox(p => (p - 1 + images.length) % images.length);
      } else {
        if (e.key === 'ArrowRight') next();
        if (e.key === 'ArrowLeft') prev();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [next, prev, lightbox, images.length]);

  return (
    <section className="py-16 md:py-24 px-4 md:px-6 z-10 relative border-t border-white/5 bg-black overflow-hidden">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-[1000px] h-[300px] bg-[#a7dd5d]/5 blur-[120px] pointer-events-none" />
      <div className="max-w-7xl mx-auto text-center mb-10 md:mb-16 relative z-10">
        <h2 className="text-2xl md:text-3xl font-bold tracking-tight mb-3 md:mb-4 text-white">{title}</h2>
        <p className="text-neutral-400 max-w-2xl mx-auto text-sm md:text-base">{subtitle}</p>
      </div>

      <div 
        className="relative w-full max-w-4xl mx-auto h-[50vh] sm:h-[60vh] min-h-[350px] flex items-center justify-center"
        style={{ perspective: '1200px' }}
      >
        {images.map((img, i) => {
          let offset = i - index;
          if (offset < -images.length / 2) offset += images.length;
          if (offset > images.length / 2) offset -= images.length;
          
          let style = {};
          if (offset === 0) {
            style = { transform: 'translateX(0) scale(1) rotateY(0deg)', zIndex: 30, opacity: 1 };
          } else if (offset === 1) {
            style = { transform: 'translateX(25%) scale(0.85) rotateY(-15deg)', zIndex: 20, opacity: 0.6 };
          } else if (offset === -1) {
            style = { transform: 'translateX(-25%) scale(0.85) rotateY(15deg)', zIndex: 20, opacity: 0.6 };
          } else if (offset === 2) {
            style = { transform: 'translateX(45%) scale(0.7) rotateY(-25deg)', zIndex: 10, opacity: 0.3 };
          } else if (offset === -2) {
            style = { transform: 'translateX(-45%) scale(0.7) rotateY(25deg)', zIndex: 10, opacity: 0.3 };
          } else {
            style = { transform: 'translateX(0) scale(0.5)', zIndex: 0, opacity: 0, pointerEvents: 'none' };
          }

          return (
            <div 
              key={i} 
              className="absolute w-[65%] sm:w-[50%] h-full flex items-center justify-center cursor-pointer transition-all duration-[600ms] ease-[cubic-bezier(0.25,1,0.5,1)]"
              style={style}
              onClick={() => {
                if (offset > 0) next();
                else if (offset < 0) prev();
                else setLightbox(i);
              }}
            >
              <img src={img} className="max-h-full max-w-full rounded-2xl border border-white/10 shadow-[0_20px_50px_rgba(0,0,0,0.5)] object-contain bg-[#050505]" alt="Screenshot" loading="lazy" />
            </div>
          )
        })}

        <button onClick={prev} className="absolute left-2 sm:-left-8 z-40 w-12 h-12 bg-white/5 border border-white/10 rounded-full flex items-center justify-center text-white hover:bg-[#a7dd5d] hover:text-black transition-colors backdrop-blur-md shadow-lg"><span className="text-xl font-bold -ml-1">‹</span></button>
        <button onClick={next} className="absolute right-2 sm:-right-8 z-40 w-12 h-12 bg-white/5 border border-white/10 rounded-full flex items-center justify-center text-white hover:bg-[#a7dd5d] hover:text-black transition-colors backdrop-blur-md shadow-lg"><span className="text-xl font-bold -mr-1">›</span></button>
      </div>

      <div className="text-center mt-8 text-xs font-mono text-neutral-500 uppercase tracking-widest relative z-10">
        {index + 1} / {images.length} · Tap lateral cards to rotate · Tap center to expand
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
    </section>
  );
}
