"use client";

import { useEffect, useState } from "react";
import { getHistory } from "@/lib/api";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { 
  Clock, 
  ArrowRight, 
  Calendar, 
  Activity, 
  AlertCircle, 
  CheckCircle2, 
  Compass, 
  Loader2,
  Plus
} from "lucide-react";

interface ResearchSession {
  id: string;
  topic: string;
  depth: string;
  status: string;
  created_at: string;
}

export default function HistoryPage() {
  const router = useRouter();
  const [history, setHistory] = useState<ResearchSession[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    getHistory("anonymous")
      .then((data) => {
        setHistory(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch research history", err);
        setLoading(false);
      });
  }, []);

  // Format date helper
  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString(undefined, { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    } catch {
      return "Recent";
    }
  };

  // Helper to determine status style properties
  const getStatusStyle = (status: string) => {
    const s = status.toLowerCase();
    if (s === "completed") {
      return {
        bg: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
        icon: <CheckCircle2 className="w-3.5 h-3.5" />,
        label: "Completed"
      };
    } else if (s === "failed") {
      return {
        bg: "bg-red-500/10 text-red-400 border-red-500/20",
        icon: <AlertCircle className="w-3.5 h-3.5" />,
        label: "Failed"
      };
    } else if (s === "pending") {
      return {
        bg: "bg-slate-800/80 text-slate-400 border-slate-700",
        icon: <Clock className="w-3.5 h-3.5" />,
        label: "Pending"
      };
    } else {
      // Any active running step (planning, researching, verifying, synthesizing, reporting, running)
      return {
        bg: "bg-blue-500/10 text-blue-400 border-blue-500/20 animate-pulse",
        icon: <Activity className="w-3.5 h-3.5" />,
        label: status.charAt(0).toUpperCase() + status.slice(1)
      };
    }
  };

  // Helper to determine depth styles
  const getDepthStyle = (depth: string) => {
    const d = depth.toLowerCase();
    if (d === "deep") {
      return "bg-indigo-500/15 text-indigo-400 border border-indigo-500/20";
    } else if (d === "standard") {
      return "bg-cyan-500/15 text-cyan-400 border border-cyan-500/20";
    } else {
      return "bg-slate-800 text-slate-300 border border-slate-700";
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <div className="min-h-screen py-10 max-w-6xl mx-auto px-4">
      {/* Header section */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 mb-10">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white mb-2 bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
            Research History
          </h1>
          <p className="text-slate-400 text-sm">
            Access and manage your past autonomous investigation swarms.
          </p>
        </div>
        
        {/* Create new research brief */}
        <button
          onClick={() => router.push("/")}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2.5 rounded-xl text-sm font-semibold transition shadow-lg shadow-indigo-600/10 hover:shadow-indigo-500/20"
        >
          <Plus className="w-4 h-4" />
          <span>New Swarm</span>
        </button>
      </div>

      {/* Loading Container */}
      {loading ? (
        <div className="flex flex-col items-center justify-center h-[50vh] gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
          <span className="text-sm text-slate-500">Retrieving research archives...</span>
        </div>
      ) : history.length === 0 ? (
        /* Empty State */
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-slate-900/60 border border-slate-800/80 rounded-3xl p-12 text-center shadow-xl max-w-md mx-auto mt-16"
        >
          <div className="w-14 h-14 rounded-full bg-slate-950 border border-slate-800 flex items-center justify-center text-slate-500 mx-auto mb-6">
            <Compass className="w-7 h-7 opacity-75" />
          </div>
          <h3 className="text-lg font-bold text-slate-200 mb-2">No Research Logged</h3>
          <p className="text-sm text-slate-400 leading-relaxed mb-6">
            No research sessions yet. Start your first research above.
          </p>
          <button
            onClick={() => router.push("/")}
            className="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-5 py-2.5 rounded-xl text-sm font-semibold transition"
          >
            <span>Begin Investigation</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </motion.div>
      ) : (
        /* Swarm History Cards Grid */
        <motion.div 
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {history.map((session) => {
            const statusStyle = getStatusStyle(session.status);
            const depthStyle = getDepthStyle(session.depth);
            
            return (
              <motion.div
                key={session.id}
                variants={itemVariants}
                onClick={() => router.push(`/research/${session.id}`)}
                className="group bg-slate-900/40 hover:bg-slate-900/80 border border-slate-800/80 hover:border-slate-700/80 rounded-2xl p-6 cursor-pointer shadow-lg hover:shadow-indigo-500/[0.02] flex flex-col justify-between h-[180px] transition-all duration-300"
              >
                {/* Top Section */}
                <div>
                  <div className="flex items-center justify-between gap-3 mb-3">
                    {/* Depth Badge */}
                    <span className={`text-[10px] font-bold uppercase tracking-widest px-2.5 py-0.5 rounded-full ${depthStyle}`}>
                      {session.depth}
                    </span>
                    
                    {/* Status Badge */}
                    <span className={`flex items-center gap-1 text-[10px] font-bold uppercase tracking-widest px-2.5 py-0.5 rounded-full border ${statusStyle.bg}`}>
                      {statusStyle.icon}
                      <span>{statusStyle.label}</span>
                    </span>
                  </div>
                  
                  {/* Topic Title */}
                  <h3 className="text-base font-bold text-slate-100 group-hover:text-indigo-400 transition-colors line-clamp-2 leading-snug">
                    {session.topic}
                  </h3>
                </div>

                {/* Bottom Section */}
                <div className="flex items-center justify-between border-t border-slate-800/50 pt-4 mt-auto">
                  <div className="flex items-center gap-1.5 text-xs text-slate-500">
                    <Calendar className="w-3.5 h-3.5 shrink-0" />
                    <span>{formatDate(session.created_at)}</span>
                  </div>
                  
                  <div className="text-slate-500 group-hover:text-indigo-400 transition-colors">
                    <ArrowRight className="w-4 h-4 translate-x-0 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      )}
    </div>
  );
}
