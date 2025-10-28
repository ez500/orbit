from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from company.models import Company


# Create your views here.

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
