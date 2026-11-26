import { ServiceError } from "@/lib/procurement-service";

export function errorResponse(error: unknown) {
  if (error instanceof ServiceError) return Response.json({ error: error.message }, { status: error.status });
  console.error("ProcureIQ API error", error);
  return Response.json({ error: "An unexpected server error occurred." }, { status: 500 });
}

export async function readJson(request: Request) {
  try { return await request.json() as unknown; }
  catch { throw new ServiceError("Request body must contain valid JSON."); }
}
