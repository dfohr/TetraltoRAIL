from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Service, Feature, Testimonial, SocialLink, BlogPost, Portal
from .forms import LeadForm
from .blog_ref_service import BlogRefService
from .portal_utils import (
    generate_access_code, send_access_code_email, cache_access_code,
    verify_access_code, set_portal_session, get_portal_session, clear_portal_session
)
from .drive_utils import query_files_by_project
import django
import sys
import os
import markdown
from django.http import HttpResponse
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
from django.http import JsonResponse, HttpResponse

def home(request):
    services = Service.objects.order_by('order')
    testimonials = Testimonial.objects.filter(is_active=True, is_featured=True).order_by('?')
    social_links = SocialLink.objects.filter(is_active=True).order_by('order')
    
    # Handle form submission
    if request.method == 'POST':
        form = LeadForm(request.POST, request=request, variant='contact')
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you! We've received your request and will contact you soon.")
            return redirect('home')  # Redirect to prevent resubmission
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LeadForm(request=request, variant='contact')
    
    return render(request, 'home.html', {
        'services': services,
        'testimonials': testimonials,
        'social_links': social_links,
        'form': form,
    })

def api_health(request):
    """
    Simple API health check endpoint for infrastructure monitoring.
    Returns 200 OK for HEAD/GET requests without database calls.
    """
    if request.method == 'HEAD':
        return HttpResponse(status=200)
    return JsonResponse({"status": "ok"})

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

    # Check PostHog status
    posthog_status = {
        "initialized": False,
        "error": None,
        "timestamp": None
    }
    
    try:
        import requests
        response = requests.get('https://e.tetralto.com/decide/', timeout=5)
        posthog_status["initialized"] = response.status_code == 200
        posthog_status["timestamp"] = datetime.now().isoformat()
    except Exception as e:
        posthog_status["error"] = str(e)
        posthog_status["timestamp"] = datetime.now().isoformat()

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
        'PostHog Status': posthog_status
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
    })

def contact(request):
    if request.method == 'POST':
        form = LeadForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            return redirect('thank_you')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LeadForm(request=request)
    
    return render(request, 'contact.html', {
        'form': form,
        'email': 'sales@tetralto.com'
    })

def blog(request):
    return render(request, 'blog.html', {})

