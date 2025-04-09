from django.conf import settings

def settings_context(request):
    """
    Make Django settings available in templates.
    This includes both GOOGLE_ANALYTICS_ID and GTM_CONTAINER_ID.
    """
    return {"settings": settings}