import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Verity AI | Autonomous Swarm Research Platform",
  description: "Deploy a swarm of specialized AI agents to plan, search, verify, and synthesize professional research reports with inline citations.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} min-h-screen bg-[#0f172a] text-slate-100 flex flex-col relative overflow-x-hidden`}>
        {/* CSS-only background dot pattern */}
        <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1.5px,transparent_1.5px)] [background-size:24px_24px] pointer-events-none z-0 opacity-60"></div>
        
        <div className="relative z-10 flex flex-col min-h-screen w-full">
          <Navbar />
          <main className="flex-1 max-w-7xl mx-auto w-full p-4 md:p-8 relative">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
