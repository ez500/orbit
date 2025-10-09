from django.shortcuts import render

# Create your views here.
def home(request):
    """Home page view"""
    context = {'title': 'Home'}

    return render(request, 'home/home.html', context)

def dashboard(request):
    """Dashboard view"""
    context = {'title': 'Dashboard'}

    return render(request, 'home/dashboard.html', context)
