from django.db import models


class ControlCycle(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("BLOCKED", "Blocked"),
        ("READY", "Ready for review"),
        ("COMPLETE", "Complete"),
    ]
    name = models.CharField(max_length=120)
    walmart_week = models.CharField(max_length=6)
    cutoff_at = models.DateTimeField()
    prepared_by = models.CharField(max_length=80, default="Jessica")
    is_synthetic = models.BooleanField(default=False)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="DRAFT")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-cutoff_at"]

    def __str__(self):
        return f"{self.name} · {self.walmart_week}"


class PackageUpload(models.Model):
    PACKAGE_CHOICES = [
        (1, "Store Sales & Inventory"),
        (2, "eCommerce Sales"),
        (3, "eCommerce Inventory"),
        (4, "Store Demand Forecast"),
        (5, "Order Forecast"),
        (6, "Confirmed POs, Receipts & OTIF"),
        (7, "Factory Production & Finished Goods"),
        (8, "Import, RJW Inventory & Shipments"),
        (9, "Walmart Context & Exceptions"),
    ]
    STATUS_CHOICES = [
        ("UPLOADED", "Uploaded"),
        ("PROCESSING", "Processing"),
        ("POPULATED", "Populated"),
        ("PARTIAL", "Partial"),
        ("STALE", "Requires refresh"),
        ("MISSING", "Data missing"),
        ("ERROR", "Validation error"),
    ]
    cycle = models.ForeignKey(ControlCycle, on_delete=models.CASCADE, related_name="uploads")
    package_number = models.PositiveSmallIntegerField(choices=PACKAGE_CHOICES)
    source_file = models.FileField(upload_to="sources/%Y/%m/")
    original_name = models.CharField(max_length=255)
    extracted_at = models.DateTimeField(null=True, blank=True)
    report_id = models.CharField(max_length=120, blank=True)
    filters = models.TextField(blank=True)
    status = models.CharField(max_length=14, choices=STATUS_CHOICES, default="UPLOADED")
    validation_message = models.TextField(blank=True)
    row_count = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["package_number", "-uploaded_at"]


class SKU(models.Model):
    vendor_stock_id = models.CharField(max_length=80, unique=True)
    item_name = models.CharField(max_length=255, blank=True)
    walmart_item_number = models.CharField(max_length=40, blank=True)
    all_links_item_number = models.CharField(max_length=40, blank=True)
    consumer_id = models.CharField(max_length=40, blank=True)
    gtin = models.CharField(max_length=40, blank=True)
    pack_quantity = models.DecimalField(max_digits=12, decimal_places=3, default=1)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["vendor_stock_id"]

    def __str__(self):
        return self.vendor_stock_id


class ReconciliationRow(models.Model):
    DECISION_CHOICES = [
        ("BLOCKED", "Blocked"),
        ("MONITOR", "Monitor"),
        ("INVESTIGATE", "Investigate"),
        ("RECOMMEND", "Recommend"),
        ("RECORDED", "Decision recorded"),
    ]
    cycle = models.ForeignKey(ControlCycle, on_delete=models.CASCADE, related_name="rows")
    sku = models.ForeignKey(SKU, on_delete=models.PROTECT)
    store_pos_units = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    store_pos_sales = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    store_on_hand = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    store_on_order = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    replen_instock = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    ecomm_units = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    ecomm_sales = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    forecast_demand_4w = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    forecast_demand_13w = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    order_forecast_total = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    first_forecast_arrival = models.DateField(null=True, blank=True)
    last_forecast_arrival = models.DateField(null=True, blank=True)
    next_mabd = models.DateField(null=True, blank=True)
    ecomm_available_inventory = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    factory_available_inventory = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    rjw_available_inventory = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    current_commitments = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    usable_supply = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    confirmed_on_time_inbound = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    late_inbound_quantity = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    next_inbound_available = models.DateField(null=True, blank=True)
    approved_buffer = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    projected_ending_supply = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    projected_gap = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    decision_status = models.CharField(max_length=14, choices=DECISION_CHOICES, default="BLOCKED")
    recommendation = models.TextField(blank=True)
    decision_note = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("cycle", "sku")]
        ordering = ["sku__vendor_stock_id"]

    @property
    def diagnostic_wos(self):
        if self.store_pos_units and self.store_on_hand is not None:
            return self.store_on_hand / self.store_pos_units
        return None

    @property
    def replen_instock_percent(self):
        if self.replen_instock is None:
            return None
        return self.replen_instock * 100

    @property
    def missing_critical(self):
        return any(v is None for v in [
            self.current_commitments,
            self.usable_supply,
            self.confirmed_on_time_inbound,
        ])


class ExceptionRecord(models.Model):
    SEVERITY_CHOICES = [("CRITICAL", "Critical"), ("HIGH", "High"), ("MEDIUM", "Medium")]
    STATUS_CHOICES = [("OPEN", "Open"), ("RESOLVED", "Resolved"), ("ACCEPTED", "Accepted")]
    cycle = models.ForeignKey(ControlCycle, on_delete=models.CASCADE, related_name="exceptions")
    sku = models.ForeignKey(SKU, on_delete=models.PROTECT, null=True, blank=True)
    code = models.CharField(max_length=80)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=200)
    effect = models.TextField()
    required_action = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="OPEN")
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["severity", "code"]
