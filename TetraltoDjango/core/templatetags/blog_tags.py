from django import template
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.templatetags.static import static
from django.urls import reverse
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


@register.filter(name='drive_url')
def drive_url(value):
    """
    Convert drive: references to blog image proxy URLs, or return static file path.
    
    Usage:
        {% load blog_tags %}
        <img src="{{ post.hero_image_filename|drive_url }}">
    
    Examples:
        'drive:sienna-legacy-1' -> '/blog/images/sienna-legacy-1/'
        'blog-hero.avif' -> '/static/images/blog-hero.avif'
    """
    if not value:
        return ''
    
    # Check if it's a drive: reference
    if value.startswith('drive:'):
        tag = value[6:]  # Remove 'drive:' prefix
        return reverse('blog_proxy_image', kwargs={'tag': tag})
    
    # Otherwise, return static file path
    return static(f'images/{value}')