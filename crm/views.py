from django.shortcuts import render

# Create your views here.
def home(request):
    """Home page view"""
    context = {'title': 'VerAlign CRM'}

    return render(request, 'crm/home.html', context)

def dashboard(request):
    """Dashboard view"""
    context = {'title': 'Dashboard'}

    return render(request, 'crm/dashboard.html', context)
