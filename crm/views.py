from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    """Home page view for the Veralign CRM."""
    return render(request, 'crm/home.html', {
        'title': 'Veralign CRM',
        'welcome_message': 'Welcome to Veralign - Your AI-based CRM Tool'
    })

def dashboard(request):
    """Dashboard view for the CRM."""
    return render(request, 'crm/dashboard.html', {
        'title': 'Dashboard',
        'user_name': 'User'  # This would come from authentication in a real app
    })
