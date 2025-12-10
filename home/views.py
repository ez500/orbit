from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import FormView

from .forms import ContactForm


# Create your views here.
def home(request):
    """Home page view - redirects authenticated users to dashboard"""
    # If user is authenticated, redirect to dashboard
    if request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('dashboard:dashboard')

    context = {'title': 'Orbit - Intelligent CRM Platform'}
    return render(request, 'home/home.html', context)


class ContactView(FormView):
    template_name = "home/contact.html"
    form_class = ContactForm


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Contact Us'
        return context


    def form_valid(self, form):
        # Calling custom send method
        form.send()
        return JsonResponse({"message": "Form sent!"})
