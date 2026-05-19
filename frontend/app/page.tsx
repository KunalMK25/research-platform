import ResearchInput from "@/components/ResearchInput";
import { Sparkles, Zap, ShieldCheck } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center pt-20 pb-32">
      <div className="text-center max-w-3xl mb-12">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 text-sm font-medium mb-6">
          <Sparkles className="w-4 h-4" />
          <span>v2.0 Autonomous Engine</span>
        </div>
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
          Research anything. Instantly.
        </h1>
        <p className="text-lg md:text-xl text-slate-400 mb-8 max-w-2xl mx-auto">
          Deploy a swarm of specialized AI agents to plan, search, verify, and synthesize a complete, professional research report with citations.
        </p>
      </div>

      <div className="w-full max-w-4xl relative z-10">
        <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl blur opacity-20"></div>
        <div className="relative bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl">
          <ResearchInput />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mt-32">
        <FeatureCard 
          icon={<Zap className="w-6 h-6 text-amber-400" />}
          title="Lightning Fast"
          description="Parallel execution across multiple agents drastically reduces research time from days to minutes."
        />
        <FeatureCard 
          icon={<ShieldCheck className="w-6 h-6 text-green-400" />}
          title="Verified Claims"
          description="Every claim is fact-checked and strictly traced back to a credible, high-authority source."
        />
        <FeatureCard 
          icon={<Sparkles className="w-6 h-6 text-purple-400" />}
          title="Professional Output"
          description="Ready-to-use executive summaries, deep syntheses, and exportable PDFs or presentations."
        />
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl flex flex-col items-center text-center">
      <div className="bg-slate-800 p-3 rounded-xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-slate-200 mb-2">{title}</h3>
      <p className="text-sm text-slate-400 leading-relaxed">{description}</p>
    </div>
  );
}
