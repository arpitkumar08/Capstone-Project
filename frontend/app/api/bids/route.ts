import { errorResponse, readJson } from "@/lib/http";
import { createBid, listBids, parsePagination, parseStatus } from "@/lib/procurement-service";

export function GET(request: Request) {
  try {
    const url = new URL(request.url);
    const pagination = parsePagination(url);
    return Response.json(listBids({ q: url.searchParams.get("q") || "", status: parseStatus(url.searchParams.get("status")), ...pagination }));
  } catch (error) { return errorResponse(error); }
}

export async function POST(request: Request) {
  try { return Response.json({ data: createBid(await readJson(request)) }, { status: 201 }); }
  catch (error) { return errorResponse(error); }
}
