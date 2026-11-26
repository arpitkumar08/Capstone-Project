import { listJobs } from "@/lib/procurement-service";

export function GET(request: Request) {
  const url = new URL(request.url);
  return Response.json({ data: listJobs(url.searchParams.get("bidId") || undefined) });
}
