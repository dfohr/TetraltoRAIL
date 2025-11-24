from django.db import models
from django.utils.text import slugify
from django.contrib.postgres.fields import ArrayField
import markdown
import re

class Service(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    subtitle = models.CharField(max_length=200)
    description = models.TextField(help_text="""
        Markdown formatted text. Use:
        * For bullet points, start lines with '* '
        * For paragraphs, leave a blank line between them
        * For emphasis, use *italics* or **bold**
        * For line breaks, use a blank line between paragraphs
    """)
    image_filename = models.CharField(max_length=100, help_text="Filename of the image in static/images/")
    icon_filename = models.CharField(max_length=100, help_text="Filename of the icon in static/images/")
    order = models.IntegerField(default=0, help_text="Order in which this service appears (lower numbers first)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

class Feature(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon_filename = models.CharField(max_length=100, help_text="Filename of the icon in static/images/ (format: feat_*_icon.avif)")
    order = models.IntegerField(default=0, help_text="Order in which this feature appears (lower numbers first)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    service = models.CharField(max_length=200)
    text = models.TextField()
    url = models.URLField()
    is_featured = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.name} - {self.city}"

class SocialLink(models.Model):
    name = models.CharField(max_length=100)
    popupText = models.CharField(max_length=200)
    icon_filename = models.CharField(max_length=100)
    url = models.URLField()
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

class Lead(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    description = models.TextField(help_text="Customer's description of their roofing needs")
    internal_notes = models.TextField(blank=True, help_text="Internal notes about this lead (only visible in admin)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d')}"

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, null=True, blank=True)
    meta_description = models.CharField(
        max_length=160,
        help_text="SEO meta description, recommended length 150-160 characters"
    )
    content = models.TextField(
        help_text="""
        Markdown formatted text. Supports:
        * Headers (# ## ###)
        * Lists (* or -)
        * Links [text](url)
        * Static images: ![alt](/static/images/filename)
        * Drive images: ![alt](drive:tag-name)
          - ONLY for images (not links or other files)
          - Tag images in Google Drive with custom property 'BlogTag'
          - Example: BlogTag='sienna-legacy-1' → ![alt](drive:sienna-legacy-1)
          - Tags: alphanumeric, hyphens, underscores only
          - Tags can be reused across multiple blog posts
        * Code blocks (```)
        * Emphasis (*italic* or **bold**)
        """
    )
    content_html = models.TextField(editable=False)
    author = models.CharField(max_length=100)
    hero_image_filename = models.CharField(
        max_length=100,
        help_text="Static filename (e.g., 'blog-hero.avif') or Drive reference (e.g., 'drive:hero-tag'). For Drive images, tag the file in Google Drive with custom property 'BlogTag'.",
        blank=True
    )
    hero_image_alt = models.CharField(max_length=200, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(
        default=False,
        help_text="Only active posts will be shown on the site"
    )

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Preprocess markdown to transform drive: references
        processed_content = self._preprocess_drive_images(self.content)
        
        # Convert markdown to HTML
        self.content_html = markdown.markdown(processed_content)
        super().save(*args, **kwargs)
    
    def _preprocess_drive_images(self, content):
        """
        Transform drive:<tag> image references to blog proxy URLs.
        
        Converts:
            ![alt text](drive:sienna-legacy-1)
        To:
            ![alt text](/blog/images/sienna-legacy-1/)
        
        This allows backward compatibility with static images while
        enabling Drive-backed images using the drive: prefix.
        """
        # Pattern to match markdown image syntax with drive: prefix
        # Matches: ![anything](drive:tag-name)
        pattern = r'!\[([^\]]*)\]\(drive:([^)]+)\)'
        replacement = r'![\1](/blog/images/\2/)'
        
        return re.sub(pattern, replacement, content)

class Portal(models.Model):
    customer_name = models.CharField(max_length=200, help_text="Customer's full name")
    project_tag = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Unique project identifier for Drive filtering (e.g., '2025-10 Sherrene Kibbe')"
    )
    emails = ArrayField(
        models.EmailField(max_length=254),
        default=list,
        help_text="List of email addresses with access to this portal"
    )
    project_date = models.DateField(help_text="Date of the roofing project")
    shingle_brand = models.CharField(max_length=100, help_text="Brand of shingles used")
    shingle_color = models.CharField(max_length=100, help_text="Color of shingles")
    has_left_review = models.BooleanField(
        default=False,
        help_text="Has customer left a Google review? (manually update in admin)"
    )
    drive_folder_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional: Google Drive folder ID to scope queries (leave blank to search all accessible files)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-project_date', '-created_at']
        verbose_name = "Customer Portal"
        verbose_name_plural = "Customer Portals"

    def __str__(self):
        return f"{self.customer_name} - {self.project_tag}"

# class ProjectImage(models.Model):
#     STATUS_CHOICES = [
#         ('raw', 'Raw'),
#         ('selected', 'Selected for Marketing'),
#         ('edited', 'Edited'),
#         ('used', 'Used in Marketing'),
#     ]
    
#     MARKETING_USE_CHOICES = [
#         ('blog', 'Blog Post'),
#         ('web', 'Website Content'),
#         ('ads', 'Google Ads'),
#         ('gmb', 'Google Business Profile'),
#         ('social', 'Social Media'),
#     ]

#     title = models.CharField(max_length=200)
#     description = models.TextField(blank=True)
#     image = models.ImageField(upload_to='project_images/%Y/%m/')
#     customer_name = models.CharField(max_length=100)
#     project_date = models.DateField()
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='raw')
#     marketing_use = models.CharField(max_length=20, choices=MARKETING_USE_CHOICES, blank=True)
#     is_featured = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ['-project_date', '-created_at']
#         verbose_name = "Project Image"
#         verbose_name_plural = "Project Images"

#     def __str__(self):
#         return f"{self.customer_name} - {self.project_date} - {self.title}"

#     def get_image_url(self):
#         return self.image.url if self.image else None 