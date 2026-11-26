import { errorResponse } from "@/lib/http";
import { listJobs, queueVerification } from "@/lib/procurement-service";

export async function GET(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  try { return Response.json({ data: listJobs((await params).id) }); }
  catch (error) { return errorResponse(error); }
}

export async function POST(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  try { return Response.json({ data: queueVerification((await params).id) }, { status: 202 }); }
  catch (error) { return errorResponse(error); }
}
