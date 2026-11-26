import { audit, store, type BidRecord, type BidStatus, type ReviewRecord, type VerificationJob } from "@/lib/store";

export class ServiceError extends Error {
  constructor(message: string, readonly status = 400) { super(message); }
}

function asObject(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new ServiceError("Request body must be a JSON object.");
  return value as Record<string, unknown>;
}

export function validateBidInput(value: unknown, partial = false): Partial<Pick<BidRecord, "title" | "reference" | "department" | "deadline">> {
  const input = asObject(value);
  const result: Record<string, string> = {};
  for (const key of ["title", "reference", "department", "deadline"] as const) {
    if (input[key] === undefined && partial) continue;
    if (typeof input[key] !== "string" || !input[key].trim()) throw new ServiceError(`${key} is required and must be text.`);
    result[key] = input[key].trim();
  }
  for (const key of ["title", "reference", "department"] as const) {
    if (result[key] && result[key].length > 180) throw new ServiceError(`${key} must be 180 characters or fewer.`);
  }
  if (result.deadline && (!/^\d{4}-\d{2}-\d{2}$/.test(result.deadline) || Number.isNaN(Date.parse(`${result.deadline}T00:00:00Z`)))) {
    throw new ServiceError("deadline must be a valid date in YYYY-MM-DD format.");
  }
  return result;
}

export function listBids(options: { q?: string; status?: string; page?: number; limit?: number }) {
  const q = (options.q || "").trim().toLocaleLowerCase();
  const status = options.status;
  const matched = store.bids.filter((bid) => !bid.archivedAt &&
    (!q || `${bid.reference} ${bid.title} ${bid.department}`.toLocaleLowerCase().includes(q)) &&
    (!status || status === "All status" || bid.status === status));
  const page = options.page ?? 1;
  const limit = options.limit ?? 50;
  return { data: matched.slice((page - 1) * limit, page * limit), total: matched.length, page, limit };
}

export function getBid(id: string) {
  const bid = store.bids.find((item) => !item.archivedAt && (item.id === id || item.reference.toLowerCase() === id.toLowerCase()));
  if (!bid) throw new ServiceError("Bid not found.", 404);
  return bid;
}

export function createBid(value: unknown) {
  const input = validateBidInput(value) as Required<Pick<BidRecord, "title" | "reference" | "department" | "deadline">>;
  if (store.bids.some((bid) => bid.reference.toLowerCase() === input.reference.toLowerCase())) throw new ServiceError("A bid with this GeM reference already exists.", 409);
  const bid: BidRecord = { id: `BID-${new Date().getFullYear()}-${crypto.randomUUID().slice(0, 8).toUpperCase()}`, ...input, status: "Draft", vendors: 0, updated: "Just now", progress: 0, documents: [] };
  store.bids.unshift(bid);
  audit("Bid workspace created", bid.reference, `Workspace created for ${bid.title}.`);
  return bid;
}

export function updateBid(id: string, value: unknown) {
  const bid = getBid(id);
  const changes = validateBidInput(value, true);
  if (!Object.keys(changes).length) throw new ServiceError("Provide at least one bid field to update.");
  if (changes.reference && store.bids.some((item) => item.id !== bid.id && item.reference.toLowerCase() === changes.reference!.toLowerCase())) throw new ServiceError("A bid with this GeM reference already exists.", 409);
  Object.assign(bid, changes, { updated: "Just now" });
  audit("Bid workspace updated", bid.reference, `Updated fields: ${Object.keys(changes).join(", ")}.`);
  return bid;
}

export function archiveBid(id: string) {
  const bid = getBid(id);
  bid.archivedAt = new Date().toISOString();
  audit("Bid workspace archived", bid.reference, "Workspace soft archived by a reviewer.");
  return bid;
}

