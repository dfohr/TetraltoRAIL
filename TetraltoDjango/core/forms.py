from django import forms
from .models import Lead
import requests
from django.conf import settings

class LeadForm(forms.ModelForm):
    g_recaptcha_response = forms.CharField(widget=forms.HiddenInput(), required=not settings.DEBUG)
    
    def clean_g_recaptcha_response(self):
        token = self.cleaned_data.get('g_recaptcha_response')
        
        # Skip validation in development
        if settings.DEBUG:
            return token
            
        if not token:
            raise forms.ValidationError("reCAPTCHA validation failed")
            
        # Verify the token with Google
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': token
        })
        
        result = response.json()
        if not result.get('success'):
            raise forms.ValidationError("reCAPTCHA validation failed")
            
        # Check the score
        if result.get('score', 0) < settings.RECAPTCHA_SCORE_THRESHOLD:
            raise forms.ValidationError("reCAPTCHA score too low")
            
        return token
    
    class Meta:
        model = Lead
        fields = ['name', 'phone', 'email', 'address', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Please describe your roofing needs...'}),
            'address': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Your address...'}),
            'name': forms.TextInput(attrs={'placeholder': 'Your name...'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Your phone number...'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your email address...'}),
        } 