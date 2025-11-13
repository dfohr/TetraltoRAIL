import random
from django.core.cache import cache
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def generate_access_code():
    """Generate a random 6-digit access code."""
    return str(random.randint(100000, 999999))

def send_access_code_email(email, code):
    """
    Send access code to user via SendGrid.
    
    Args:
        email: Recipient email address
        code: 6-digit access code
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        message = Mail(
            from_email=settings.SENDGRID_FORM_FROM_EMAIL,
            to_emails=email,
            subject='Your Tetralto Customer Portal Access Code',
            html_content=f"""
            <div style="font-family: 'Comfortaa', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #E75A35;">Your Portal Access Code</h2>
                <p>Someone requested access to view your roofing project details at Tetralto Roofing.</p>
                <div style="background: #F5F5F5; border-left: 4px solid #E75A35; padding: 20px; margin: 20px 0;">
                    <p style="margin: 0; font-size: 14px; color: #666;">Your access code:</p>
                    <p style="margin: 10px 0 0 0; font-size: 32px; font-weight: bold; color: #E75A35; letter-spacing: 4px;">{code}</p>
                </div>
                <p><strong>This code expires in 15 minutes.</strong></p>
                <p>If you didn't request this code, you can safely ignore this email.</p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="font-size: 12px; color: #999;">
                    Tetralto Roofing<br>
                    Quality Roofing Solutions
                </p>
            </div>
            """
        )
        
        sg = SendGridAPIClient(api_key=settings.SENDGRID_FORM_API_KEY)
        response = sg.send(message)
        
        return response.status_code in [200, 201, 202]
        
    except Exception as e:
        print(f"Failed to send access code email: {e}")
        return False

def cache_access_code(email, code, portal_ids):
    """
    Cache access code with email and associated portal IDs.
    
    Args:
        email: User's email address
        code: 6-digit access code
        portal_ids: List of Portal IDs accessible to this email
        
    Returns:
        str: Cache key used
    """
    cache_key = f"portal_code_{email.lower()}"
    cache_data = {
        'code': code,
        'portal_ids': portal_ids
    }
    cache.set(cache_key, cache_data, timeout=900)  # 15 minutes
    return cache_key

def verify_access_code(email, submitted_code):
    """
    Verify submitted code matches cached code for email.
    
    Args:
        email: User's email address
        submitted_code: Code submitted by user
        
    Returns:
        tuple: (success: bool, portal_ids: list or None)
    """
    cache_key = f"portal_code_{email.lower()}"
    cached_data = cache.get(cache_key)
    
    if not cached_data:
        return False, None
        
    if cached_data['code'] == submitted_code:
        cache.delete(cache_key)  # Delete after successful verification
        return True, cached_data['portal_ids']
    
    return False, None

def set_portal_session(request, email, portal_ids):
    """
    Set session data for authenticated portal user.
    
    Args:
        request: Django request object
        email: Authenticated email address
        portal_ids: List of accessible Portal IDs
    """
    request.session['portal_auth'] = {
        'email': email.lower(),
        'portal_ids': portal_ids
    }
    request.session.set_expiry(432000)  # 5 days

def get_portal_session(request):
    """
    Get portal session data.
    
    Returns:
        dict or None: Session data if authenticated, None otherwise
    """
    return request.session.get('portal_auth')

def clear_portal_session(request):
    """Clear portal session data (logout)."""
    if 'portal_auth' in request.session:
        del request.session['portal_auth']
