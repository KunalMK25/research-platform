import { useEffect, useRef, useState } from "react";
import { Terminal } from "lucide-react";

export default function StreamOutput({ progress }: { progress: any }) {
  const [logs, setLogs] = useState<string[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (progress?.message) {
      setLogs(prev => {
        if (prev[prev.length - 1] === progress.message) return prev;
        return [...prev, progress.message];
      });
    }
  }, [progress]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div className="bg-black border border-slate-800 rounded-2xl p-6 h-full min-h-[500px] flex flex-col font-mono text-sm relative overflow-hidden">
      <div className="flex items-center gap-3 border-b border-slate-800 pb-4 mb-4">
        <Terminal className="w-5 h-5 text-slate-500" />
        <span className="text-slate-400 font-sans">Live Execution Logs</span>
      </div>
      
      <div className="flex-1 overflow-y-auto space-y-3 custom-scrollbar">
        {logs.length === 0 ? (
          <div className="text-slate-600 italic">Awaiting agent initialization...</div>
        ) : (
          logs.map((log, i) => (
            <div key={i} className="text-slate-300 flex items-start gap-3">
              <span className="text-blue-500 shrink-0">{`>`}</span>
              <span className="break-words">{log}</span>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
