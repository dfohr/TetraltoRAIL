from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def send_lead_notification(lead):
    """
    Send email notification when a new lead is submitted.
    
    Args:
        lead: Lead model instance
    """
    if not settings.SENDGRID_FORM_TO_EMAIL:
        logger.warning("SENDGRID_FORM_TO_EMAIL not configured, skipping email notification")
        return False
    
    try:
        # Create email content
        subject = f"New Lead: {lead.name} - {lead.created_at.strftime('%Y-%m-%d %H:%M')}"
        
        # Build the email body
        email_body = f"""
New lead submitted on Tetralto Roofing website:

Name: {lead.name}
Phone: {lead.phone}
Email: {lead.email}
Address: {lead.address}

Description: {lead.description}

Submitted: {lead.created_at.strftime('%Y-%m-%d %H:%M:%S')}

Internal Notes: {lead.internal_notes if lead.internal_notes else 'None'}

---
This is an automated notification from your website contact form.
        """.strip()
        
        # Send the email
        success = send_mail(
            subject=subject,
            message=email_body,
            from_email=settings.SENDGRID_FORM_FROM_EMAIL,
            recipient_list=[settings.SENDGRID_FORM_TO_EMAIL],
            fail_silently=False,
        )
        
        if success:
            logger.info(f"Lead notification email sent successfully for lead ID {lead.id}")
            return True
        else:
            logger.error(f"Failed to send lead notification email for lead ID {lead.id}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending lead notification email: {str(e)}")
        return False

def send_test_email():
    """
    Send a test email to verify SendGrid configuration.
    """
    if not settings.SENDGRID_FORM_TO_EMAIL:
        logger.warning("SENDGRID_FORM_TO_EMAIL not configured, cannot send test email")
        return False
    
    try:
        subject = "Test Email - Tetralto Roofing Website"
        message = f"""
This is a test email from your Tetralto Roofing website.

Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
Environment: {'Production' if not settings.DEBUG else 'Development'}

If you received this email, your SendGrid configuration is working correctly!
        """.strip()
        
        success = send_mail(
            subject=subject,
            message=message,
            from_email=settings.SENDGRID_FORM_FROM_EMAIL,
            recipient_list=[settings.SENDGRID_FORM_TO_EMAIL],
            fail_silently=False,
        )
        
        if success:
            logger.info("Test email sent successfully")
            return True
        else:
            logger.error("Failed to send test email")
            return False
            
    except Exception as e:
        logger.error(f"Error sending test email: {str(e)}")
        return False
