from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, CreateView, UpdateView, ListView
from .models import Company, CompanyMembership
from .forms import CompanyRegistrationForm


def ensure_membership_roles():
    """Automatically fix any memberships with blank roles."""
    from .models import CompanyMembership
    bad_rows = CompanyMembership.objects.filter(role="")
    if bad_rows.exists():
        bad_rows.update(role="employee")

# -------------------------------------------------------
# Register a Company
# -------------------------------------------------------
class RegisterCompany(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyRegistrationForm
    template_name = "company/register.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        self.object = form.save()

        # Make the creator the owner
        CompanyMembership.objects.create(
            company=self.object, user=self.request.user, role="owner"
        )
        messages.success(self.request, f"Company '{self.object.name}' created successfully!")
        return redirect("company:company", name=self.object.name)


# -------------------------------------------------------
# View Company Profile
# -------------------------------------------------------
class CompanyView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = "company/profile.html"
    context_object_name = "company"
    slug_field = "name"
    slug_url_kwarg = "name"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.object
        user = self.request.user

        # Ensure owner always has a membership
        CompanyMembership.objects.get_or_create(
            company=company, user=company.owner, defaults={"role": "owner"}
        )

        memberships = CompanyMembership.objects.filter(company=company).select_related("user")
        viewer_membership = memberships.filter(user=user).first()

        if viewer_membership is None and user == company.owner:
            viewer_membership = CompanyMembership.objects.get(company=company, user=company.owner)

        context["memberships"] = memberships
        context["viewer_membership"] = viewer_membership
        return context


# -------------------------------------------------------
# Edit Company Info
# -------------------------------------------------------
class EditCompany(LoginRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyRegistrationForm
    template_name = "company/edit.html"
    slug_field = "name"
    slug_url_kwarg = "name"

    def form_valid(self, form):
        company = self.get_object()
        if self.request.user != company.owner:
            messages.error(self.request, "Only the owner can edit this company.")
            return redirect("company:company", name=company.name)

        messages.success(self.request, f"{company.name} updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return f"/company/{self.object.name}/"


# -------------------------------------------------------
# Join a Company
# -------------------------------------------------------
@login_required
def join_company(request, name):
    company = get_object_or_404(Company, name=name)
    existing = CompanyMembership.objects.filter(company=company, user=request.user).first()

    if existing:
        messages.warning(request, "You are already a member of this company.")
        return redirect("company:company", name=company.name)

    CompanyMembership.objects.create(company=company, user=request.user, role="employee")
    messages.success(request, f"You joined {company.name} as an employee.")
    return redirect("company:company", name=company.name)

class JoinCompanyListView(LoginRequiredMixin, ListView):
    """Show all companies that the user is not a member of."""
    model = Company
    template_name = "company/join_list.html"
    context_object_name = "companies"

    def get_queryset(self):
        # Show companies where the user is NOT already a member
        return Company.objects.exclude(memberships__user=self.request.user)

# -------------------------------------------------------
# Promote / Demote / Kick
# -------------------------------------------------------
@login_required
def promote_member(request, name, username):
    """Promote a member to the next higher role."""
    ensure_membership_roles()
    company = get_object_or_404(Company, name=name)
    target = get_object_or_404(CompanyMembership, company=company, user__username=username)
    viewer = get_object_or_404(CompanyMembership, company=company, user=request.user)

    hierarchy = ["employee", "mod", "admin", "owner"]
    if not viewer.role:
        viewer.role = "employee"
    if not target.role:
        target.role = "employee"
    # Only allow promotion by someone above in hierarchy
    if hierarchy.index(viewer.role) <= hierarchy.index(target.role):
        messages.error(request, "You don’t have permission to promote this user.")
        return redirect("company:company", name=company.name)

    current_index = hierarchy.index(target.role)
    if current_index < len(hierarchy) - 1:
        target.role = hierarchy[current_index + 1]
        target.save()
        messages.success(request, f"{target.user.username} has been promoted to {target.role.title()}.")
    else:
        messages.warning(request, "User is already at the highest role.")

    return redirect("company:company", name=company.name)


@login_required
def demote_member(request, name, username):
    """Demote a member to the next lower role."""
    ensure_membership_roles()
    company = get_object_or_404(Company, name=name)
    target = get_object_or_404(CompanyMembership, company=company, user__username=username)
    viewer = get_object_or_404(CompanyMembership, company=company, user=request.user)

    hierarchy = ["employee", "mod", "admin", "owner"]
    if not viewer.role:
        viewer.role = "employee"
    if not target.role:
        target.role = "employee"

    if hierarchy.index(viewer.role) <= hierarchy.index(target.role):
        messages.error(request, "You don’t have permission to demote this user.")
        return redirect("company:company", name=company.name)

    current_index = hierarchy.index(target.role)
    if current_index > 0:
        target.role = hierarchy[current_index - 1]
        target.save()
        messages.success(request, f"{target.user.username} has been demoted to {target.role.title()}.")
    else:
        messages.warning(request, "User is already at the lowest role.")

    return redirect("company:company", name=company.name)


@login_required
def kick_member(request, name, username):
    """Remove a member from the company."""
    ensure_membership_roles()
    company = get_object_or_404(Company, name=name)
    target = get_object_or_404(CompanyMembership, company=company, user__username=username)
    viewer = get_object_or_404(CompanyMembership, company=company, user=request.user)

    if viewer.role not in ["admin", "owner"]:
        messages.error(request, "You don’t have permission to kick members.")
        return redirect("company:company", name=company.name)

    if target.role == "owner":
        messages.error(request, "You cannot remove the owner.")
        return redirect("company:company", name=company.name)

    target.delete()
    messages.success(request, f"{target.user.username} has been removed from {company.name}.")

    return redirect("company:company", name=company.name)
