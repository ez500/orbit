from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import FormView

from .forms import ContactForm


# Create your views here.
def home(request):
    """Home page view"""
    context = {'title': 'Home'}

    return render(request, 'home/home.html', context)


class ContactView(FormView):
    template_name = "home/contact.html"
    form_class = ContactForm

    def form_valid(self, form):
        # Calling custom send method
        form.send()
        return JsonResponse({"message": "Form sent!"})