def blog_list(request):
    posts = BlogPost.objects.filter(
        is_active=True,
        published_at__lte=timezone.now()
    ).order_by('-published_at')
    
    context = {
        'posts': posts,
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
        'debug': settings.DEBUG,
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

def terms_and_conditions(request):
    """View for the Terms and Conditions page."""
    return render(request, 'terms.html', {})

def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    
    # Get blog content using service layer
    featured_blog = BlogRefService.get_featured_post('services')
    related_posts = BlogRefService.get_related_posts('services')
    
    # Convert markdown to HTML
    service.description_html = markdown.markdown(
        service.description,
        extensions=['nl2br', 'tables', 'fenced_code']
    )
    
    return render(request, f'{slug}.html', {
        'service': service,
        'featured_blog': featured_blog,
        'related_posts': related_posts,
    })

def thank_you(request):
    return render(request, 'thank-you.html', {})

def google_landing(request):
    if request.method == 'POST':
        form = LeadForm(request.POST, request=request, minimal_required=True)
        if form.is_valid():
            form.save()
            return redirect('google_thank_you')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LeadForm(request=request, minimal_required=True)
    
    return render(request, 'google-landing.html', {
        'form': form,
    })

def google_thank_you(request):
    return render(request, 'google-thank-you.html')

def test_page(request):
    """Component test page - not indexed."""
    from .drive_utils import query_files_by_project, get_images_from_files, get_non_image_files, list_all_accessible_files
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Debug mode: List all accessible files to check properties
    debug_mode = request.GET.get('debug', '') == 'true'
    debug_files = []
    
    if debug_mode:
        try:
            debug_files = list_all_accessible_files(max_results=20)
            print(f"[Drive DEBUG] Found {len(debug_files)} accessible files")
            for f in debug_files[:5]:  # Print first 5 files
                print(f"  - {f.get('name')}: properties = {f.get('properties')}")
        except Exception as e:
            print(f"[Drive DEBUG ERROR] {e}")
    
    # Google Drive POC - Query project files
    project_tag = request.GET.get('project', '2025-10 Sherrene Kibbe')  # Allow testing different projects
    no_filter = request.GET.get('nofilter', '') == 'true'  # Show ALL files without Project filter
    drive_images = []
    drive_files = []
    drive_error = None
    drive_success_msg = None
    
    try:
        if no_filter:
            # Query ALL accessible files without Project filter
            all_files = list_all_accessible_files(max_results=100)
            drive_success_msg = f"Successfully queried Drive API (NO FILTER). Found {len(all_files)} total accessible files"
        else:
            # Query with Project filter
            all_files = query_files_by_project(project_tag, max_results=50)
            drive_success_msg = f"Successfully queried Drive API. Found {len(all_files)} total files matching Project='{project_tag}'"
        
        drive_images = get_images_from_files(all_files, limit=3)
        drive_files = get_non_image_files(all_files, skip_count=len(drive_images))
        print(f"[Drive POC] {drive_success_msg}")
    except Exception as e:
        drive_error = str(e)
        print(f"[Drive POC ERROR] {e}")
        import traceback
        traceback.print_exc()
    
    return render(request, 'test.html', {
        'project_tag': project_tag,
        'drive_images': drive_images,
        'drive_files': drive_files,
        'drive_error': drive_error,
        'drive_success_msg': drive_success_msg,
        'debug_mode': debug_mode,
        'debug_files': debug_files,
        'no_filter': no_filter,
    })

# Portal Views

def portal_login(request):
    """Email-based login for customer portal access."""
    # If already authenticated, redirect to portal selection
    session_data = get_portal_session(request)
    if session_data:
        return redirect('portal_select')
    
    if request.method == 'POST':
        step = request.POST.get('step', 'email')
        
        if step == 'email':
            # Step 1: Email submission - generate and send code
            email = request.POST.get('email', '').strip().lower()
            
            if not email:
                messages.error(request, "Please enter your email address.")
                return render(request, 'portal/login.html', {})
            
            # Find portals accessible by this email
            portals = Portal.objects.filter(emails__contains=[email])
            
            if not portals.exists():
                messages.error(request, "No portal access found for this email address. Please contact Tetralto Roofing.")
                return render(request, 'portal/login.html', {})
            
            # Generate and cache access code
            code = generate_access_code()
            portal_ids = list(portals.values_list('id', flat=True))
            cache_access_code(email, code, portal_ids)
            
            # Send email
            if send_access_code_email(email, code):
                return render(request, 'portal/login.html', {
                    'step': 'code',
                    'email': email,
                    'portal_count': len(portal_ids)
                })
            else:
                messages.error(request, "Failed to send access code. Please try again or contact support.")
                return render(request, 'portal/login.html', {})
        
        elif step == 'code':
            # Step 2: Code verification
            email = request.POST.get('email', '').strip().lower()
            code = request.POST.get('code', '').strip()
            
            if not email or not code:
                messages.error(request, "Please enter your access code.")
                return render(request, 'portal/login.html', {
                    'step': 'code',
                    'email': email
                })
            
            # Verify code
            success, portal_ids = verify_access_code(email, code)
            
            if not success:
                messages.error(request, "Invalid or expired access code. Please request a new one.")
                return render(request, 'portal/login.html', {})
            
            # Set session
            set_portal_session(request, email, portal_ids)
            
            # Redirect to portal selection page
            return redirect('portal_select')
    
    return render(request, 'portal/login.html', {})

def portal_select(request):
    """Portal selection page for users with access to multiple portals."""
    session_data = get_portal_session(request)
    
    if not session_data:
        return redirect('portal_login')
    
    portal_ids = session_data.get('portal_ids', [])
    portals = Portal.objects.filter(id__in=portal_ids).order_by('-project_date')
    
    return render(request, 'portal/select.html', {
        'portals': portals,
        'email': session_data.get('email')
    })

def portal_detail(request, project_tag):
    """Portal detail page showing Drive media grouped by PortalPage."""
    session_data = get_portal_session(request)
    
    if not session_data:
        return redirect('portal_login')
    
    # Get the portal and verify access
    try:
        portal = Portal.objects.get(project_tag=project_tag)
    except Portal.DoesNotExist:
        messages.error(request, "Portal not found.")
        return redirect('portal_select')
    
    # Verify user has access to this portal
    portal_ids = session_data.get('portal_ids', [])
    if portal.id not in portal_ids:
        messages.error(request, "You do not have access to this portal.")
        return redirect('portal_select')
    
    # Query Google Drive for files
    portal_pages = {}
    files_section = []
    error_message = None
    
    try:
        all_files = query_files_by_project(project_tag, max_results=200)
        
        # Group files by PortalPage custom property
        for file_data in all_files:
            # Extract PortalPage from properties dict
            properties = file_data.get('properties', {})
            portal_page = properties.get('PortalPage')
            
            # Skip files without PortalPage property
            if not portal_page:
                continue
            
            # Add convenient keys to file_data for template use
            file_data['portal_page'] = portal_page
            file_data['thumbnail_link'] = file_data.get('thumbnailLink')
            file_data['web_view_link'] = file_data.get('webViewLink')
            file_data['mime_type'] = file_data.get('mimeType')
            
            # Separate "Files" section from PortalPage tiles
            if portal_page == 'Files':
                files_section.append(file_data)
            else:
                if portal_page not in portal_pages:
                    portal_pages[portal_page] = []
                portal_pages[portal_page].append(file_data)
        
    except Exception as e:
        error_message = f"Error loading media: {str(e)}"
        print(f"[Portal Detail Error] {e}")
        import traceback
        traceback.print_exc()
    
    return render(request, 'portal/detail.html', {
        'portal': portal,
        'portal_pages': portal_pages,
        'files_section': files_section,
        'error_message': error_message,
        'email': session_data.get('email')
    })

def portal_gallery(request, project_tag, page_name):
    """Gallery page showing all photos for a specific PortalPage category."""
    session_data = get_portal_session(request)
    
    if not session_data:
        return redirect('portal_login')
    
    # Get the portal and verify access
    try:
        portal = Portal.objects.get(project_tag=project_tag)
    except Portal.DoesNotExist:
        messages.error(request, "Portal not found.")
        return redirect('portal_select')
    
    # Verify user has access to this portal
    portal_ids = session_data.get('portal_ids', [])
    if portal.id not in portal_ids:
        messages.error(request, "You do not have access to this portal.")
        return redirect('portal_select')
    
    # Query Google Drive for files in this PortalPage category
    images = []
    error_message = None
    
    try:
        all_files = query_files_by_project(project_tag, max_results=200)
        
        # Filter files for this specific PortalPage
        for file_data in all_files:
            properties = file_data.get('properties', {})
            portal_page = properties.get('PortalPage')
            
            if portal_page == page_name:
                # Only include image files
                if file_data.get('mimeType', '').startswith('image/'):
                    # Normalize keys for template
                    file_data['thumbnail_link'] = file_data.get('thumbnailLink')
                    file_data['web_view_link'] = file_data.get('webViewLink')
                    file_data['web_content_link'] = file_data.get('webContentLink')
                    images.append(file_data)
        
    except Exception as e:
        error_message = f"Error loading images: {str(e)}"
        print(f"[Portal Gallery Error] {e}")
        import traceback
        traceback.print_exc()
    
    return render(request, 'portal/gallery.html', {
        'portal': portal,
        'page_name': page_name,
        'images': images,
        'error_message': error_message,
        'email': session_data.get('email')
    })

def portal_logout(request):
    """Logout from portal and redirect to home."""
    clear_portal_session(request)
    messages.success(request, "You have been logged out of the customer portal.")
    return redirect('home') 