from django.shortcuts import render


# Create your views here.
def home(request):
    """Home page view"""
    context = {'title': 'Home'}

    return render(request, 'home/home.html', context)
