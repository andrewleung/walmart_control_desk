from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from controls.models import ControlCycle, PackageUpload
from controls.services import process_upload, run_controls


class Command(BaseCommand):
    help = "Load the clearly labeled, complete synthetic demonstration cycle."

    def handle(self, *args, **options):
        source_root = Path(settings.BASE_DIR) / "demo_data" / "synthetic"
        sources = [
            (1, "P01_Store_Sales_Inventory_SYNTHETIC.xlsx"),
            (2, "P02_eCommerce_Sales_SYNTHETIC.xlsx"),
            (3, "P03_eCommerce_Inventory_SYNTHETIC.xlsx"),
            (4, "P04_Store_Demand_Forecast_SYNTHETIC.xlsx"),
            (5, "P05_Order_Forecast_SYNTHETIC.xlsx"),
            (6, "P06_Confirmed_PO_Receipts_OTIF_SYNTHETIC.xlsx"),
            (7, "P07_Factory_Production_SYNTHETIC.xlsx"),
            (8, "P08_RJW_Inventory_Inbound_SYNTHETIC.xlsx"),
            (9, "P09_Walmart_Context_Exceptions_SYNTHETIC.xlsx"),
        ]
        missing = [name for _, name in sources if not (source_root / name).exists()]
        if missing:
            raise CommandError("Missing synthetic source files: " + ", ".join(missing))

        cutoff = timezone.make_aware(datetime(2026, 7, 31, 9, 0))
        cycle, _ = ControlCycle.objects.get_or_create(
            name="Synthetic complete workflow demo",
            walmart_week="202630",
            defaults={
                "cutoff_at": cutoff,
                "prepared_by": "Jessica",
                "is_synthetic": True,
                "notes": "Made-up, internally consistent demonstration data. Not for operational use.",
            },
        )
        cycle.cutoff_at = cutoff
        cycle.prepared_by = "Jessica"
        cycle.is_synthetic = True
        cycle.notes = "Made-up, internally consistent demonstration data. Not for operational use."
        cycle.save()

        for package_number, filename in sources:
            existing = cycle.uploads.filter(
                package_number=package_number, original_name=filename, status="POPULATED"
            ).first()
            if existing:
                self.stdout.write(f"Package {package_number} already populated.")
                continue
            path = source_root / filename
            with path.open("rb") as handle:
                upload = PackageUpload(
                    cycle=cycle,
                    package_number=package_number,
                    original_name=filename,
                    extracted_at=cutoff,
                    report_id=f"SYNTHETIC-P{package_number:02d}-202630",
                    filters="Synthetic Walmart week 202630; all three demonstration SKUs.",
                )
                upload.source_file.save(filename, File(handle), save=True)
            process_upload(upload)
            if upload.status != "POPULATED":
                raise CommandError(
                    f"Package {package_number} did not populate: {upload.validation_message}"
                )
            self.stdout.write(f"Package {package_number}: populated ({upload.row_count} rows)")

        run_controls(cycle)
        self.stdout.write(self.style.SUCCESS(
            f"Synthetic demo ready: {cycle.status}, {cycle.rows.count()} items, "
            f"{cycle.exceptions.count()} exception(s)."
        ))
