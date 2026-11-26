import { errorResponse } from "@/lib/http";
import { removeDocument } from "@/lib/procurement-service";

export async function DELETE(_request: Request, { params }: { params: Promise<{ id: string; documentId: string }> }) {
  try {
    const { id, documentId } = await params;
    return Response.json({ data: removeDocument(id, documentId), removed: true });
  } catch (error) { return errorResponse(error); }
}
