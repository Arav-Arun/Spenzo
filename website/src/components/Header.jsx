import React from 'react';

export default function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 h-16 border-b border-white/10 flex items-center justify-between px-6 lg:px-10 z-[120] bg-black/80 backdrop-blur-md">
      <a href="/" className="flex items-center gap-2 group">
        <img src="/spenzo-logo.png" alt="Spenzo Logo" className="h-8 w-auto group-hover:scale-105 transition-transform duration-300" />
        <span className="font-semibold tracking-tight text-lg">Spenzo</span>
      </a>
    </header>
  );
}
