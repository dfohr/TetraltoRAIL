from django import forms
from .models import Lead

class LeadForm(forms.ModelForm):
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