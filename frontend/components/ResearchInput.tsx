"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { startResearch } from "@/lib/api";
import { Loader2, Search } from "lucide-react";

export default function ResearchInput() {
  const [topic, setTopic] = useState("");
  const [depth, setDepth] = useState("Standard");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleStart = async () => {
    if (!topic.trim()) return;
    setLoading(true);
    try {
      const res = await startResearch(topic, depth);
      router.push(`/research/${res.session_id}`);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-8">
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-6 h-6 text-slate-500" />
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="e.g., The impact of quantum computing on cryptography..."
          className="w-full bg-slate-950 border border-slate-700 rounded-2xl py-5 pl-14 pr-6 text-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
          onKeyDown={(e) => e.key === 'Enter' && handleStart()}
        />
      </div>

      <div>
        <h3 className="text-sm font-medium text-slate-400 mb-4 uppercase tracking-wider">Select Depth</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {["Quick", "Standard", "Deep"].map((d) => (
            <button
              key={d}
              onClick={() => setDepth(d)}
              className={`p-4 rounded-xl border text-left transition-all ${
                depth === d 
                  ? "bg-blue-600/10 border-blue-500 ring-1 ring-blue-500" 
                  : "bg-slate-950 border-slate-800 hover:border-slate-600"
              }`}
            >
              <div className={`font-semibold mb-1 ${depth === d ? "text-blue-400" : "text-slate-300"}`}>{d}</div>
              <div className="text-xs text-slate-500">
                {d === "Quick" && "3 subtopics • Fast overview"}
                {d === "Standard" && "5 subtopics • Detailed analysis"}
                {d === "Deep" && "6+ subtopics • Academic rigor"}
              </div>
            </button>
          ))}
        </div>
      </div>

      <button
        onClick={handleStart}
        disabled={!topic.trim() || loading}
        className="w-full py-4 rounded-xl font-bold text-lg text-white bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(37,99,235,0.3)] hover:shadow-[0_0_30px_rgba(37,99,235,0.5)]"
      >
        {loading ? (
          <>
            <Loader2 className="w-6 h-6 animate-spin" />
            Initializing Agents...
          </>
        ) : (
          "Start Autonomous Research"
        )}
      </button>
    </div>
  );
}
