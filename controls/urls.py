from django.urls import path
from . import views

app_name = "controls"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("cycles/new/", views.cycle_create, name="cycle_create"),
    path("cycles/<int:pk>/", views.cycle_detail, name="cycle_detail"),
    path("cycles/<int:pk>/upload/", views.package_upload, name="package_upload"),
    path("templates/packages/<int:package_number>/blank.xlsx", views.package_template, name="package_template"),
    path("templates/packages/mapping/", views.package_mapping, name="package_mapping"),
    path("cycles/<int:pk>/run/", views.run_reconciliation, name="run_reconciliation"),
    path("cycles/<int:pk>/export.xlsx", views.export_excel, name="export_excel"),
    path("cycles/<int:pk>/report/", views.print_report, name="print_report"),
    path("rows/<int:pk>/decision/", views.update_decision, name="update_decision"),
]
