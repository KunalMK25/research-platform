"use client";

import { useEffect, useState } from "react";
import { getHistory } from "@/lib/api";
import Link from "next/link";
import { Clock, ArrowRight, FileText } from "lucide-react";

export default function HistoryPage() {
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    getHistory("anonymous").then(data => setHistory(data)).catch(console.error);
  }, []);

  return (
    <div className="max-w-5xl mx-auto pb-20">
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-white mb-2">Research History</h1>
        <p className="text-slate-400">View and manage your past autonomous research sessions.</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden">
        {history.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No research history found.</p>
          </div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/50">
                <th className="p-4 font-medium text-slate-400">Topic</th>
                <th className="p-4 font-medium text-slate-400">Depth</th>
                <th className="p-4 font-medium text-slate-400">Status</th>
                <th className="p-4 font-medium text-slate-400">Date</th>
                <th className="p-4 font-medium text-slate-400 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {history.map((session) => (
                <tr key={session.id} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition">
                  <td className="p-4 font-medium text-slate-200">{session.topic}</td>
                  <td className="p-4">
                    <span className="bg-slate-800 text-slate-300 text-xs px-2 py-1 rounded-full">{session.depth}</span>
                  </td>
                  <td className="p-4">
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      session.status === 'completed' ? 'bg-green-500/10 text-green-400' :
                      session.status === 'failed' ? 'bg-red-500/10 text-red-400' :
                      'bg-blue-500/10 text-blue-400'
                    }`}>
                      {session.status}
                    </span>
                  </td>
                  <td className="p-4 text-sm text-slate-500">
                    {new Date(session.created_at).toLocaleDateString()}
                  </td>
                  <td className="p-4 text-right">
                    {session.status === 'completed' ? (
                      <Link href={`/report/${session.id}`} className="inline-flex items-center gap-1 text-sm text-blue-400 hover:text-blue-300 transition">
                        View Report <ArrowRight className="w-4 h-4" />
                      </Link>
                    ) : (
                      <Link href={`/research/${session.id}`} className="inline-flex items-center gap-1 text-sm text-slate-400 hover:text-slate-300 transition">
                        View Live <ArrowRight className="w-4 h-4" />
                      </Link>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
