import ResearchInput from "@/components/ResearchInput";
import { Sparkles, Zap, ShieldCheck } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center pt-16 pb-28">
      <div className="text-center max-w-3xl mb-12 flex flex-col items-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 text-sm font-medium mb-6">
          <Sparkles className="w-4 h-4" />
          <span>v2.0 Autonomous Engine</span>
        </div>
        
        {/* Hero Title */}
        <h1 className="text-6xl md:text-8xl font-extrabold tracking-tight mb-4 bg-gradient-to-b from-white via-slate-100 to-slate-350 bg-clip-text text-transparent">
          Verity AI
        </h1>
        
        {/* Subtitle */}
        <p className="text-lg md:text-xl text-slate-300 mb-6 max-w-xl mx-auto font-medium">
          Research anything. Trust everything.
        </p>
        
        {/* Small Indigo Badge */}
        <div className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-bold uppercase tracking-widest mb-10">
          <span>Multi-Agent Research Platform</span>
        </div>
      </div>

      {/* Main Search Swarm Form Area */}
      <div className="w-full max-w-4xl relative z-10">
        <div className="absolute -inset-1.5 bg-gradient-to-r from-indigo-500 to-blue-500 rounded-3xl blur opacity-25 animate-pulse"></div>
        <div className="relative bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl">
          <ResearchInput />
        </div>
      </div>

      {/* Dynamic Swarm Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mt-32">
        <FeatureCard 
          icon={<Zap className="w-6 h-6 text-indigo-400" />}
          title="Lightning Fast"
          description="Parallel execution across multiple specialized agents drastically reduces research time from days to seconds."
        />
        <FeatureCard 
          icon={<ShieldCheck className="w-6 h-6 text-emerald-400" />}
          title="Verified Claims"
          description="Every finding is cross-checked for conflicts and strictly verified back to a credible, high-authority domain."
        />
        <FeatureCard 
          icon={<Sparkles className="w-6 h-6 text-purple-400" />}
          title="Swarm Summaries"
          description="Generates executive summaries, synthesized subtopics with domain citations, and download-ready PDF & PPT decks."
        />
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="bg-slate-900/40 border border-slate-850/80 p-6 rounded-2xl flex flex-col items-center text-center backdrop-blur-sm">
      <div className="bg-slate-800/60 border border-slate-700/40 p-3 rounded-xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-slate-200 mb-2">{title}</h3>
      <p className="text-sm text-slate-400 leading-relaxed">{description}</p>
    </div>
  );
}
