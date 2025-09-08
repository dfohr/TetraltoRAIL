from django import template
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ..models import BlogPost

register = template.Library()

@register.inclusion_tag('_blog_tile.html')
def blog_tile(slug, variant='default'):
    """
    Render a blog tile for the given slug.
    
    Args:
        slug: Blog post slug to display
        variant: Style variant ('default', 'card', 'compact')
    
    Usage:
        {% load blog_tags %}
        {% blog_tile "my-blog-post" %}
        {% blog_tile "my-blog-post" "card" %}
    """
    post = get_object_or_404(
        BlogPost,
        slug=slug,
        is_active=True,
        published_at__lte=timezone.now()
    )
    
    css_class = f"blog-tile {variant}" if variant != 'default' else "blog-tile"
    
    return {
        'post': post,
        'css_class': css_class
    }