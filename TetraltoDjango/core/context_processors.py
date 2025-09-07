from django.conf import settings
from .models import SocialLink

def settings_context(request):
    """
    Make Django settings available in templates.
    This includes both GOOGLE_ANALYTICS_ID and GTM_CONTAINER_ID.
    """
    return {"settings": settings}

def social_links_context(request):
    """Make social links available to all templates automatically."""
    return {
        'social_links': SocialLink.objects.filter(is_active=True).order_by('order')
    }