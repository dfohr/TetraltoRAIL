from django.core.management.base import BaseCommand
from core.email_utils import send_test_email
from django.conf import settings

class Command(BaseCommand):
    help = 'Test SendGrid email configuration'

    def handle(self, *args, **options):
        self.stdout.write("Testing SendGrid email configuration...")
        
        # Check if SendGrid is configured
        if not settings.SENDGRID_FORM_API_KEY:
            self.stdout.write(
                self.style.ERROR(
                    "SENDGRID_FORM_API_KEY not configured. Please set this environment variable."
                )
            )
            return
        
        if not settings.SENDGRID_FORM_TO_EMAIL:
            self.stdout.write(
                self.style.ERROR(
                    "SENDGRID_FORM_TO_EMAIL not configured. Please set this environment variable."
                )
            )
            return
        
        self.stdout.write(f"SendGrid API Key: {'*' * 10 + settings.SENDGRID_FORM_API_KEY[-4:] if settings.SENDGRID_FORM_API_KEY else 'Not set'}")
        self.stdout.write(f"From Email: {settings.SENDGRID_FORM_FROM_EMAIL}")
        self.stdout.write(f"To Email: {settings.SENDGRID_FORM_TO_EMAIL}")
        self.stdout.write("")
        
        # Send test email
        success = send_test_email()
        
        if success:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Test email sent successfully to {settings.SENDGRID_FORM_TO_EMAIL}"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    "Failed to send test email. Check your SendGrid configuration."
                )
            )
