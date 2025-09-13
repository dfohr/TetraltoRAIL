from django import template
from django.utils.safestring import mark_safe
from core.models import Testimonial
import json

register = template.Library()

@register.simple_tag(takes_context=True)
def set_testimonial_filter(context, is_featured=True, is_active=True, **kwargs):
    """
    Set testimonial filtering for entire page. All carousels will use this filter.
    
    Usage:
        {% load testimonial_tags %}
        {% set_testimonial_filter is_featured=True %}
        {% testimonials_carousel carousel_id="carousel1" %}
        {% testimonials_carousel carousel_id="carousel2" %}
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
    
    # Store filtered testimonials in context
    context['filtered_testimonials'] = testimonials
    
    return ""  # Don't output anything

@register.inclusion_tag('testimonials/carousel.html', takes_context=True)
def testimonials_carousel(context, carousel_id="testimonials-carousel"):
    """
    Display testimonials carousel using pre-filtered testimonials from context.
    Use {% set_testimonial_filter %} first to define the filtering.
    
    Usage:
        {% load testimonial_tags %}
        {% set_testimonial_filter is_featured=True %}
        {% testimonials_carousel carousel_id="carousel1" %}
        {% testimonials_carousel carousel_id="carousel2" %}
    
    Args:
        carousel_id (str): Unique ID for the carousel container
    
    Returns:
        dict: Context with filtered testimonials data and carousel configuration
    """
    # Get filtered testimonials from context (set by set_testimonial_filter)
    testimonials = context.get('filtered_testimonials', Testimonial.objects.filter(is_active=True).order_by('-created_at'))
    
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

@register.simple_tag
def testimonials_jsonld_seo():
    """
    Generate JSON-LD structured data for featured testimonials for SEO.
    Only includes is_featured=True testimonials to avoid duplicate indexing.
    
    Returns properly formatted JSON-LD Review objects for search engines.
    """
    featured_testimonials = Testimonial.objects.filter(is_active=True, is_featured=True)
    
    reviews_data = []
    for testimonial in featured_testimonials:
        review_data = {
            "@type": "Review",
            "author": {
                "@type": "Person",
                "name": testimonial.name,
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": testimonial.city
                }
            },
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": testimonial.rating,
                "bestRating": 5,
                "worstRating": 1
            },
            "reviewBody": testimonial.text,
            "itemReviewed": {
                "@type": "LocalBusiness",
                "name": "Tetralto Roofing",
                "@id": "https://tetralto.com",
                "url": "https://tetralto.com",
                "telephone": "281-895-1213",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "Missouri City",
                    "addressLocality": "Missouri City",
                    "addressRegion": "TX",
                    "addressCountry": "US"
                }
            },
            "url": testimonial.url,
            "datePublished": testimonial.created_at.isoformat()
        }
        reviews_data.append(review_data)
    
    # Wrap in structured data format
    structured_data = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "itemListElement": []
    }
    
    for index, review in enumerate(reviews_data):
        structured_data["itemListElement"].append({
            "@type": "ListItem",
            "position": index + 1,
            "item": review
        })
    
    return mark_safe(json.dumps(structured_data, indent=2))