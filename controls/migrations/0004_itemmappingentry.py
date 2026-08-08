from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("controls", "0003_reconciliationrow_actual_orders_l4_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ItemMappingEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("internal_sku", models.CharField(max_length=80)),
                ("proposed_alias", models.CharField(blank=True, max_length=80)),
                ("walmart_item_number", models.CharField(blank=True, max_length=40)),
                ("gtin", models.CharField(blank=True, max_length=40)),
                ("status", models.CharField(choices=[("PROVISIONAL", "Provisional"), ("UNRESOLVED", "Unresolved")], max_length=12)),
                ("confidence", models.CharField(choices=[("MEDIUM", "Medium"), ("LOW", "Low")], max_length=8)),
                ("evidence", models.TextField()),
                ("required_action", models.TextField()),
                ("cycle", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mapping_entries", to="controls.controlcycle")),
            ],
            options={
                "ordering": ["status", "internal_sku"],
                "unique_together": {("cycle", "internal_sku")},
            },
        ),
    ]
