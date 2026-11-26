import { errorResponse, readJson } from "@/lib/http";
import { archiveBid, getBid, updateBid } from "@/lib/procurement-service";

type Context = { params: Promise<{ id: string }> };

export async function GET(_request: Request, { params }: Context) {
  try { return Response.json({ data: getBid((await params).id) }); }
  catch (error) { return errorResponse(error); }
}

export async function PATCH(request: Request, { params }: Context) {
  try { return Response.json({ data: updateBid((await params).id, await readJson(request)) }); }
  catch (error) { return errorResponse(error); }
}

export async function DELETE(_request: Request, { params }: Context) {
  try { return Response.json({ data: archiveBid((await params).id), archived: true }); }
  catch (error) { return errorResponse(error); }
}
