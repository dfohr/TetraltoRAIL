from django.urls import path
from django.contrib.sitemaps.views import sitemap
from core import views
from .sitemaps import sitemaps

urlpatterns = [
    path('contact/', views.contact, name='contact'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
] 