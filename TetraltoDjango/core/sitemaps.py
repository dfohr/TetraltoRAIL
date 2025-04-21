from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogPost, Service
from django.utils import timezone
from datetime import timedelta

class StaticViewSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return ['home', 'services', 'contact', 'blog']

    def location(self, item):
        return reverse(item)

    def lastmod(self, obj):
        # Return specific last modified dates for each page
        # These dates help search engines determine when to recrawl
        if obj == 'blog':
            try:
                latest_post = BlogPost.objects.filter(is_active=True).latest('updated_at')
                return latest_post.updated_at
            except BlogPost.DoesNotExist:
                return None
        
        # Return datetime instead of date for consistency
        return timezone.now()

    def changefreq(self, item):
        # Customize change frequency for different pages
        frequencies = {
            'home': 'daily',      # Homepage changes frequently
            'services': 'weekly',  # Service pages change occasionally
            'contact': 'monthly',  # Contact info rarely changes
            'blog': 'daily'       # Blog list changes with new posts
        }
        return frequencies.get(item, 'weekly')

    def priority(self, item):
        # Customize priority for different pages
        priorities = {
            'home': 1.0,      # Homepage is most important
            'services': 0.8,   # Services are key content
            'contact': 0.6,    # Contact is important but not primary
            'blog': 0.7        # Blog list is fairly important
        }
        return priorities.get(item, 0.5)

class BlogPostSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        # Only include active blog posts
        return BlogPost.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at or obj.created_at

    def location(self, obj):
        return reverse('blog_post', args=[obj.slug])
    
    def priority(self, obj):
        # Convert datetime to date before comparison
        update_date = (obj.updated_at or obj.created_at).date()
        age = timezone.now().date() - update_date
        if age <= timedelta(days=7):
            return 0.8  # New posts (1 week old or less)
        elif age <= timedelta(days=30):
            return 0.6  # Recent posts (1 month old or less)
        else:
            return 0.4  # Older posts

    def changefreq(self, obj):
        # Convert datetime to date before comparison
        update_date = (obj.updated_at or obj.created_at).date()
        age = timezone.now().date() - update_date
        if age <= timedelta(days=7):
            return 'daily'     # New posts might be edited frequently
        elif age <= timedelta(days=30):
            return 'weekly'    # Recent posts might get updates
        elif age <= timedelta(days=90):
            return 'monthly'   # Older posts get occasional updates
        else:
            return 'yearly'    # Very old posts rarely change

class ServiceSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        # Only include services with slugs
        return Service.objects.filter(slug__isnull=False)

    def lastmod(self, obj):
        return obj.updated_at or obj.created_at

    def location(self, obj):
        return reverse('service_detail', args=[obj.slug])
    
    def priority(self, obj):
        # Services are important content, give them high priority
        return 0.9

    def changefreq(self, obj):
        # Services don't change very often
        return 'monthly' 