export function addDocuments(id: string, files: File[]) {
  const bid = getBid(id);
  if (!files.length) throw new ServiceError("Choose at least one file.");
  if (files.length > 20) throw new ServiceError("Upload no more than 20 files at once.");
  const allowed = new Set(["pdf", "doc", "docx", "xls", "xlsx"]);
  const badFile = files.find((file) => !allowed.has(file.name.split(".").pop()?.toLowerCase() || "") || file.size <= 0 || file.size > 25 * 1024 * 1024);
  if (badFile) throw new ServiceError(`${badFile.name} must be a non-empty PDF, DOC, DOCX, XLS, or XLSX file no larger than 25 MB.`);
  if (files.reduce((total, file) => total + file.size, 0) > 100 * 1024 * 1024) throw new ServiceError("The combined upload size cannot exceed 100 MB.");
  const added = files.map((file) => ({ id: crypto.randomUUID(), name: file.name.replace(/[\\/]/g, "_").slice(0, 180), size: file.size, uploadedAt: new Date().toISOString() }));
  bid.documents.push(...added);
  bid.updated = "Just now";
  audit("Documents added", bid.reference, `${added.length} document(s) added. File contents are discarded by the in-memory backend.`);
  return added;
}

export function removeDocument(bidId: string, documentId: string) {
  const bid = getBid(bidId);
  const index = bid.documents.findIndex((document) => document.id === documentId);
  if (index < 0) throw new ServiceError("Document not found.", 404);
  const [removed] = bid.documents.splice(index, 1);
  audit("Document removed", bid.reference, `${removed.name} metadata removed.`);
  return removed;
}

export function queueVerification(id: string): VerificationJob {
  const bid = getBid(id);
  const job: VerificationJob = { id: `JOB-${crypto.randomUUID().slice(0, 8).toUpperCase()}`, bidId: bid.id, status: "queued", createdAt: new Date().toISOString(), message: "Request recorded. No worker is configured until AI integration is added." };
  store.jobs.unshift(job);
  audit("Verification request queued", bid.reference, `${job.id} recorded; processing is disabled until an AI worker is configured.`);
  return job;
}

export function listJobs(bidId?: string) {
  return store.jobs.filter((job) => !bidId || job.bidId === bidId);
}

export function recordReview(id: string, value: unknown): ReviewRecord {
  const input = asObject(value);
  const decision = input.decision;
  const validDecisions: ReviewRecord["decision"][] = ["Compliant", "Non-compliant", "Request clarification"];
  if (typeof decision !== "string" || !validDecisions.includes(decision as ReviewRecord["decision"])) throw new ServiceError("Choose a valid reviewer decision.");
  if (typeof input.note !== "string" || !input.note.trim()) throw new ServiceError("Reviewer notes are required.");
  if (input.note.trim().length > 4000) throw new ServiceError("Reviewer notes must be 4,000 characters or fewer.");
  const review: ReviewRecord = { id, decision: decision as ReviewRecord["decision"], note: input.note.trim(), reviewer: "Arjun Sharma", createdAt: new Date().toISOString() };
  store.reviews.set(id, review);
  audit("Review decision recorded", id, `${review.decision}: ${review.note}`);
  return review;
}

export function auditPage(requestUrl: string) {
  const url = new URL(requestUrl);
  const q = (url.searchParams.get("q") || "").trim().toLowerCase();
  const event = url.searchParams.get("event");
  const page = Math.max(1, Number(url.searchParams.get("page")) || 1);
  const limit = Math.min(100, Math.max(1, Number(url.searchParams.get("limit")) || 50));
  const entries = store.audit.filter((row) => (!q || `${row.event} ${row.actor} ${row.target} ${row.details}`.toLowerCase().includes(q)) && (!event || row.event === event));
  return { data: entries.slice((page - 1) * limit, page * limit), total: entries.length, page, limit, readOnly: true };
}

export function parsePagination(url: URL) {
  const page = Number(url.searchParams.get("page") || 1);
  const limit = Number(url.searchParams.get("limit") || 50);
  if (!Number.isInteger(page) || page < 1) throw new ServiceError("page must be a positive integer.");
  if (!Number.isInteger(limit) || limit < 1 || limit > 100) throw new ServiceError("limit must be an integer from 1 to 100.");
  return { page, limit };
}

export function parseStatus(value: string | null): BidStatus | undefined {
  if (!value || value === "All status") return undefined;
  if (!["Draft", "Processing", "Needs review", "Completed"].includes(value)) throw new ServiceError("status must be Draft, Processing, Needs review, or Completed.");
  return value as BidStatus;
}
