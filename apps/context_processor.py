from apps.models import SiteSetting


def site_settings(request):
    _site = SiteSetting.objects.first()
    return {"setting": _site}
