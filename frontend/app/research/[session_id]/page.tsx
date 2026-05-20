"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getResearchStatus, getReport } from "@/lib/api";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import { 
  Loader2, 
  CheckCircle2, 
  Circle, 
  ArrowRight, 
  Download, 
  FileText, 
  Presentation, 
  AlertTriangle, 
  Clock, 
  BookOpen, 
  Layers
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface SubTopic {
  id: string;
  title: string;
  status: string;
}

interface ProgressEvent {
  step: string;
  agent: string;
  message: string;
  detail: string;
  timestamp: string;
}

export default function ResearchSessionPage() {
  const params = useParams();
  const sessionId = params?.session_id as string;

  const [overallStatus, setOverallStatus] = useState<string>("planning");
  const [subtopics, setSubtopics] = useState<SubTopic[]>([]);
  const [latestEvent, setLatestEvent] = useState<ProgressEvent | null>(null);
  const [report, setReport] = useState<{ markdown: string; metrics: any } | null>(null);
  const [downloading, setDownloading] = useState<'pdf' | 'ppt' | null>(null);

  // Steps matching the 5 Agents
  const steps = [
    { id: "planning", label: "Planner", desc: "Formulates subtopics" },
    { id: "researching", label: "Researcher", desc: "Gathers web & arXiv data" },
    { id: "verifying", label: "Verifier", desc: "Fact-checks & scores credibility" },
    { id: "synthesizing", label: "Synthesizer", desc: "Drafts deep summaries" },
    { id: "reporting", label: "Reporter", desc: "Assembles structured briefing" }
  ];

  // Helper to query report contents on completion
  const fetchReportData = async () => {
    try {
      const data = await getReport(sessionId);
      setReport(data);
    } catch (err) {
      console.error("Failed to load report", err);
    }
  };

  // 1. Initial Status Check
  useEffect(() => {
    if (!sessionId) return;
    
    const fetchStatus = async () => {
      try {
        const statusData = await getResearchStatus(sessionId);
        setOverallStatus(statusData.status);
        setSubtopics(statusData.subtopics || []);
        if (statusData.progress) {
          setLatestEvent(statusData.progress);
        }
        if (statusData.status === "completed") {
          fetchReportData();
        }
      } catch (err) {
        console.error("Error retrieving initial status", err);
      }
    };
    
    fetchStatus();
  }, [sessionId]);

  // 2. Establish Server-Sent Events (SSE) Stream
  useEffect(() => {
    if (!sessionId || overallStatus === "completed" || overallStatus === "failed") return;

    const eventSource = new EventSource(`${API_URL}/research/${sessionId}/stream`);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.step === "done") {
          setOverallStatus("completed");
          fetchReportData();
          eventSource.close();
        } else if (data.step === "failed") {
          setOverallStatus("failed");
          setLatestEvent(data);
          eventSource.close();
        } else {
          setLatestEvent(data);
          if (data.step) {
            setOverallStatus(data.step);
          }
          // Fetch subtopics on status updates to show planning completion
          getResearchStatus(sessionId).then((statusData) => {
            setSubtopics(statusData.subtopics || []);
          });
        }
      } catch (err) {
        console.error("SSE parse error", err);
      }
    };

    eventSource.onerror = (err) => {
      console.error("SSE connection dropped", err);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [sessionId]);

  // Helper to determine the state of a step
  const getStepState = (stepId: string) => {
    const order = ["planning", "researching", "verifying", "synthesizing", "reporting", "completed"];
    const currentIndex = order.indexOf(overallStatus);
    const stepIndex = order.indexOf(stepId);

    if (overallStatus === "failed") {
      return "waiting";
    }
    if (currentIndex > stepIndex) {
      return "done";
    } else if (currentIndex === stepIndex) {
      return "active";
    } else {
      return "waiting";
    }
  };

  // File Download Handler
  const handleDownload = async (type: 'pdf' | 'ppt') => {
    setDownloading(type);
    try {
      const res = await fetch(`${API_URL}/export/${type}/${sessionId}`, {
        method: "POST"
      });
      if (!res.ok) throw new Error("Failed to compile export file");
      
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = type === 'pdf' ? `report_${sessionId}.pdf` : `presentation_${sessionId}.pptx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert(`Could not download ${type.toUpperCase()}. Please try again.`);
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div className="min-h-screen py-10 max-w-5xl mx-auto px-4">
      <AnimatePresence mode="wait">
        
        {/* CASE 1: ACTIVE RESEARCH PROCESS TIMELINE */}
        {overallStatus !== "completed" && overallStatus !== "failed" && (
          <motion.div 
            key="timeline"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            className="flex flex-col items-center"
          >
            <div className="text-center max-w-2xl mb-12">
              <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent mb-4">
                Research swarm at work...
              </h1>
              <p className="text-slate-400 leading-relaxed">
                Specialized AI agents are operating sequentially to investigate, fact-check, and synthesize a polished research dossier for you.
              </p>
            </div>

            {/* Swarm Timeline Grid */}
            <div className="w-full max-w-3xl bg-slate-900/60 border border-slate-800/80 rounded-3xl p-8 shadow-2xl relative">
              <div className="grid grid-cols-1 md:grid-cols-5 gap-6 relative z-10">
                {steps.map((s, idx) => {
                  const state = getStepState(s.id);
                  return (
                    <div key={s.id} className="flex flex-col items-center text-center relative">
                      {/* Connection Line */}
                      {idx < steps.length - 1 && (
                        <div className="hidden md:block absolute top-6 left-[60%] right-[-40%] h-0.5 bg-slate-800 z-0">
                          {state === "done" && (
                            <motion.div 
                              className="h-full bg-indigo-500" 
                              initial={{ width: 0 }}
                              animate={{ width: "100%" }}
                              transition={{ duration: 0.5 }}
                            />
                          )}
                        </div>
                      )}

                      {/* Icon Bubble */}
                      <div className="relative z-10 mb-4">
                        {state === "done" ? (
                          <motion.div 
                            initial={{ scale: 0.8 }} 
                            animate={{ scale: 1 }}
                            className="w-12 h-12 rounded-full bg-emerald-500/25 border-2 border-emerald-500 flex items-center justify-center text-emerald-400 shadow-lg shadow-emerald-500/20"
                          >
                            <CheckCircle2 className="w-6 h-6" />
                          </motion.div>
                        ) : state === "active" ? (
                          <motion.div 
                            className="w-12 h-12 rounded-full bg-indigo-500/20 border-2 border-indigo-500 flex items-center justify-center text-indigo-400 shadow-xl shadow-indigo-500/30"
                            animate={{ scale: [1, 1.1, 1] }}
                            transition={{ repeat: Infinity, duration: 1.8, ease: "easeInOut" }}
                          >
                            <Loader2 className="w-6 h-6 animate-spin" />
                          </motion.div>
                        ) : (
                          <div className="w-12 h-12 rounded-full bg-slate-950 border border-slate-800 flex items-center justify-center text-slate-500">
                            <Circle className="w-4 h-4" />
                          </div>
                        )}
                      </div>

                      <h3 className={`font-semibold text-sm ${state === 'active' ? 'text-indigo-400' : state === 'done' ? 'text-slate-200' : 'text-slate-500'}`}>
                        {s.label}
                      </h3>
                      <p className="text-xs text-slate-500 mt-1 max-w-[120px]">{s.desc}</p>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Live Progress Logs */}
            {latestEvent && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl text-center mt-8 relative"
              >
                <div className="absolute top-3 right-3 flex items-center gap-1.5 text-xs text-slate-500">
                  <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
                  <span>Streaming</span>
                </div>
                <span className="text-xs text-indigo-400 font-bold uppercase tracking-wider">{latestEvent.agent || "Orchestrator"}</span>
                <p className="text-lg text-slate-100 font-semibold mt-2">{latestEvent.message}</p>
                {latestEvent.detail && (
                  <p className="text-sm text-slate-400 mt-2 italic leading-relaxed">{latestEvent.detail}</p>
                )}
              </motion.div>
            )}

            {/* Identified Subtopics Progress Panel */}
            {subtopics.length > 0 && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="w-full max-w-2xl mt-12"
              >
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest text-center mb-6">Research Areas Being Investigated</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {subtopics.map((st) => (
                    <div 
                      key={st.id} 
                      className={`flex items-center gap-3 p-4 rounded-xl border transition-all ${
                        st.status === 'completed' || st.status === 'done'
                          ? 'bg-emerald-950/10 border-emerald-900/50 text-slate-300'
                          : st.status === 'verifying' || st.status === 'searching'
                          ? 'bg-indigo-950/15 border-indigo-900/50 text-indigo-200'
                          : 'bg-slate-900/40 border-slate-800/80 text-slate-500'
                      }`}
                    >
                      {st.status === 'completed' || st.status === 'done' ? (
                        <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                      ) : st.status === 'verifying' || st.status === 'searching' ? (
                        <Loader2 className="w-5 h-5 text-indigo-400 animate-spin shrink-0" />
                      ) : (
                        <Circle className="w-4 h-4 text-slate-700 shrink-0" />
                      )}
                      <span className="text-sm font-medium line-clamp-2">{st.title}</span>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </motion.div>
        )}

        {/* CASE 2: COMPLETED REPORT CONTAINER */}
        {overallStatus === "completed" && report && (
          <motion.div 
            key="report"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col gap-8"
          >
            {/* Report Header Block */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-800">
              <div>
                <span className="text-xs text-indigo-400 font-bold uppercase tracking-widest">Autonomous SWARM Output</span>
                <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight mt-1 text-slate-100">
                  Research Document Ready
                </h1>
                <p className="text-sm text-slate-400 mt-1">Verified references mapped automatically with inline citations.</p>
              </div>

              {/* Action Downloads Swarm */}
              <div className="flex gap-4">
                <button
                  onClick={() => handleDownload('pdf')}
                  disabled={downloading !== null}
                  className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white px-5 py-3 rounded-xl text-sm font-semibold transition-all shadow-lg shadow-indigo-600/10 hover:shadow-indigo-500/20"
                >
                  {downloading === 'pdf' ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <FileText className="w-4 h-4" />
                  )}
                  <span>Download PDF</span>
                </button>
                <button
                  onClick={() => handleDownload('ppt')}
                  disabled={downloading !== null}
                  className="flex items-center gap-2 bg-slate-900 hover:bg-slate-800 border border-slate-700/80 disabled:border-slate-800 text-slate-200 px-5 py-3 rounded-xl text-sm font-semibold transition-all shadow-md"
                >
                  {downloading === 'ppt' ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Presentation className="w-4 h-4" />
                  )}
                  <span>Download PPT</span>
                </button>
              </div>
            </div>

            {/* Metrics Dashboard Widget */}
            {report.metrics && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-5">
                  <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">
                    <BookOpen className="w-4 h-4 text-indigo-400" />
                    <span>Report Length</span>
                  </div>
                  <p className="text-2xl font-extrabold text-slate-200">{report.metrics.word_count || 0} words</p>
                </div>
                <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-5">
                  <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">
                    <Layers className="w-4 h-4 text-emerald-400" />
                    <span>Sources Verified</span>
                  </div>
                  <p className="text-2xl font-extrabold text-slate-200">{report.metrics.source_count || 0} sources</p>
                </div>
                <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-5">
                  <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">
                    <CheckCircle2 className="w-4 h-4 text-indigo-400" />
                    <span>Citation Coverage</span>
                  </div>
                  <p className="text-2xl font-extrabold text-slate-200">{Math.round(report.metrics.citation_coverage || 0)}%</p>
                </div>
                <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-5">
                  <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">
                    <Clock className="w-4 h-4 text-amber-400" />
                    <span>Swarm Duration</span>
                  </div>
                  <p className="text-2xl font-extrabold text-slate-200">{Math.round(report.metrics.time_taken || 0)}s</p>
                </div>
              </div>
            )}

            {/* Markdown Report Visual Renderer */}
            <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-8 shadow-2xl relative prose prose-invert max-w-none">
              <ReactMarkdown
                components={{
                  h1: ({node, ...props}) => <h1 className="text-3xl font-extrabold text-slate-50 border-b border-slate-800 pb-4 mt-8 mb-4 bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent" {...props} />,
                  h2: ({node, ...props}) => <h2 className="text-2xl font-bold text-slate-100 mt-8 mb-4 border-l-4 border-indigo-500 pl-3.5" {...props} />,
                  h3: ({node, ...props}) => <h3 className="text-xl font-semibold text-slate-200 mt-6 mb-3" {...props} />,
                  p: ({node, ...props}) => <p className="text-slate-300 leading-relaxed my-4 text-base" {...props} />,
                  ul: ({node, ...props}) => <ul className="list-disc pl-6 my-4 space-y-2 text-slate-300" {...props} />,
                  ol: ({node, ...props}) => <ol className="list-decimal pl-6 my-4 space-y-2 text-slate-300" {...props} />,
                  li: ({node, ...props}) => <li className="pl-1" {...props} />,
                  blockquote: ({node, ...props}) => <blockquote className="bg-slate-900/50 border-l-4 border-indigo-600/60 pl-4 py-2.5 my-5 italic text-slate-400 rounded-r-lg" {...props} />,
                  code: ({node, ...props}) => <code className="bg-slate-950 px-1.5 py-0.5 rounded font-mono text-indigo-300 text-sm" {...props} />
                }}
              >
                {report.markdown}
              </ReactMarkdown>
            </div>
          </motion.div>
        )}

        {/* CASE 3: PIPELINE EXECUTION FAILURE */}
        {overallStatus === "failed" && (
          <motion.div 
            key="failed"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full max-w-2xl mx-auto mt-16"
          >
            <div className="bg-red-950/20 border border-red-900/60 rounded-3xl p-10 text-center shadow-2xl relative overflow-hidden">
              {/* Top Warning Icon */}
              <div className="w-16 h-16 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-500 mx-auto mb-6">
                <AlertTriangle className="w-8 h-8 animate-pulse" />
              </div>
              <h2 className="text-2xl font-extrabold text-red-400 mb-3">Swarm Deployment Aborted</h2>
              <p className="text-slate-300 leading-relaxed mb-6 max-w-md mx-auto">
                {latestEvent?.message || "An unexpected error occurred while deploying our AI agents."}
              </p>
              {latestEvent?.detail && (
                <div className="bg-red-950/50 p-4 rounded-2xl border border-red-900/40 text-left font-mono text-xs text-red-300 overflow-x-auto leading-relaxed max-w-lg mx-auto">
                  <span className="font-bold text-red-400 block mb-1">Diagnostic Log:</span>
                  {latestEvent.detail}
                </div>
              )}
            </div>
          </motion.div>
        )}

      </AnimatePresence>
    </div>
  );
}
