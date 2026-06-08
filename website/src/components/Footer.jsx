import React from 'react';

export default function Footer() {
  return (
    <footer className="py-8 text-center text-xs font-mono text-neutral-600 uppercase tracking-widest bg-[#0a0a0a] z-10 relative">
      SPENZO &copy; {new Date().getFullYear()} : Made by <a href="https://aravarun.xyz" target="_blank" rel="noreferrer" className="text-[#a7dd5d] hover:underline">Arav Arun</a>
    </footer>
  );
}
