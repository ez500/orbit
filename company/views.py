from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import DetailView, CreateView, UpdateView, ListView
from .models import Company, CompanyMembership, CompanyMembershipRequest
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
        context["can_manage_requests"] = viewer_membership and viewer_membership.role in ["admin", "owner"]
        context["already_requested"] = CompanyMembershipRequest.objects.filter(company=company, user=user).exists()
        context["requests"] = CompanyMembershipRequest.objects.filter(company=company)
        context["title"] = company.name + " - Company Profile"
        return context


class CreateAnnouncementView(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyRegistrationForm
    template_name = "company/create_announcement.html"
    slug_field = "name"
    slug_url_kwarg = "name"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Create Announcement - {self.object.name}"
        return context

    def form_valid(self, form):
        company = self.get_object()
        if self.request.user != company.owner:
            messages.error(self.request, "Only the owner can create announcements.")
            return redirect("company:company", name=company.name)

        messages.success(self.request, f"Announcement created successfully for {company.name}.")
        return super().form_valid(form)

    def get_success_url(self):
        return f"/company/{self.object.name}/"


# -------------------------------------------------------
# Edit Company Info
# -------------------------------------------------------
class EditCompany(LoginRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyRegistrationForm
    template_name = "company/edit.html"
    slug_field = "name"
    slug_url_kwarg = "name"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Edit {self.object.name} - Company Profile"
        return context

    def form_valid(self, form):
        company = self.get_object()
        if self.request.user != company.owner:
            messages.error(self.request, "Only the owner can edit this company.")
            return redirect("company:company", name=company.name)

        messages.success(self.request, f"{company.name} updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return f"/company/{self.object.name}/"


def _safe_redirect_back(request, fallback_url):
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect(fallback_url)


# -------------------------------------------------------
# Join a Company
# -------------------------------------------------------
@login_required
def send_join_request(request, name):
    if request.method == 'POST':
        company = get_object_or_404(Company, name=name)

        if company.memberships.filter(user=request.user).exists():
            messages.info(request, "You are already a member of this company.")
        else:
            CompanyMembershipRequest.objects.create(
                user=request.user,
                company=company
            )
            messages.success(request, f'Join request sent to {company.name}.')
    return _safe_redirect_back(request, fallback_url=reverse('company:company', args=[name]))


@login_required
def accept_join_request(request, name, username):
    if request.method == 'POST':
        company = get_object_or_404(Company, name=name)

        try:
            join_request = CompanyMembershipRequest.objects.get(company=company, user__username=username)
            join_request.delete()

            if company.memberships.filter(user__username=username).exists():
                messages.info(request, f"{username} is already a member of this company.")
            else:
                CompanyMembership.objects.create(company=company, user=join_request.user, role="employee")
                messages.success(request, f"{username} has been added to {company.name} as an employee.")
        except CompanyMembershipRequest.DoesNotExist:
            messages.error(request, f"No join request from {username} found.")
    return _safe_redirect_back(request, fallback_url=reverse('company:company', args=[name]))


@login_required
def decline_join_request(request, name, username):
    if request.method == 'POST':
        company = get_object_or_404(Company, name=name)

        try:
            join_request = CompanyMembershipRequest.objects.get(company=company, user__username=username)
            join_request.delete()

            if company.memberships.filter(user__username=username).exists():
                messages.info(request, f"{username} is already a member of this company.")
            else:
                messages.success(request, f"Join request from {username} has been declined.")
        except CompanyMembershipRequest.DoesNotExist:
            messages.error(request, f"No join request from {username} found.")
    return _safe_redirect_back(request, fallback_url=reverse('company:company', args=[name]))


@login_required
def leave_company(request, name):
    if request.method == 'POST':
        company = get_object_or_404(Company, name=name)
        membership = get_object_or_404(CompanyMembership, company=company, user=request.user)

        if membership.role == "owner":
            messages.error(request, "The owner cannot quit the company. Please transfer ownership first.")
        else:
            membership.delete()
            messages.success(request, f"You have left the company {company.name}.")
    return _safe_redirect_back(request, fallback_url=reverse('company:company', args=[name]))

class JoinCompanyListView(LoginRequiredMixin, ListView):
    """Show all companies that the user is not a member of."""
    model = Company
    template_name = "company/join_list.html"
    context_object_name = "companies"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["requested_companies"] = CompanyMembershipRequest.objects.filter(user=self.request.user).values_list('company__name', flat=True)
        context["title"] = "Join Company Profiles"

        return context


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
