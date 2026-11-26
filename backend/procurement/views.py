from datetime import datetime, timezone
from pathlib import PurePath
from uuid import uuid4

from django.db import OperationalError, connection
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .repository import now_iso, repository
from .serializers import BidSerializer, ReviewSerializer


def not_found(message: str) -> Response:
    return Response({"error": message}, status=status.HTTP_404_NOT_FOUND)


class HealthView(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except OperationalError:
            return Response({"status": "degraded", "service": "procureiq-django-api", "integrations": {"redis": False, "database": False, "ai": False}}, status=503)
        return Response({"status": "ok", "service": "procureiq-django-api", "integrations": {"redis": False, "database": True, "ai": False}})


class BidListCreateView(APIView):
    def get(self, request):
        try:
            page = int(request.query_params.get("page", "1"))
            limit = int(request.query_params.get("limit", "50"))
        except ValueError:
            return Response({"error": "page and limit must be integers."}, status=400)
        if page < 1 or not 1 <= limit <= 100:
            return Response({"error": "page must be positive and limit must be from 1 to 100."}, status=400)
        query = request.query_params.get("q", "").strip().casefold()
        valid_statuses = {"Draft", "Processing", "Needs review", "Completed"}
        chosen_status = request.query_params.get("status")
        if chosen_status and chosen_status != "All status" and chosen_status not in valid_statuses:
            return Response({"error": "status must be Draft, Processing, Needs review, or Completed."}, status=400)
        rows = repository.active_bids()
        if query:
            rows = [row for row in rows if query in " ".join((row["reference"], row["title"], row["department"])).casefold()]
        if chosen_status and chosen_status != "All status":
            rows = [row for row in rows if row["status"] == chosen_status]
        start = (page - 1) * limit
        return Response({"data": rows[start:start + limit], "total": len(rows), "page": page, "limit": limit})

    def post(self, request):
        serializer = BidSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            bid = repository.create_bid(serializer.validated_data)
        except ValueError as error:
            return Response({"error": str(error)}, status=409)
        return Response({"data": bid}, status=status.HTTP_201_CREATED)


class BidDetailView(APIView):
    def get(self, request, bid_id):
        bid = repository.get_bid(bid_id)
        return Response({"data": bid}) if bid else not_found("Bid not found.")

    def patch(self, request, bid_id):
        existing = repository.get_bid(bid_id)
        if not existing:
            return not_found("Bid not found.")
        serializer = BidSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if not serializer.validated_data:
            return Response({"error": "Provide at least one bid field to update."}, status=400)
        values = dict(serializer.validated_data)
        try:
            bid = repository.update_bid(existing["id"], values)
        except ValueError as error:
            return Response({"error": str(error)}, status=409)
        return Response({"data": bid})

    def delete(self, request, bid_id):
        existing = repository.get_bid(bid_id)
        if not existing:
            return not_found("Bid not found.")
        archived = repository.archive_bid(existing["id"])
        return Response({"data": archived, "archived": True})


class BidDocumentView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    allowed_extensions = {".pdf", ".doc", ".docx", ".xls", ".xlsx"}
    max_file_size = 25 * 1024 * 1024

    def get(self, request, bid_id):
        bid = repository.get_bid(bid_id)
        return Response({"data": bid["documents"]}) if bid else not_found("Bid not found.")

    def post(self, request, bid_id):
        bid = repository.get_bid(bid_id)
        if not bid:
            return not_found("Bid not found.")
        files = request.FILES.getlist("files")
        if not files:
            return Response({"error": "Choose at least one file using the 'files' field."}, status=400)
        if len(files) > 20:
            return Response({"error": "Upload no more than 20 files at once."}, status=400)
        total = 0
        entries = []
        for uploaded in files:
            safe_name = PurePath(uploaded.name.replace("\\", "/")).name[:180]
            if not safe_name or PurePath(safe_name).suffix.lower() not in self.allowed_extensions:
                return Response({"error": f"{safe_name or 'File'} must be PDF, DOC, DOCX, XLS, or XLSX."}, status=400)
            if uploaded.size <= 0 or uploaded.size > self.max_file_size:
                return Response({"error": f"{safe_name} must be non-empty and no larger than 25 MB."}, status=400)
            total += uploaded.size
            entries.append({"id": str(uuid4()), "name": safe_name, "size": uploaded.size, "uploadedAt": now_iso()})
        if total > 100 * 1024 * 1024:
            return Response({"error": "The combined upload size cannot exceed 100 MB."}, status=400)
        added = repository.add_documents(bid["id"], entries)
        return Response({"data": added, "contentStored": False}, status=status.HTTP_201_CREATED)


class BidDocumentDetailView(APIView):
    def delete(self, request, bid_id, document_id):
        bid = repository.get_bid(bid_id)
        if not bid:
            return not_found("Bid not found.")
        removed = repository.remove_document(bid["id"], document_id)
        return Response({"data": removed, "removed": True}) if removed else not_found("Document not found.")


class VerificationJobView(APIView):
    def get(self, request, bid_id):
        bid = repository.get_bid(bid_id)
        return Response({"data": repository.list_jobs(bid["id"])}) if bid else not_found("Bid not found.")

    def post(self, request, bid_id):
        bid = repository.get_bid(bid_id)
        if not bid:
            return not_found("Bid not found.")
        job = repository.add_job(bid["id"])
        return Response({"data": job}, status=status.HTTP_202_ACCEPTED)


class JobListView(APIView):
    def get(self, request):
        return Response({"data": repository.list_jobs(request.query_params.get("bidId"))})


class ReviewView(APIView):
    def get(self, request, finding_id):
        review = repository.get_review(finding_id)
        return Response({"data": review}) if review else not_found("Review not found.")

    def post(self, request, finding_id):
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = {"id": finding_id, **serializer.validated_data, "reviewer": "Arjun Sharma", "createdAt": datetime.now(timezone.utc).isoformat()}
        return Response({"data": repository.save_review(review)}, status=status.HTTP_201_CREATED)


class AuditListView(APIView):
    def get(self, request):
        try:
            page = max(1, int(request.query_params.get("page", "1")))
            limit = min(100, max(1, int(request.query_params.get("limit", "50"))))
        except ValueError:
            return Response({"error": "page and limit must be integers."}, status=400)
        query = request.query_params.get("q", "").strip().casefold()
        event = request.query_params.get("event", "").strip()
        rows = repository.list_audit()
        rows = [row for row in rows if (not event or row["event"] == event) and (not query or query in " ".join(str(row[key]) for key in ("event", "actor", "target", "details")).casefold())]
        start = (page - 1) * limit
        return Response({"data": rows[start:start + limit], "total": len(rows), "page": page, "limit": limit, "readOnly": True})
