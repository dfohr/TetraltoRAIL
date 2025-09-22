from django import forms
from .models import Lead
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class LeadForm(forms.ModelForm):
    """Unified form for both contact and landing page lead capture"""
    g_recaptcha_response = forms.CharField(widget=forms.HiddenInput(), required=not settings.DEBUG)
    
    # Hidden fields for campaign tracking and source data
    submission_source = forms.CharField(widget=forms.HiddenInput(), required=False)
    page_url = forms.CharField(widget=forms.HiddenInput(), required=False)
    referrer = forms.CharField(widget=forms.HiddenInput(), required=False)
    recaptcha_action = forms.CharField(widget=forms.HiddenInput(), required=False)
    gclid = forms.CharField(widget=forms.HiddenInput(), required=False)
    gad_campaignid = forms.CharField(widget=forms.HiddenInput(), required=False)
    utm_source = forms.CharField(widget=forms.HiddenInput(), required=False)
    utm_medium = forms.CharField(widget=forms.HiddenInput(), required=False)
    utm_campaign = forms.CharField(widget=forms.HiddenInput(), required=False)
    utm_term = forms.CharField(widget=forms.HiddenInput(), required=False)
    utm_content = forms.CharField(widget=forms.HiddenInput(), required=False)
    posthog_distinct_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    def __init__(self, *args, **kwargs):
        # Control which fields are required based on form type
        self.minimal_required = kwargs.pop('minimal_required', False)
        self.variant = kwargs.pop('variant', 'full')  # hero, contact, minimal, full
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Apply CSS classes based on variant
        form_input_class = self._get_input_class_for_variant()
        for field_name, field in self.fields.items():
            if field_name not in ['g_recaptcha_response', 'submission_source', 'page_url', 'referrer', 'recaptcha_action', 'gclid', 'gad_campaignid', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'posthog_distinct_id']:
                if hasattr(field.widget, 'attrs'):
                    field.widget.attrs.update({'class': form_input_class})
        
        # For Google landing (minimal_required=True): only phone + description required
        if self.minimal_required:
            self.fields['name'].required = False
            self.fields['email'].required = False
            self.fields['address'].required = False
    
    def _get_input_class_for_variant(self):
        """Return CSS class for form inputs based on variant"""
        variant_classes = {
            'hero': 'form-input',
            'contact': 'form-field',
            'minimal': 'form-input',
            'full': 'form-field'
        }
        return variant_classes.get(self.variant, 'form-field')
    
    def clean_phone(self):
        """Validate phone as 10-digit US number"""
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
        """Require meaningful descriptions"""
        description = self.cleaned_data.get('description')
        if not description:
            raise forms.ValidationError("Please describe your roofing needs.")
        
        if len(description.strip()) < 10:
            raise forms.ValidationError("Please provide at least 10 characters describing your roofing needs.")
        
        return description
    
    def clean_g_recaptcha_response(self):
        """Validate reCAPTCHA token"""
        token = self.cleaned_data.get('g_recaptcha_response')
        
        # Skip validation in development
        if settings.DEBUG:
            return token
            
        if not token:
            raise forms.ValidationError("reCAPTCHA validation failed")
            
        # Verify the token with Google
        try:
            response = requests.post('https://www.google.com/recaptcha/api/siteverify', {
                'secret': settings.RECAPTCHA_PRIVATE_KEY,
                'response': token
            })
            
            result = response.json()
            if not result.get('success'):
                logger.warning(f"reCAPTCHA validation failed: {result}")
                raise forms.ValidationError("reCAPTCHA validation failed")
                
            # Store the score for later use
            self.recaptcha_score = result.get('score', 0)
            
            # Track score in session
            if self.request:
                session_scores = self.request.session.get('recaptcha_scores', [])
                session_scores.append(str(self.recaptcha_score))
                self.request.session['recaptcha_scores'] = session_scores
            
            # Check the score
            if self.recaptcha_score < settings.RECAPTCHA_SCORE_THRESHOLD:
                logger.warning(f"reCAPTCHA score too low: {self.recaptcha_score} < {settings.RECAPTCHA_SCORE_THRESHOLD}")
                raise forms.ValidationError("reCAPTCHA score too low")
                
        except requests.RequestException as e:
            logger.error(f"reCAPTCHA verification error: {e}")
            raise forms.ValidationError("reCAPTCHA verification failed")
            
        return token
    
    def save(self, commit=True):
        """Save lead with campaign tracking and reCAPTCHA score"""
        lead = super().save(commit=False)
        
        # Build internal notes with tracking data
        notes_parts = []
        
        # Add reCAPTCHA scores from session
        if self.request and 'recaptcha_scores' in self.request.session:
            scores = self.request.session['recaptcha_scores']
            if len(scores) > 1:
                notes_parts.append(f"reCAPTCHA: {' | '.join(scores)}")
            else:
                notes_parts.append(f"reCAPTCHA: {scores[0]}")
            # Clear the session scores after successful submission
            del self.request.session['recaptcha_scores']
        
        # Add reCAPTCHA action
        recaptcha_action = self.cleaned_data.get('recaptcha_action')
        if recaptcha_action:
            notes_parts.append(f"reCAPTCHA Action: {recaptcha_action}")
        
        # Add source and referral data
        submission_source = self.cleaned_data.get('submission_source')
        if submission_source:
            notes_parts.append(f"Submitted from: {submission_source}")
        
        page_url = self.cleaned_data.get('page_url')
        if page_url:
            notes_parts.append(f"Page URL: {page_url}")
        
        referrer = self.cleaned_data.get('referrer')
        if referrer:
            notes_parts.append(f"Referrer: {referrer}")
        
        # Add campaign tracking data from form fields (more reliable than request.GET)
        campaign_data = []
        
        # Google Ads data
        gclid = self.cleaned_data.get('gclid')
        if gclid:
            campaign_data.append(f"GCLID: {gclid}")
        
        gad_campaignid = self.cleaned_data.get('gad_campaignid')
        if gad_campaignid:
            campaign_data.append(f"Campaign ID: {gad_campaignid}")
        
        # UTM parameters
        utm_params = []
        utm_source = self.cleaned_data.get('utm_source')
        if utm_source:
            utm_params.append(f"Source: {utm_source}")
        
        utm_medium = self.cleaned_data.get('utm_medium')
        if utm_medium:
            utm_params.append(f"Medium: {utm_medium}")
        
        utm_campaign = self.cleaned_data.get('utm_campaign')
        if utm_campaign:
            utm_params.append(f"Campaign: {utm_campaign}")
        
        utm_term = self.cleaned_data.get('utm_term')
        if utm_term:
            utm_params.append(f"Term: {utm_term}")
        
        utm_content = self.cleaned_data.get('utm_content')
        if utm_content:
            utm_params.append(f"Content: {utm_content}")
        
        if utm_params:
            campaign_data.extend(utm_params)
        
        if campaign_data:
            notes_parts.append("Campaign: " + ", ".join(campaign_data))
        
        # Add PostHog distinct ID if available
        posthog_distinct_id = self.cleaned_data.get('posthog_distinct_id')
        if posthog_distinct_id:
            notes_parts.append(f"PostHog ID: {posthog_distinct_id}")
        
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

# Legacy alias for backward compatibility
GoogleLandingForm = LeadForm 