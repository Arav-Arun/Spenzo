import { NAME } from '../brand';

export default function Footer() {
  return (
    <footer className="border-t border-line">
      <div className="mx-auto flex max-w-6xl flex-col items-center gap-2 px-4 py-10 text-center text-sm text-muted">
        <a href="/privacy" className="font-medium text-ink/80 hover:text-ink">Privacy Policy</a>
        <p>Copyright © {NAME} {new Date().getFullYear()}</p>
        <p>Made by <a href="https://aravarun.in" target="_blank" rel="noreferrer" className="font-semibold text-leaf-deep hover:underline">Arav Arun</a></p>
      </div>
    </footer>
  );
}
