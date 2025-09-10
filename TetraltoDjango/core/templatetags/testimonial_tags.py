from django import template

register = template.Library()

@register.inclusion_tag('testimonials/carousel.html')
def testimonials_carousel(carousel_id="testimonials-carousel", filter_featured=None):
    """
    Lightweight Django inclusion tag for displaying testimonials carousel.
    Uses global testimonials data loaded by context processor.
    
    Usage:
        {% load testimonial_tags %}
        {% testimonials_carousel carousel_id="featured-carousel" filter_featured=True %}
        {% testimonials_carousel carousel_id="recent-carousel" %}
    
    Args:
        carousel_id (str): Unique ID for the carousel container
        filter_featured (bool): If True, JavaScript will filter to only featured testimonials
    
    Returns:
        dict: Simple context with carousel configuration
    """
    return {
        'carousel_id': carousel_id,
        'filter_featured': filter_featured,
    }