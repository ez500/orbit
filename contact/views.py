from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import render

def contact_view(request):
    return render(request, "contact/contact.html")