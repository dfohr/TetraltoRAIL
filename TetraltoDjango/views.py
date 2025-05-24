from django.shortcuts import render, redirect
from core.forms import LeadForm

def contact(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('thank_you')
    else:
        form = LeadForm()
    return render(request, 'contact.html', {'form': form, 'email': 'sales@tetralto.com'})

def thank_you(request):
    return render(request, 'thank-you.html') 