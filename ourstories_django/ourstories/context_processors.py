from django.conf import settings

def api_keys(request):
    return { "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY }
