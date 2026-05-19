const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function startResearch(topic: string, depth: string, userId: string = "anonymous") {
  const res = await fetch(`${API_URL}/research/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, depth, user_id: userId }),
  });
  if (!res.ok) throw new Error("Failed to start research");
  return res.json();
}

export async function getResearchStatus(sessionId: string) {
  const res = await fetch(`${API_URL}/research/${sessionId}/status`);
  if (!res.ok) throw new Error("Failed to get status");
  return res.json();
}

export async function getReport(sessionId: string) {
  const res = await fetch(`${API_URL}/research/${sessionId}/report`);
  if (!res.ok) throw new Error("Failed to get report");
  return res.json();
}

export async function getHistory(userId: string) {
  const res = await fetch(`${API_URL}/history/${userId}`);
  if (!res.ok) throw new Error("Failed to get history");
  return res.json();
}
