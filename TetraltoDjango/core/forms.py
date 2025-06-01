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

class GoogleLandingForm(forms.ModelForm):
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
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError("Phone number is required.")
        
        # Remove all non-digit characters
        digits_only = ''.join(filter(str.isdigit, phone))
        
        # Check if it's a valid 10-digit US phone number
        if len(digits_only) != 10:
            raise forms.ValidationError("Please enter a valid 10-digit phone number.")
        
        return phone
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description:
            raise forms.ValidationError("Please describe your roofing needs.")
        
        if len(description.strip()) < 10:
            raise forms.ValidationError("Please provide at least 10 characters describing your roofing needs.")
        
        return description
    
    class Meta:
        model = Lead
        fields = ['name', 'phone', 'email', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Your Name',
                'class': 'form-input'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Your Phone',
                'class': 'form-input',
                'type': 'tel'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Your Email',
                'class': 'form-input'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Describe your roofing needs',
                'class': 'form-input',
                'rows': 4
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make name and email optional
        self.fields['name'].required = False
        self.fields['email'].required = False
        # Set address to empty string since it's not used in this form
        self.fields['address'] = forms.CharField(widget=forms.HiddenInput(), required=False, initial='') 