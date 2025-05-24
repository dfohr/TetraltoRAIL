from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogPost, Service

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return ['home', 'services', 'contact', 'blog']

    def location(self, item):
        return reverse(item)

    def get_urls(self, page=1, site=None, protocol=None):
        urls = super().get_urls(page=1, site=None, protocol=None)
        # Filter out thank-you page
        return [url for url in urls if 'thank-you' not in url['location']]

class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return BlogPost.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.published_at

class ServiceSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Service.objects.all()

    def location(self, obj):
        return f"/services/{obj.slug}/"

sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogPostSitemap,
    'services': ServiceSitemap,
} 