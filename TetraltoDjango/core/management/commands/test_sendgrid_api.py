from django.core.management.base import BaseCommand
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class Command(BaseCommand):
    help = 'Test SendGrid API key directly'

    def handle(self, *args, **options):
        self.stdout.write("Testing SendGrid API key...")
        
        # Check environment variables
        self.stdout.write(f"API Key: {'*' * 10 + settings.SENDGRID_FORM_API_KEY[-4:] if settings.SENDGRID_FORM_API_KEY else 'Not set'}")
        self.stdout.write(f"From Email: {settings.SENDGRID_FORM_FROM_EMAIL}")
        self.stdout.write(f"To Email: {settings.SENDGRID_FORM_TO_EMAIL}")
        
        if not settings.SENDGRID_FORM_API_KEY:
            self.stdout.write(self.style.ERROR("SENDGRID_FORM_API_KEY not set"))
            return
        
        # Test API call
        try:
            message = Mail(
                from_email=settings.SENDGRID_FORM_FROM_EMAIL,
                to_emails=settings.SENDGRID_FORM_TO_EMAIL,
                subject='Test Email from Django',
                plain_text_content='This is a test email from your Django application.'
            )
            
            sg = SendGridAPIClient(api_key=settings.SENDGRID_FORM_API_KEY)
            response = sg.send(message)
            
            self.stdout.write(f"Status Code: {response.status_code}")
            self.stdout.write(f"Response Body: {response.body}")
            self.stdout.write(f"Response Headers: {response.headers}")
            
            if response.status_code in [200, 201, 202]:
                self.stdout.write(self.style.SUCCESS("API test successful!"))
            else:
                self.stdout.write(self.style.ERROR(f"API test failed with status {response.status_code}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"API test failed: {str(e)}"))
            self.stdout.write(f"Exception type: {type(e).__name__}")
