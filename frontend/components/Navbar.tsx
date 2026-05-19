"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Brain, LogOut, LogIn } from 'lucide-react';
import { auth } from '@/lib/firebase';
import { 
  signInWithPopup, 
  GoogleAuthProvider, 
  signOut, 
  onAuthStateChanged, 
  User 
} from 'firebase/auth';

export default function Navbar() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  const handleSignIn = async () => {
    const provider = new GoogleAuthProvider();
    try {
      await signInWithPopup(auth, provider);
    } catch (err) {
      console.error("Firebase Sign In Error", err);
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut(auth);
    } catch (err) {
      console.error("Firebase Sign Out Error", err);
    }
  };

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
          
          {!loading && (
            user ? (
              <div className="flex items-center gap-3">
                {user.photoURL && (
                  <img src={user.photoURL} alt="Avatar" className="w-7 h-7 rounded-full border border-indigo-500/30" />
                )}
                <span className="text-slate-300 text-xs hidden md:inline">{user.displayName || "User"}</span>
                <button 
                  onClick={handleSignOut}
                  className="flex items-center gap-1.5 bg-slate-900 border border-slate-850 hover:bg-slate-800 text-slate-300 px-4 py-2 rounded-xl transition text-xs font-semibold"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span>Logout</span>
                </button>
              </div>
            ) : (
              <button 
                onClick={handleSignIn}
                className="flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-xl transition text-xs font-semibold shadow-lg shadow-indigo-600/10 hover:shadow-indigo-500/20"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>Sign In</span>
              </button>
            )
          )}
        </div>
      </div>
    </nav>
  );
}
