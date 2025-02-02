from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Service, Feature, Testimonial, SocialLink, BlogPost
from .forms import LeadForm
import django
import sys
import os
import markdown
from django.http import HttpResponse
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

def home(request):
    services = Service.objects.order_by('order')
    features = Feature.objects.order_by('order')
    testimonials = Testimonial.objects.filter(is_active=True, is_featured=True).order_by('?')
    social_links = SocialLink.objects.filter(is_active=True).order_by('order')
    
    return render(request, 'home.html', {
        'services': services,
        'features': features,
        'testimonials': testimonials,
        'social_links': social_links,
    })

def health(request):
    # Database info
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]

    # Get user info
    User = get_user_model()
    users = User.objects.all()
    user_list = [f"{user.username} (Staff: {user.is_staff}, Superuser: {user.is_superuser})" for user in users]

    # System info
    system_info = {
        'Django Version': django.get_version(),
        'Python Version': sys.version,
        'Database Version': db_version,
        'Database Name': db_name,
        'Environment': os.environ.get('RAILWAY_ENVIRONMENT', 'development'),
        'Debug Mode': os.environ.get('DJANGO_DEBUG', 'True'),
        'Allowed Hosts': os.environ.get('DJANGO_ALLOWED_HOSTS', '*'),
        'User Count': users.count(),
        'Users': user_list,
    }
    
    return render(request, 'health.html', {'system_info': system_info})

def services_view(request):
    services = Service.objects.all().order_by('order')
    # Convert markdown to HTML for each service
    for service in services:
        service.description_html = markdown.markdown(
            service.description,
            extensions=['nl2br', 'tables', 'fenced_code']
        )
    
    return render(request, 'services.html', {
        'services': services,
        'social_links': SocialLink.objects.filter(is_active=True).order_by('order'),
    })

def contact(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'contact.html', {
                'submission_successful': True,
                'email': 'sales@tetralto.com'
            })
    else:
        form = LeadForm()
    
    return render(request, 'contact.html', {
        'form': form,
        'email': 'sales@tetralto.com',
        'submission_successful': False
    })

def blog(request):
    return render(request, 'blog.html', {
        'social_links': SocialLink.objects.filter(is_active=True).order_by('order'),
    })

def blog_list(request):
    posts = BlogPost.objects.filter(
        is_active=True,
        published_at__lte=timezone.now()
    ).order_by('-published_at')
    
    context = {
        'posts': posts,
        'social_links': SocialLink.objects.filter(is_active=True).order_by('order'),
    }
    return render(request, 'blog.html', context)

def blog_post(request, slug):
    post = get_object_or_404(
        BlogPost,
        slug=slug,
        is_active=True,
        published_at__lte=timezone.now()
    )
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=[
        'markdown.extensions.fenced_code',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
    ])
    post.content_html = md.convert(post.content)
    
    context = {
        'post': post,
        'social_links': SocialLink.objects.filter(is_active=True).order_by('order'),
    }
    return render(request, 'blog_post.html', context)

def robots_txt(request):
    protocol = 'https' if not settings.DEBUG else 'http'
    domain = settings.SITE_DOMAIN
    sitemap_url = f"{protocol}://{domain}/sitemap.xml"
    content = f"""User-agent: *
Allow: /
Sitemap: {sitemap_url}"""
    return HttpResponse(content, content_type="text/plain") 