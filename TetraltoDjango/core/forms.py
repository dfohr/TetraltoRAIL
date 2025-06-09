from django import forms
from .models import Lead
import requests
from django.conf import settings
import json

class LeadForm(forms.ModelForm):
    g_recaptcha_response = forms.CharField(widget=forms.HiddenInput(), required=not settings.DEBUG)
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
    
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
            # Log more details about the failure
            print(f"reCAPTCHA validation failed: {result}")
            raise forms.ValidationError("reCAPTCHA validation failed")
            
        # Store the score for later use
        self.recaptcha_score = result.get('score', 0)
        
        # Check the score
        if self.recaptcha_score < settings.RECAPTCHA_SCORE_THRESHOLD:
            # Log the score that failed
            print(f"reCAPTCHA score too low: {self.recaptcha_score} < {settings.RECAPTCHA_SCORE_THRESHOLD}")
            raise forms.ValidationError("reCAPTCHA score too low")
            
        return token
    
    def save(self, commit=True):
        lead = super().save(commit=False)
        
        # Build internal notes with reCAPTCHA score and campaign data
        notes_parts = []
        
        # Add reCAPTCHA score
        if hasattr(self, 'recaptcha_score'):
            notes_parts.append(f"reCAPTCHA: {self.recaptcha_score}")
        
        # Add campaign data if available
        if self.request:
            campaign_data = []
            
            # Get GCLID
            gclid = self.request.GET.get('gclid')
            if gclid:
                campaign_data.append(f"GCLID: {gclid}")
            
            # Get Campaign ID
            campaign_id = self.request.GET.get('gad_campaignid')
            if campaign_id:
                campaign_data.append(f"Campaign ID: {campaign_id}")
            
            # Get UTM parameters
            utm_source = self.request.GET.get('utm_source')
            if utm_source:
                campaign_data.append(f"Source: {utm_source}")
                
            utm_campaign = self.request.GET.get('utm_campaign')
            if utm_campaign:
                campaign_data.append(f"Campaign: {utm_campaign}")
            
            if campaign_data:
                notes_parts.append("Campaign: " + ", ".join(campaign_data))
        
        # Set internal notes
        if notes_parts:
            lead.internal_notes = " | ".join(notes_parts)
        
        if commit:
            lead.save()
        return lead
    
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
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # Make name and email optional
        self.fields['name'].required = False
        self.fields['email'].required = False
        # Set address to empty string since it's not used in this form
        self.fields['address'] = forms.CharField(widget=forms.HiddenInput(), required=False, initial='')
    
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
            # Log more details about the failure
            print(f"reCAPTCHA validation failed: {result}")
            raise forms.ValidationError("reCAPTCHA validation failed")
            
        # Store the score for later use
        self.recaptcha_score = result.get('score', 0)
        
        # Check the score
        if self.recaptcha_score < settings.RECAPTCHA_SCORE_THRESHOLD:
            # Log the score that failed
            print(f"reCAPTCHA score too low: {self.recaptcha_score} < {settings.RECAPTCHA_SCORE_THRESHOLD}")
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
    
    def save(self, commit=True):
        lead = super().save(commit=False)
        
        # Build internal notes with reCAPTCHA score and campaign data
        notes_parts = []
        
        # Add reCAPTCHA score
        if hasattr(self, 'recaptcha_score'):
            notes_parts.append(f"reCAPTCHA: {self.recaptcha_score}")
        
        # Add campaign data if available
        if self.request:
            campaign_data = []
            
            # Get GCLID
            gclid = self.request.GET.get('gclid')
            if gclid:
                campaign_data.append(f"GCLID: {gclid}")
            
            # Get Campaign ID
            campaign_id = self.request.GET.get('gad_campaignid')
            if campaign_id:
                campaign_data.append(f"Campaign ID: {campaign_id}")
            
            # Get UTM parameters
            utm_source = self.request.GET.get('utm_source')
            if utm_source:
                campaign_data.append(f"Source: {utm_source}")
                
            utm_campaign = self.request.GET.get('utm_campaign')
            if utm_campaign:
                campaign_data.append(f"Campaign: {utm_campaign}")
            
            if campaign_data:
                notes_parts.append("Campaign: " + ", ".join(campaign_data))
        
        # Set internal notes
        if notes_parts:
            lead.internal_notes = " | ".join(notes_parts)
        
        if commit:
            lead.save()
        return lead
    
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