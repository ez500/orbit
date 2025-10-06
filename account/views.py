from django.shortcuts import render

# Create your views here.
def register(request):
    """Register view"""
    context = {'title': 'VerAlign CRM'}

    return render(request, 'account/register.html', context)

