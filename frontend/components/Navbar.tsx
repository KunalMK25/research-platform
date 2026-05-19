import Link from 'next/link';
import { Beaker } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition">
          <Beaker className="w-6 h-6 text-blue-400" />
          <span className="font-bold text-xl tracking-tight text-slate-100">Agentic<span className="text-blue-500">Research</span></span>
        </Link>
        <div className="flex gap-6 items-center text-sm font-medium text-slate-300">
          <Link href="/history" className="hover:text-white transition">History</Link>
          <button className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-full transition">Sign In</button>
        </div>
      </div>
    </nav>
  );
}
