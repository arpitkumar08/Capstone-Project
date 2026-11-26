import { errorResponse, readJson } from "@/lib/http";
import { ServiceError, recordReview } from "@/lib/procurement-service";
import { store } from "@/lib/store";

export async function GET(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const review = store.reviews.get(id);
  return review ? Response.json({ data: review }) : Response.json({ error: "Review not found." }, { status: 404 });
}

export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    if (!id.trim()) throw new ServiceError("Review finding id is required.");
    return Response.json({ data: recordReview(id, await readJson(request)) }, { status: 201 });
  } catch (error) { return errorResponse(error); }
}
