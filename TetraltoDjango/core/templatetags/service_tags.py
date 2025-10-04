from django import template
from django.shortcuts import get_object_or_404
from ..models import Service

register = template.Library()

@register.inclusion_tag('_service_tile.html')
def service_tile(identifier):
    """
    Render a service tile for the given identifier.
    
    Args:
        identifier: Service slug, ID, or title to display
    
    Usage:
        {% load service_tags %}
        {% service_tile "roof-replacement" %}
        {% service_tile 1 %}
    """
    # Try to get by slug first
    try:
        if isinstance(identifier, int) or identifier.isdigit():
            service = get_object_or_404(Service, pk=int(identifier))
        else:
            # Try slug first, then fallback to title
            try:
                service = get_object_or_404(Service, slug=identifier)
            except:
                service = get_object_or_404(Service, title__iexact=identifier)
    except:
        service = None
    
    return {
        'service': service
    }
