"""Django ORM repository for PostgreSQL-backed procurement records."""
from datetime import datetime, timezone

from django.db import transaction
from django.utils import timezone as django_timezone
from uuid import uuid4

from .models import AuditEvent, Bid, BidDocument, ReviewDecision, VerificationJob


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bid_data(bid: Bid) -> dict:
    return {
        "id": bid.id,
        "reference": bid.reference,
        "title": bid.title,
        "department": bid.department,
        "deadline": bid.deadline.isoformat(),
        "status": bid.status,
        "vendors": bid.vendors,
        "updated": django_timezone.localtime(bid.updated_at).strftime("%d %b %Y, %I:%M %p"),
        "progress": bid.progress,
        "documents": [_document_data(item) for item in bid.documents.all()],
    }


def _document_data(document: BidDocument) -> dict:
    return {"id": str(document.id), "name": document.name, "size": document.size, "uploadedAt": document.uploaded_at.isoformat()}


def _job_data(job: VerificationJob) -> dict:
    return {"id": job.id, "bidId": job.bid_id, "status": job.status, "createdAt": job.created_at.isoformat(), "message": job.message}


def _review_data(review: ReviewDecision) -> dict:
    return {"id": review.finding_id, "decision": review.decision, "note": review.note, "reviewer": review.reviewer, "createdAt": review.created_at.isoformat()}


def _audit_data(event: AuditEvent) -> dict:
    return {"id": str(event.id), "event": event.event, "actor": event.actor, "target": event.target, "details": event.details, "createdAt": event.created_at.isoformat()}


class PostgresRepository:
    def active_bids(self) -> list[dict]:
        return [_bid_data(bid) for bid in Bid.objects.filter(archived_at__isnull=True).prefetch_related("documents")]

    def get_bid(self, bid_id: str) -> dict | None:
        bid = Bid.objects.filter(archived_at__isnull=True).filter(id=bid_id).prefetch_related("documents").first()
        if bid is None:
            bid = Bid.objects.filter(archived_at__isnull=True, reference__iexact=bid_id).prefetch_related("documents").first()
        return _bid_data(bid) if bid else None

    @transaction.atomic
    def create_bid(self, values: dict) -> dict:
        bid_id = f"BID-{datetime.now().year}-{uuid4().hex[:8].upper()}"
        bid = Bid.objects.create(id=bid_id, **values)
        self.add_audit("Bid workspace created", bid.reference, f"Workspace created for {bid.title}.")
        return _bid_data(bid)

    @transaction.atomic
    def update_bid(self, bid_id: str, values: dict) -> dict | None:
        bid = Bid.objects.select_for_update().filter(id=bid_id, archived_at__isnull=True).first()
        if not bid:
            return None
        for key, value in values.items():
            setattr(bid, key, value)
        bid.save()
        self.add_audit("Bid workspace updated", bid.reference, f"Updated fields: {', '.join(values)}.")
        return _bid_data(bid)

    @transaction.atomic
    def archive_bid(self, bid_id: str) -> dict | None:
        bid = Bid.objects.select_for_update().filter(id=bid_id, archived_at__isnull=True).first()
        if not bid:
            return None
        bid.archived_at = django_timezone.now()
        bid.save(update_fields=["archived_at", "updated_at"])
        self.add_audit("Bid workspace archived", bid.reference, "Workspace soft archived.")
        return _bid_data(bid)

    @transaction.atomic
    def add_documents(self, bid_id: str, entries: list[dict]) -> list[dict] | None:
        bid = Bid.objects.select_for_update().filter(id=bid_id, archived_at__isnull=True).first()
        if not bid:
            return None
        documents = [
            BidDocument.objects.create(id=entry["id"], bid=bid, name=entry["name"], size=entry["size"])
            for entry in entries
        ]
        bid.save(update_fields=["updated_at"])
        self.add_audit("Documents added", bid.reference, f"{len(documents)} document(s) added; content discarded.")
        return [_document_data(item) for item in documents]

    @transaction.atomic
    def remove_document(self, bid_id: str, document_id: str) -> dict | None:
        document = BidDocument.objects.select_for_update().filter(bid_id=bid_id, bid__archived_at__isnull=True, id=document_id).first()
        if not document:
            return None
        data = _document_data(document)
        bid_reference = document.bid.reference
        document.delete()
        self.add_audit("Document removed", bid_reference, f"{data['name']} metadata removed.")
        return data

    @transaction.atomic
    def add_job(self, bid_id: str) -> dict | None:
        bid = Bid.objects.select_for_update().filter(id=bid_id, archived_at__isnull=True).first()
        if not bid:
            return None
        job = VerificationJob.objects.create(
            id=f"JOB-{uuid4().hex[:8].upper()}",
            bid=bid,
            message="Request recorded. No worker is configured until AI integration is added.",
        )
        self.add_audit("Verification request queued", bid.reference, f"{job.id} recorded; no processing worker is configured.")
        return _job_data(job)

    def list_jobs(self, bid_id: str | None = None) -> list[dict]:
        jobs = VerificationJob.objects.all()
        if bid_id:
            jobs = jobs.filter(bid_id=bid_id)
        return [_job_data(job) for job in jobs]

    def get_review(self, finding_id: str) -> dict | None:
        review = ReviewDecision.objects.filter(finding_id=finding_id).first()
        return _review_data(review) if review else None

    @transaction.atomic
    def save_review(self, review: dict) -> dict:
        record, _ = ReviewDecision.objects.update_or_create(
            finding_id=review["id"],
            defaults={"decision": review["decision"], "note": review["note"], "reviewer": review["reviewer"]},
        )
        self.add_audit("Review decision recorded", record.finding_id, f"{record.decision}: {record.note}")
        return _review_data(record)

    def add_audit(self, event: str, target: str, details: str, actor: str = "Arjun Sharma") -> dict:
        return _audit_data(AuditEvent.objects.create(event=event, actor=actor, target=target, details=details))

    def list_audit(self) -> list[dict]:
        return [_audit_data(event) for event in AuditEvent.objects.all()]


repository = PostgresRepository()
