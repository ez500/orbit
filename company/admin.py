from django.contrib import admin

from company.models import CompanyMembership, Company

# Register your models here.

admin.site.register(Company)
admin.site.register(CompanyMembership)
