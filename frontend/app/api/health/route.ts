export function GET() {
  return Response.json({ status: "ok", service: "procureiq-api", integrations: { redis: false, database: false, ai: false } });
}
