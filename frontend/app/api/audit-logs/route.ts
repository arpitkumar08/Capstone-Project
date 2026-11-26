import { errorResponse } from "@/lib/http";
import { auditPage } from "@/lib/procurement-service";

export function GET(request: Request) {
  try { return Response.json(auditPage(request.url)); }
  catch (error) { return errorResponse(error); }
}
