from interactions.models import Report


def admin_context(request):
    if request.user.is_authenticated and request.user.is_campus_admin:
        return {
            "reports_count": Report.objects.filter(status=Report.STATUS_OPEN).count(),
        }
    return {}