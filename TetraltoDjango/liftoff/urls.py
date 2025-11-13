"""
URL configuration for liftoff project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from core.views import (
    home, health, api_health, services_view, contact, 
    blog_list, blog_post, robots_txt, terms_and_conditions,
    service_detail, thank_you, google_landing, google_thank_you, test_page,
    portal_login, portal_select, portal_detail, portal_gallery, portal_proxy_image, portal_logout
)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import StaticViewSitemap, BlogPostSitemap, ServiceSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogPostSitemap,
    'services': ServiceSitemap,
}

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('health/', health, name='health'),
    re_path(r'^api/?$', api_health, name='api_health'),
    path('services/', services_view, name='services'),
    path('services/<slug:slug>/', service_detail, name='service_detail'),
    path('contact/', contact, name='contact'),
    path('thank-you/', thank_you, name='thank_you'),
    path('google-landing/', google_landing, name='google_landing'),
    path('google-thank-you/', google_thank_you, name='google_thank_you'),
    path('blog/', blog_list, name='blog'),
    path('blog/<slug:slug>/', blog_post, name='blog_post'),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('terms-and-conditions/', terms_and_conditions, name='terms_and_conditions'),
    path('test/', test_page, name='test_page'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    
    # Customer Portal URLs
    path('portal/login/', portal_login, name='portal_login'),
    path('portal/select/', portal_select, name='portal_select'),
    path('portal/image/<str:file_id>/', portal_proxy_image, name='portal_proxy_image'),
    path('portal/<str:project_tag>/', portal_detail, name='portal_detail'),
    path('portal/<str:project_tag>/<str:page_name>/', portal_gallery, name='portal_gallery'),
    path('portal/logout/', portal_logout, name='portal_logout'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
