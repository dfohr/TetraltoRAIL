from django.contrib import admin
from .models import Service, Feature, Testimonial, SocialLink, Lead, BlogPost

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'subtitle', 'order', 'created_at', 'updated_at']
    list_editable = ['order']
    search_fields = ['title', 'subtitle', 'description']
    readonly_fields = ('created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'created_at', 'updated_at']
    list_editable = ['order']
    search_fields = ['title', 'description']
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'service', 'rating', 'is_featured', 'is_active', 'created_at')
    list_filter = ('is_featured', 'is_active', 'rating', 'service')
    search_fields = ('name', 'city', 'service', 'text')
    ordering = ('-created_at',)

@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'is_active', 'order', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['name', 'popupText', 'url']
    ordering = ['order']

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'phone', 'description', 'internal_notes']
    readonly_fields = ('created_at', 'updated_at')

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_active', 'published_at', 'created_at']
    list_filter = ['is_active', 'published_at', 'created_at']
    search_fields = ['title', 'content', 'meta_description']
    readonly_fields = ('created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'hero_image_filename')
        }),
        ('Content', {
            'fields': ('content', 'meta_description')
        }),
        ('Publication', {
            'fields': ('is_active', 'published_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    ) 