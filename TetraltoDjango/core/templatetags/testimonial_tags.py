from django import template
from django.utils.safestring import mark_safe
from core.models import Testimonial
import json

register = template.Library()

@register.inclusion_tag('testimonials/carousel.html')
def testimonials_carousel(carousel_id="testimonials-carousel", is_active=True, is_featured=None, **kwargs):
    """
    Django inclusion tag for displaying filtered testimonials carousel.
    Filtering happens at Django level, component just displays the data.
    
    Usage:
        {% load testimonial_tags %}
        {% testimonials_carousel carousel_id="featured-carousel" is_featured=True %}
        {% testimonials_carousel carousel_id="recent-carousel" is_active=True %}
        {% testimonials_carousel carousel_id="all-carousel" %}
    
    Args:
        carousel_id (str): Unique ID for the carousel container
        is_active (bool): Filter by active status (default: True)
        is_featured (bool): Filter by featured status (if specified)
        **kwargs: Future filter parameters (roof_replacement, etc.)
    
    Returns:
        dict: Context with filtered testimonials data and carousel configuration
    """
    # Start with base queryset
    queryset = Testimonial.objects.all()
    
    # Apply is_active filter (default True)
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)
    
    # Apply is_featured filter if specified
    if is_featured is not None:
        queryset = queryset.filter(is_featured=is_featured)
    
    # Apply any additional future filters from kwargs
    for field, value in kwargs.items():
        if hasattr(Testimonial, field) and value is not None:
            queryset = queryset.filter(**{field: value})
    
    # Order by creation date (newest first)
    testimonials = queryset.order_by('-created_at')
    
    # Convert to JSON for JavaScript
    testimonials_json = []
    for testimonial in testimonials:
        testimonials_json.append({
            'id': testimonial.id,
            'name': testimonial.name,
            'text': testimonial.text,
            'city': testimonial.city,
            'service': testimonial.service,
            'rating': testimonial.rating,
            'url': testimonial.url,
            'created_at': testimonial.created_at.isoformat(),
            'is_featured': testimonial.is_featured
        })
    
    return {
        'carousel_id': carousel_id,
        'testimonials': testimonials,
        'testimonials_json': mark_safe(json.dumps(testimonials_json)),
        'total_count': testimonials.count(),
    }