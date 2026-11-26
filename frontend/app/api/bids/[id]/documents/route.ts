import { errorResponse } from "@/lib/http";
import { addDocuments, getBid } from "@/lib/procurement-service";
import { ServiceError } from "@/lib/procurement-service";

type Context = { params: Promise<{ id: string }> };

export async function GET(_request: Request, { params }: Context) {
  try { return Response.json({ data: getBid((await params).id).documents }); }
  catch (error) { return errorResponse(error); }
}

export async function POST(request: Request, { params }: Context) {
  try {
    const { id } = await params;
    const form = await request.formData();
    const files = form.getAll("files");
    if (files.some((file) => !(file instanceof File))) throw new ServiceError("Each files field must contain an uploaded file.");
    return Response.json({ data: addDocuments(id, files as File[]) }, { status: 201 });
  } catch (error) { return errorResponse(error); }
}
