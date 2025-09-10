from django import template
from django.utils.safestring import mark_safe
from core.models import Testimonial
import json

register = template.Library()

@register.inclusion_tag('testimonials/carousel.html')
def import_testimonials(carousel_id="testimonials-carousel", is_featured=None):
    """
    Django inclusion tag for displaying testimonials carousel with SEO optimization.
    
    Usage:
        {% load testimonial_tags %}
        {% import_testimonials carousel_id="test-carousel" is_featured=True %}
    
    Args:
        carousel_id (str): Unique ID for the carousel container
        is_featured (bool): If True, filter only featured testimonials. If None, get all active testimonials.
    
    Returns:
        dict: Context with testimonials data and carousel configuration
    """
    # Base queryset - only active testimonials
    queryset = Testimonial.objects.filter(is_active=True)
    
    # Apply is_featured filter if specified
    if is_featured is not None:
        queryset = queryset.filter(is_featured=is_featured)
    
    # Order by creation date (newest first for better display)
    testimonials = queryset.order_by('-created_at')
    
    # Prepare JSON-LD schema data for SEO
    schema_data = []
    for testimonial in testimonials:
        schema_item = {
            "@type": "Review",
            "author": {
                "@type": "Person",
                "name": testimonial.name,
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": testimonial.city
                }
            },
            "reviewBody": testimonial.text,
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": testimonial.rating,
                "bestRating": 5
            },
            "datePublished": testimonial.created_at.isoformat(),
            "url": testimonial.url
        }
        schema_data.append(schema_item)
    
    return {
        'testimonials': testimonials,
        'carousel_id': carousel_id,
        'schema_data': mark_safe(json.dumps(schema_data, indent=2)),
        'total_count': testimonials.count(),
    }