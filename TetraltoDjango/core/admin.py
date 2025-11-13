from django.contrib import admin
from .models import Service, Feature, Testimonial, SocialLink, Lead, BlogPost, Portal

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

@admin.register(Portal)
class PortalAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'project_tag', 'project_date', 'has_left_review', 'created_at']
    list_filter = ['has_left_review', 'project_date', 'created_at']
    search_fields = ['customer_name', 'project_tag', 'shingle_brand', 'shingle_color']
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'project_tag', 'emails')
        }),
        ('Project Details', {
            'fields': ('project_date', 'shingle_brand', 'shingle_color')
        }),
        ('Google Drive', {
            'fields': ('drive_folder_id',),
            'description': 'Optional: Specify a folder ID to scope Drive queries'
        }),
        ('Review Status', {
            'fields': ('has_left_review',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    ) 