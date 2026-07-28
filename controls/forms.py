from django import forms
from django.utils import timezone
from .models import ControlCycle, PackageUpload, ReconciliationRow


class CycleForm(forms.ModelForm):
    cutoff_at = forms.DateTimeField(
        initial=timezone.now,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )

    class Meta:
        model = ControlCycle
        fields = ["name", "walmart_week", "cutoff_at", "notes"]


class UploadForm(forms.ModelForm):
    class Meta:
        model = PackageUpload
        fields = ["package_number", "source_file", "extracted_at", "report_id", "filters"]
        widgets = {
            "extracted_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "filters": forms.Textarea(attrs={"rows": 2}),
        }


class DecisionForm(forms.ModelForm):
    class Meta:
        model = ReconciliationRow
        fields = ["decision_status", "recommendation", "decision_note"]
        widgets = {
            "recommendation": forms.Textarea(attrs={"rows": 3}),
            "decision_note": forms.Textarea(attrs={"rows": 3}),
        }
