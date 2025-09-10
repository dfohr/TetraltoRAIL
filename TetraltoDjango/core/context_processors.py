from django.conf import settings
from .models import SocialLink, Testimonial
from django.utils.safestring import mark_safe
import json

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

def testimonials_data_context(request):
    """
    Context processor that provides testimonials data globally.
    Creates centralized data source for all carousels on the page.
    """
    # Load all active testimonials once per request
    testimonials = Testimonial.objects.filter(is_active=True).order_by('-created_at')
    
    # Prepare Schema.org JSON-LD markup for SEO
    schema_reviews = []
    testimonials_json = []
    
    for testimonial in testimonials:
        # Schema.org markup
        schema_review = {
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
                "bestRating": 5,
                "worstRating": 1
            },
            "itemReviewed": {
                "@type": "Service",
                "name": testimonial.service,
                "provider": {
                    "@type": "Organization",
                    "name": "Tetralto Roofing"
                }
            },
            "datePublished": testimonial.created_at.isoformat(),
            "url": testimonial.url
        }
        schema_reviews.append(schema_review)
        
        # JavaScript data
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
    
    # Complete Schema.org structure
    schema_data = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": idx + 1,
                "item": review
            }
            for idx, review in enumerate(schema_reviews)
        ]
    }
    
    return {
        'testimonials_list': testimonials,
        'testimonials_schema': mark_safe(json.dumps(schema_data, indent=2)),
        'testimonials_json': mark_safe(json.dumps(testimonials_json))
    }