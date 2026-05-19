"use client";

import Link from 'next/link';
import { Brain } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="border-b border-slate-800 bg-slate-950/70 backdrop-blur-md sticky top-0 z-50 transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 hover:opacity-90 transition group">
          <div className="relative">
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg blur opacity-40 group-hover:opacity-75 transition duration-300"></div>
            <div className="relative bg-slate-900 border border-slate-800 p-1.5 rounded-lg text-indigo-400">
              <Brain className="w-5 h-5" />
            </div>
          </div>
          <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-white via-indigo-100 to-indigo-300 bg-clip-text text-transparent">
            Verity <span className="text-indigo-400 font-medium">AI</span>
          </span>
        </Link>
        <div className="flex gap-6 items-center text-sm font-medium">
          <Link href="/history" className="text-slate-300 hover:text-white transition">History</Link>
        </div>
      </div>
    </nav>
  );
}
