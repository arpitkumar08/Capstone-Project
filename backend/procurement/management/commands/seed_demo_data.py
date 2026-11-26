from django.core.management.base import BaseCommand

from procurement.models import Bid


SEED_BIDS = [
    ("BID-2025-0842", "GEM/2025/B/5842190", "Supply of 250 kVA Diesel Generator Sets", "Ministry of Railways", "2025-02-18", "Needs review", 4, 86),
    ("BID-2025-0837", "GEM/2025/B/5839072", "Enterprise Network Switches · 48 Port", "National Informatics Centre", "2025-02-21", "Processing", 6, 62),
    ("BID-2025-0829", "GEM/2025/B/5828641", "Laboratory Grade Water Purification System", "IIT Delhi", "2025-02-24", "Completed", 3, 100),
    ("BID-2025-0816", "GEM/2025/B/5817730", "Annual Maintenance · HVAC Equipment", "AIIMS New Delhi", "2025-02-28", "Draft", 2, 0),
    ("BID-2025-0804", "GEM/2025/B/5802291", "Desktop Workstations for Regional Offices", "Ministry of Finance", "2025-03-04", "Completed", 5, 100),
]


class Command(BaseCommand):
    help = "Create the sample bids used by the frontend demo. Safe to run more than once."

    def handle(self, *args, **options):
        created = 0
        for bid_id, reference, title, department, deadline, state, vendors, progress in SEED_BIDS:
            _, was_created = Bid.objects.get_or_create(
                id=bid_id,
                defaults={
                    "reference": reference,
                    "title": title,
                    "department": department,
                    "deadline": deadline,
                    "status": state,
                    "vendors": vendors,
                    "progress": progress,
                },
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Demo seed complete: {created} bid(s) created."))
