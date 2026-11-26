from django.urls import path

from .views import (
    AuditListView,
    BidDetailView,
    BidDocumentDetailView,
    BidDocumentView,
    BidListCreateView,
    HealthView,
    JobListView,
    ReviewView,
    VerificationJobView,
)

urlpatterns = [
    path("health", HealthView.as_view(), name="health"),
    path("bids", BidListCreateView.as_view(), name="bid-list-create"),
    path("bids/<str:bid_id>", BidDetailView.as_view(), name="bid-detail"),
    path("bids/<str:bid_id>/documents", BidDocumentView.as_view(), name="bid-documents"),
    path("bids/<str:bid_id>/documents/<str:document_id>", BidDocumentDetailView.as_view(), name="bid-document-detail"),
    path("bids/<str:bid_id>/verify", VerificationJobView.as_view(), name="verification-jobs"),
    path("jobs", JobListView.as_view(), name="job-list"),
    path("reviews/<str:finding_id>", ReviewView.as_view(), name="review-detail"),
    path("audit-logs", AuditListView.as_view(), name="audit-logs"),
]
