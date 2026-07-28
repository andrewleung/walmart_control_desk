from datetime import datetime
from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import ControlCycle, ReconciliationRow, SKU
from .services import run_controls


class ControlGateTests(TestCase):
    def setUp(self):
        self.cycle = ControlCycle.objects.create(
            name="Test cycle",
            walmart_week="202623",
            cutoff_at=timezone.make_aware(datetime(2026, 7, 24, 20, 40)),
        )
        self.sku = SKU.objects.create(vendor_stock_id="TEST-1", item_name="Test item")
        self.row = ReconciliationRow.objects.create(
            cycle=self.cycle,
            sku=self.sku,
            store_on_hand=Decimal("100"),
        )

    def test_missing_supply_blocks_calculation(self):
        run_controls(self.cycle)
        self.row.refresh_from_db()
        self.cycle.refresh_from_db()
        self.assertEqual(self.cycle.status, "BLOCKED")
        self.assertEqual(self.row.decision_status, "BLOCKED")
        self.assertIsNone(self.row.projected_gap)

    def test_complete_row_calculates_projected_gap(self):
        self.row.current_commitments = Decimal("80")
        self.row.usable_supply = Decimal("100")
        self.row.confirmed_on_time_inbound = Decimal("30")
        self.row.approved_buffer = Decimal("10")
        self.row.save()
        run_controls(self.cycle)
        self.row.refresh_from_db()
        self.assertEqual(self.row.projected_ending_supply, Decimal("50"))
        self.assertEqual(self.row.projected_gap, Decimal("40"))

    def test_main_pages_and_export_render(self):
        self.assertEqual(self.client.get(reverse("controls:dashboard")).status_code, 200)
        self.assertEqual(
            self.client.get(reverse("controls:cycle_detail", args=[self.cycle.pk])).status_code,
            200,
        )
        detail = self.client.get(reverse("controls:update_decision", args=[self.row.pk]))
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "Projected-gap calculation")
        response = self.client.get(reverse("controls:export_excel", args=[self.cycle.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b"PK"))

    @override_settings(DEMO_READ_ONLY=True, SYNTHETIC_ONLY=True)
    def test_public_demo_hides_real_cycle_and_blocks_changes(self):
        synthetic = ControlCycle.objects.create(
            name="Synthetic cycle",
            walmart_week="202630",
            cutoff_at=timezone.make_aware(datetime(2026, 7, 31, 9, 0)),
            is_synthetic=True,
        )
        dashboard = self.client.get(reverse("controls:dashboard"))
        self.assertContains(dashboard, "Synthetic cycle")
        self.assertNotContains(dashboard, "Test cycle")
        self.assertEqual(
            self.client.get(reverse("controls:cycle_detail", args=[self.cycle.pk])).status_code,
            404,
        )
        self.assertEqual(self.client.get(reverse("controls:cycle_create")).status_code, 403)
        self.assertEqual(
            self.client.post(reverse("controls:run_reconciliation", args=[synthetic.pk])).status_code,
            403,
        )
