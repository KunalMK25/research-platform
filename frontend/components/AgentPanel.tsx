import { motion } from "framer-motion";
import { BrainCircuit, Globe, CheckCircle, FileText, CheckCircle2 } from "lucide-react";

const agents = [
  { id: "planning", name: "Planner", icon: <BrainCircuit className="w-5 h-5" /> },
  { id: "researching", name: "Researcher & Verifier", icon: <Globe className="w-5 h-5" /> },
  { id: "synthesizing", name: "Synthesizer", icon: <FileText className="w-5 h-5" /> },
  { id: "reporting", name: "Reporter", icon: <CheckCircle className="w-5 h-5" /> },
];

export default function AgentPanel({ status }: { status: string }) {
  const currentIndex = agents.findIndex(a => a.id === status);
  const activeIndex = currentIndex === -1 && status === "completed" ? 4 : currentIndex;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 h-full flex flex-col">
      <h2 className="text-xl font-bold text-white mb-8">Agent Swarm Activity</h2>
      <div className="flex-1 flex flex-col justify-center gap-6">
        {agents.map((agent, index) => {
          const isDone = index < activeIndex;
          const isActive = index === activeIndex;

          return (
            <div key={agent.id} className={`flex items-center gap-4 p-4 rounded-xl transition ${isActive ? "bg-slate-800/80 border border-blue-500/30" : "bg-transparent"}`}>
              <div className={`p-3 rounded-full ${isDone ? "bg-green-500/20 text-green-400" : isActive ? "bg-blue-500/20 text-blue-400" : "bg-slate-800 text-slate-500"}`}>
                {isDone ? <CheckCircle2 className="w-5 h-5" /> : agent.icon}
              </div>
              <div className="flex-1">
                <div className={`font-medium ${isDone ? "text-slate-300" : isActive ? "text-blue-400" : "text-slate-500"}`}>
                  {agent.name}
                </div>
                <div className="text-xs text-slate-500 mt-1">
                  {isDone ? "Completed" : isActive ? "Working..." : "Pending"}
                </div>
              </div>
              {isActive && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: [0, 1, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                  className="w-2 h-2 rounded-full bg-blue-500"
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
