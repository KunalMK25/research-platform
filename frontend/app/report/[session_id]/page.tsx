"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getReport, exportPDF, exportPPT } from "@/lib/api";
import ReactMarkdown from "react-markdown";
import { Loader2, Download, Share2 } from "lucide-react";

export default function ReportPage() {
  const params = useParams();
  const id = params?.session_id as string;
  const [report, setReport] = useState<any>(null);
  const [downloading, setDownloading] = useState<'pdf' | 'ppt' | null>(null);

  const handleDownload = async (type: 'pdf' | 'ppt') => {
    setDownloading(type);
    try {
      const fn = type === 'pdf' ? exportPDF : exportPPT;
      const blob = await fn(id);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = type === 'pdf' ? `report_${id}.pdf` : `presentation_${id}.pptx`;
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

  useEffect(() => {
    if (!id) return;
    getReport(id).then(data => setReport(data)).catch(console.error);
  }, [id]);

  if (!report) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto pb-20">
      <div className="flex items-center justify-between mb-8 pb-8 border-b border-slate-800">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Final Research Report</h1>
          <p className="text-slate-400">Session ID: {id}</p>
        </div>
        <div className="flex gap-4">
          <button onClick={() => handleDownload('pdf')} disabled={downloading !== null} className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-white px-4 py-2 rounded-xl transition">
            {downloading === 'pdf' ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />} PDF
          </button>
          <button onClick={() => handleDownload('ppt')} disabled={downloading !== null} className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-white px-4 py-2 rounded-xl transition">
            {downloading === 'ppt' ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />} PPT
          </button>
          <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-xl transition">
            <Share2 className="w-4 h-4" /> Share
          </button>
        </div>
      </div>

      <div className="prose prose-invert prose-blue max-w-none bg-slate-900 border border-slate-800 p-8 md:p-12 rounded-3xl shadow-xl">
        <ReactMarkdown>{report.markdown}</ReactMarkdown>
      </div>
    </div>
  );
}
