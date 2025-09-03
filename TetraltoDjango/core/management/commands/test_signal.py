from django.core.management.base import BaseCommand
from core.models import Lead
from django.conf import settings

class Command(BaseCommand):
    help = 'Test if the Lead post_save signal is working'

    def handle(self, *args, **options):
        self.stdout.write("Testing Lead post_save signal...")
        
        # Create a test lead to trigger the signal
        test_lead = Lead.objects.create(
            name="Test Signal",
            phone="555-123-4567",
            email="test@example.com",
            address="123 Test St",
            description="Testing signal functionality"
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Test lead created with ID: {test_lead.id}"
            )
        )
        
        # Clean up the test lead
        test_lead.delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                "Test lead deleted. Check logs for signal messages."
            )
        )
