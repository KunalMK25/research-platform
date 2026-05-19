"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getResearchStatus } from "@/lib/api";
import AgentPanel from "@/components/AgentPanel";
import StreamOutput from "@/components/StreamOutput";
import { Loader2 } from "lucide-react";

export default function LiveResearchPage() {
  const { id } = useParams();
  const router = useRouter();
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    if (!id) return;

    const interval = setInterval(async () => {
      try {
        const data = await getResearchStatus(id as string);
        setStatus(data);
        if (data.status === "completed") {
          clearInterval(interval);
          setTimeout(() => {
            router.push(`/report/${id}`);
          }, 2000);
        } else if (data.status === "failed") {
          clearInterval(interval);
        }
      } catch (err) {
        console.error(err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [id, router]);

  if (!status) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="lg:col-span-1">
        <AgentPanel status={status.status} />
      </div>
      <div className="lg:col-span-2">
        <StreamOutput progress={status.progress} />
      </div>
    </div>
  );
}
