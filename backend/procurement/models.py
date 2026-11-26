import uuid

from django.db import models


class Bid(models.Model):
    class Status(models.TextChoices):
        DRAFT = "Draft", "Draft"
        PROCESSING = "Processing", "Processing"
        NEEDS_REVIEW = "Needs review", "Needs review"
        COMPLETED = "Completed", "Completed"

    id = models.CharField(max_length=32, primary_key=True)
    reference = models.CharField(max_length=180, unique=True)
    title = models.CharField(max_length=180)
    department = models.CharField(max_length=180)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    vendors = models.PositiveIntegerField(default=0)
    progress = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} · {self.title}"


class BidDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bid = models.ForeignKey(Bid, related_name="documents", on_delete=models.CASCADE)
    name = models.CharField(max_length=180)
    size = models.PositiveBigIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at"]


class VerificationJob(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"

    id = models.CharField(max_length=20, primary_key=True)
    bid = models.ForeignKey(Bid, related_name="verification_jobs", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    message = models.CharField(max_length=240)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class ReviewDecision(models.Model):
    class Decision(models.TextChoices):
        COMPLIANT = "Compliant", "Compliant"
        NON_COMPLIANT = "Non-compliant", "Non-compliant"
        CLARIFICATION = "Request clarification", "Request clarification"

    finding_id = models.CharField(max_length=100, primary_key=True)
    decision = models.CharField(max_length=32, choices=Decision.choices)
    note = models.TextField(max_length=4000)
    reviewer = models.CharField(max_length=180)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class AuditEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.CharField(max_length=120)
    actor = models.CharField(max_length=180)
    target = models.CharField(max_length=240)
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
