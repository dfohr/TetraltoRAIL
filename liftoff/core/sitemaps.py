from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogPost

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return ['home', 'services', 'contact', 'blog']

    def location(self, item):
        return reverse(item)

    def lastmod(self, obj):
        # Add specific last modified dates for each page
        if obj == 'blog':
            return None  # Will be updated when blog is active
        return None  # Default to server's Last-Modified header

    def priority(self, item):
        # Customize priority for different pages
        priorities = {
            'home': 1.0,
            'services': 0.8,
            'contact': 0.6,
            'blog': 0.4
        }
        return priorities.get(item, 0.5)

class BlogPostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6
    protocol = 'https'

    def items(self):
        return BlogPost.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at or obj.created_at

    def location(self, obj):
        return reverse('blog_post', args=[obj.slug]) 