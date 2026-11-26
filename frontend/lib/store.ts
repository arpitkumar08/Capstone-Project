export type BidStatus = "Draft" | "Processing" | "Needs review" | "Completed";
export type BidRecord = {
  id: string; reference: string; title: string; department: string; deadline: string;
  status: BidStatus; vendors: number; updated: string; progress: number;
  documents: { id: string; name: string; size: number; uploadedAt: string }[];
  archivedAt?: string;
};
export type AuditEntry = { id: string; event: string; actor: string; target: string; details: string; createdAt: string };
export type VerificationJob = { id: string; bidId: string; status: "queued"; createdAt: string; message: string };
export type ReviewRecord = { id: string; decision: "Compliant" | "Non-compliant" | "Request clarification"; note: string; reviewer: string; createdAt: string };
// This no-database backend deliberately stores only process-local metadata. Upload bytes are discarded.

const seed: BidRecord[] = [
  { id: "BID-2025-0842", reference: "GEM/2025/B/5842190", title: "Supply of 250 kVA Diesel Generator Sets", department: "Ministry of Railways", deadline: "2025-02-18", status: "Needs review", vendors: 4, updated: "12 min ago", progress: 86, documents: [] },
  { id: "BID-2025-0837", reference: "GEM/2025/B/5839072", title: "Enterprise Network Switches · 48 Port", department: "National Informatics Centre", deadline: "2025-02-21", status: "Processing", vendors: 6, updated: "38 min ago", progress: 62, documents: [] },
  { id: "BID-2025-0829", reference: "GEM/2025/B/5828641", title: "Laboratory Grade Water Purification System", department: "IIT Delhi", deadline: "2025-02-24", status: "Completed", vendors: 3, updated: "2 hours ago", progress: 100, documents: [] },
  { id: "BID-2025-0816", reference: "GEM/2025/B/5817730", title: "Annual Maintenance · HVAC Equipment", department: "AIIMS New Delhi", deadline: "2025-02-28", status: "Draft", vendors: 2, updated: "Yesterday", progress: 0, documents: [] },
  { id: "BID-2025-0804", reference: "GEM/2025/B/5802291", title: "Desktop Workstations for Regional Offices", department: "Ministry of Finance", deadline: "2025-03-04", status: "Completed", vendors: 5, updated: "Yesterday", progress: 100, documents: [] },
];

type Store = { bids: BidRecord[]; reviews: Map<string, ReviewRecord>; audit: AuditEntry[]; jobs: VerificationJob[] };
const g = globalThis as typeof globalThis & { __procureIQStore?: Store };
export const store = g.__procureIQStore ??= {
  bids: seed,
  reviews: new Map<string, ReviewRecord>(),
  audit: [] as AuditEntry[],
  jobs: [] as VerificationJob[],
};
export function audit(event: string, target: string, details: string, actor = "Arjun Sharma") {
  const entry = { id: crypto.randomUUID(), event, actor, target, details, createdAt: new Date().toISOString() };
  store.audit.unshift(entry);
  return entry;
}
export function jsonError(message: string, status = 400) {
  return Response.json({ error: message }, { status });
}
