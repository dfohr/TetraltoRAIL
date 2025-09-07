from django import template
from ..models import SocialLink

register = template.Library()

@register.inclusion_tag('_social_bar.html')
def social_bar():
    """Render social bar with its own data - no view dependency needed."""
    return {
        'social_links': SocialLink.objects.filter(is_active=True).order_by('order')
    }