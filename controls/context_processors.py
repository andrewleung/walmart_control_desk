from django.conf import settings


def deployment_mode(request):
    return {
        "demo_read_only": settings.DEMO_READ_ONLY,
        "synthetic_only": settings.SYNTHETIC_ONLY,
    }
