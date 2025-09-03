from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import asyncio
import threading
from .models import Lead
from .email_utils import send_lead_notification
import logging

logger = logging.getLogger(__name__)

def send_email_async(lead):
    """
    Send email notification asynchronously to avoid blocking the request.
    """
    try:
        send_lead_notification(lead)
        logger.info(f"Async email notification sent successfully for lead ID {lead.id}")
    except Exception as e:
        logger.error(f"Error sending async email notification for lead ID {lead.id}: {str(e)}")

@receiver(post_save, sender=Lead)
def handle_new_lead_notification(sender, instance, created, **kwargs):
    """
    Signal handler that triggers email notification only when a new lead is created.
    This prevents admin edits from triggering emails.
    """
    # Debug logging to see if signal is being called at all
    logger.info(f"Signal triggered: Lead ID {instance.id}, created={created}")
    
    if created:  # Only for new records, not updates
        logger.info(f"New lead created (ID: {instance.id}), triggering async email notification")
        
        # Send email notification asynchronously
        # Use threading to avoid blocking the request
        thread = threading.Thread(target=send_email_async, args=(instance,))
        thread.daemon = True  # Don't prevent app shutdown
        thread.start()
        
        logger.info(f"Async email notification thread started for lead ID {instance.id}")
    else:
        # This is an update, not a new creation
        logger.debug(f"Lead updated (ID: {instance.id}), no email notification sent")
