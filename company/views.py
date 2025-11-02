from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, CreateView

from company.forms import CompanyRegistrationForm
from company.models import Company, CompanyMembership


# Create your views here.

class RegisterCompany(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyRegistrationForm
    template_name = 'company/register.html'
    extra_context = {'title': 'Register Company'}

    def form_valid(self, form):
        form.instance.owner = self.request.user
        self.object = form.save()
        CompanyMembership.objects.create(company=self.object, user=self.request.user)
        return redirect("company:company", name=self.object.name)


class CompanyView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'company/profile.html'
    context_object_name = 'company'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.get_object()

        context['title'] = f'{company}\'s Profile'
        context['members'] = company.members.all()
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(Company, name=self.kwargs['name'])
