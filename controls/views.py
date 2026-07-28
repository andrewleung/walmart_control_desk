from io import BytesIO
from pathlib import Path

from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from .forms import CycleForm, DecisionForm, UploadForm
from .models import ControlCycle, PackageUpload, ReconciliationRow
from .services import process_upload, run_controls
from .template_schemas import PACKAGE_TEMPLATE_SCHEMAS


def dashboard(request):
    cycles = ControlCycle.objects.prefetch_related("uploads", "exceptions").all()
    if settings.SYNTHETIC_ONLY:
        cycles = cycles.filter(is_synthetic=True)
    return render(request, "controls/dashboard.html", {"cycles": cycles})


def cycle_create(request):
    if settings.DEMO_READ_ONLY:
        return HttpResponseForbidden("This public synthetic demonstration is read-only.")
    form = CycleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cycle = form.save(commit=False)
        cycle.prepared_by = "Jessica"
        cycle.save()
        messages.success(request, "Control cycle created.")
        return redirect("controls:cycle_detail", pk=cycle.pk)
    return render(request, "controls/cycle_form.html", {"form": form})


def cycle_detail(request, pk):
    queryset = ControlCycle.objects.all()
    if settings.SYNTHETIC_ONLY:
        queryset = queryset.filter(is_synthetic=True)
    cycle = get_object_or_404(queryset, pk=pk)
    packages = []
    latest = {}
    for upload in cycle.uploads.all():
        latest.setdefault(upload.package_number, upload)
    for number, label in PackageUpload.PACKAGE_CHOICES:
        packages.append({"number": number, "label": label, "upload": latest.get(number)})
    return render(request, "controls/cycle_detail.html", {
        "cycle": cycle,
        "packages": packages,
        "rows": cycle.rows.select_related("sku"),
        "exceptions": cycle.exceptions.select_related("sku"),
    })


