from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    """Home page view"""
    context = {'title': 'Home'}

    return render(request, 'home/home.html', context)

@login_required
def dashboard(request):
    """Dashboard view"""
    
    context = {'title': 'Dashboard'}

    return render(request, 'home/dashboard.html', context)

@login_required
def tasks(request):
    """Tasks view"""
    
    context = {'title': 'Tasks'}

    return render(request, 'home/tasks.html', context)
