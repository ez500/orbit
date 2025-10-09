from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView

# Create your views here.
def register(request):
    """Register view"""
    context = {'title': 'VerAlign CRM'}

    return render(request, 'accounts/register.html', context)

def login(request):
    """Login view"""
    context = {'title': 'VerAlign CRM'}

    return render(request, 'account/login.html', context)

class RegisterView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = 'accounts/register.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = 'VerAlign CRM'
        return context