def package_upload(request, pk):
    if settings.DEMO_READ_ONLY:
        return HttpResponseForbidden("This public synthetic demonstration is read-only.")
    cycle = get_object_or_404(ControlCycle, pk=pk)
    initial = {"package_number": request.GET.get("package")}
    form = UploadForm(request.POST or None, request.FILES or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        upload = form.save(commit=False)
        upload.cycle = cycle
        upload.original_name = request.FILES["source_file"].name
        upload.save()
        process_upload(upload)
        if upload.status == "ERROR":
            messages.error(request, upload.validation_message)
        else:
            messages.success(request, f"Package {upload.package_number} uploaded: {upload.validation_message}")
        return redirect("controls:cycle_detail", pk=cycle.pk)
    return render(request, "controls/upload_form.html", {"cycle": cycle, "form": form})


def package_template(request, package_number):
    labels = dict(PackageUpload.PACKAGE_CHOICES)
    schema = PACKAGE_TEMPLATE_SCHEMAS.get(package_number)
    if not schema or package_number not in labels:
        return HttpResponse(status=404)

    book = Workbook()
    data = book.active
    data.title = "Data Upload"
    headers = [column for column, _required, _guidance in schema]
    data.append(headers)
    for cell in data[1]:
        cell.fill = PatternFill("solid", fgColor="17365D")
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(wrap_text=True)
    data.freeze_panes = "A2"
    data.auto_filter.ref = f"A1:{get_column_letter(len(headers))}1"
    for index, header in enumerate(headers, 1):
        data.column_dimensions[get_column_letter(index)].width = min(max(len(header) + 3, 18), 42)

    instructions = book.create_sheet("Instructions")
    instructions.append([f"P{package_number:02d}", labels[package_number]])
    instructions.append(["Purpose", "Enter one source record per row on the Data Upload sheet. Do not rename the columns."])
    instructions.append(["Dates", "Use YYYY-MM-DD. Walmart weeks use YYYYYY, for example 202630."])
    instructions.append(["Required fields", "Every required column must remain present; values should be completed for each applicable row."])
    instructions.append([])
    instructions.append(["Column", "Required?", "Meaning / format"])
    for column, required, guidance in schema:
        instructions.append([column, "Yes" if required else "No", guidance])
    for cell in instructions[6]:
        cell.fill = PatternFill("solid", fgColor="17365D")
        cell.font = Font(color="FFFFFF", bold=True)
    instructions.column_dimensions["A"].width = 42
    instructions.column_dimensions["B"].width = 14
    instructions.column_dimensions["C"].width = 78
    instructions.freeze_panes = "A7"

    output = BytesIO()
    book.save(output)
    filename = f"P{package_number:02d}_blank_upload_template.xlsx"
    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@require_POST
def run_reconciliation(request, pk):
    if settings.DEMO_READ_ONLY:
        return HttpResponseForbidden("This public synthetic demonstration is read-only.")
    cycle = get_object_or_404(ControlCycle, pk=pk)
    run_controls(cycle)
    messages.success(request, "Reconciliation and exception controls completed.")
    return redirect("controls:cycle_detail", pk=cycle.pk)


def update_decision(request, pk):
    row = get_object_or_404(ReconciliationRow, pk=pk)
    if settings.SYNTHETIC_ONLY and not row.cycle.is_synthetic:
        return HttpResponseForbidden("Only the synthetic demonstration is available.")
    if request.method == "POST" and settings.DEMO_READ_ONLY:
        return HttpResponseForbidden("This public synthetic demonstration is read-only.")
    form = DecisionForm(request.POST or None, instance=row)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Decision note updated for {row.sku.vendor_stock_id}.")
        return redirect("controls:cycle_detail", pk=row.cycle_id)
    return render(request, "controls/decision_form.html", {"row": row, "form": form})


def export_excel(request, pk):
    queryset = ControlCycle.objects.all()
    if settings.SYNTHETIC_ONLY:
        queryset = queryset.filter(is_synthetic=True)
    cycle = get_object_or_404(queryset, pk=pk)
    book = Workbook()
    sheet = book.active
    sheet.title = "Reconciliation"
    headers = [
        "SKU", "Item", "Store POS Units", "Store POS Sales", "Store On Hand",
        "Store On Order", "Replen In-stock", "eComm Units", "eComm Sales",
        "4W Store Demand", "13W Store Demand", "Order Forecast", "First Arrival",
        "Last Arrival", "Current Commitments", "Usable Supply", "On-time Inbound",
        "Approved Buffer", "Projected Ending", "Projected Gap", "Decision Status",
        "Recommendation", "Decision Note",
    ]
    header_row = 1
    if cycle.is_synthetic:
        sheet.append(["SYNTHETIC DEMONSTRATION DATA — NOT FOR OPERATIONAL USE"])
        sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
        sheet["A1"].fill = PatternFill("solid", fgColor="FFF0C9")
        sheet["A1"].font = Font(color="8A5A00", bold=True, size=14)
        sheet.append([])
        header_row = 3
    sheet.append(headers)
    for cell in sheet[header_row]:
        cell.fill = PatternFill("solid", fgColor="17365D")
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(wrap_text=True)
    for row in cycle.rows.select_related("sku"):
        sheet.append([
            row.sku.vendor_stock_id, row.sku.item_name, row.store_pos_units, row.store_pos_sales,
            row.store_on_hand, row.store_on_order, row.replen_instock, row.ecomm_units,
            row.ecomm_sales, row.forecast_demand_4w, row.forecast_demand_13w,
            row.order_forecast_total, row.first_forecast_arrival, row.last_forecast_arrival,
            row.current_commitments, row.usable_supply, row.confirmed_on_time_inbound,
            row.approved_buffer, row.projected_ending_supply, row.projected_gap,
            row.get_decision_status_display(), row.recommendation, row.decision_note,
        ])
    sheet.freeze_panes = f"A{header_row + 1}"
    sheet.auto_filter.ref = sheet.dimensions
    widths = [14, 28, 15, 16, 15, 15, 14, 14, 14, 16, 16, 16, 15, 15, 18, 15, 16, 15, 16, 15, 16, 30, 30]
    for i, width in enumerate(widths, 1):
        sheet.column_dimensions[get_column_letter(i)].width = width
    exceptions = book.create_sheet("Exceptions")
    exceptions.append(["Severity", "SKU", "Code", "Exception", "Effect", "Required Action", "Status", "Note"])
    for cell in exceptions[1]:
        cell.fill = PatternFill("solid", fgColor="17365D")
        cell.font = Font(color="FFFFFF", bold=True)
    for item in cycle.exceptions.select_related("sku"):
        exceptions.append([
            item.severity, item.sku.vendor_stock_id if item.sku else "", item.code,
            item.title, item.effect, item.required_action, item.status, item.note,
        ])
    output = BytesIO()
    book.save(output)
    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="walmart-control-{cycle.walmart_week}.xlsx"'
    return response


def print_report(request, pk):
    queryset = ControlCycle.objects.all()
    if settings.SYNTHETIC_ONLY:
        queryset = queryset.filter(is_synthetic=True)
    cycle = get_object_or_404(queryset, pk=pk)
    return render(request, "controls/print_report.html", {
        "cycle": cycle,
        "rows": cycle.rows.select_related("sku"),
        "exceptions": cycle.exceptions.select_related("sku"),
    })
